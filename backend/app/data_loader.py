"""Load Stage 2 portfolio inputs from the UCI stock portfolio dataset.

The UCI file is not a date/symbol/close price table. Each ID is treated as a
candidate stock-selection weighting strategy, and PSO optimizes allocations
across those candidate strategies.
"""

from __future__ import annotations

from pathlib import Path
import re

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_DIR = PROJECT_ROOT / "data" / "raw"
CANONICAL_FILENAME = "uci_stock_portfolio_performance.xlsx"
LOCAL_UCI_FILENAME = "stock portfolio performance data set.xlsx"
PERIOD_SHEETS = ("1st period", "2nd period", "3rd period", "4th period")
ALL_PERIOD_SHEET = "all period"


def load_portfolio_dataset(raw_dir=None, random_seed=42):
    """Return expected returns and covariance matrix for the PSO prototype."""
    raw_path = Path(raw_dir) if raw_dir is not None else DEFAULT_RAW_DIR
    data_path = _resolve_uci_path(raw_path)
    if data_path is None:
        return get_fallback_simulated_dataset(
            random_seed=random_seed,
            source_notes=(
                "Stage 2 simulated fallback is used because no UCI Excel file "
                "was found. This is not real UCI data."
            ),
        )

    try:
        dataset = _load_uci_dataset(data_path)
        validate_portfolio_inputs(
            dataset["asset_names"],
            dataset["expected_returns"],
            dataset["covariance_matrix"],
        )
        return dataset
    except Exception as exc:
        return get_fallback_simulated_dataset(
            random_seed=random_seed,
            source_notes=(
                "Stage 2 simulated fallback is used because UCI parsing failed: "
                f"{exc}. This is not real UCI data."
            ),
        )


def validate_portfolio_inputs(asset_names, expected_returns, covariance_matrix):
    asset_count = len(asset_names)
    if asset_count < 2:
        raise ValueError("asset_names must contain at least two assets")

    returns = np.asarray(expected_returns, dtype=float)
    covariance = np.asarray(covariance_matrix, dtype=float)

    if returns.ndim != 1:
        raise ValueError("expected_returns must be a one-dimensional vector")
    if returns.shape != (asset_count,):
        raise ValueError("expected_returns length must match asset_names")
    if covariance.shape != (asset_count, asset_count):
        raise ValueError("covariance_matrix must be an N x N matrix")
    if not np.all(np.isfinite(returns)):
        raise ValueError("expected_returns must not contain NaN or inf")
    if not np.all(np.isfinite(covariance)):
        raise ValueError("covariance_matrix must not contain NaN or inf")
    if np.any(np.diag(covariance) < 0):
        raise ValueError("covariance_matrix diagonal cannot be negative")


def get_fallback_simulated_dataset(
    asset_count=10,
    random_seed=42,
    source_notes=(
        "Stage 2 simulated fallback dataset. This is not real UCI data and "
        "must not be reported as a real-data experiment."
    ),
):
    rng = np.random.default_rng(random_seed)
    expected_returns = rng.uniform(0.04, 0.18, size=asset_count)
    factor_loadings = rng.normal(size=(asset_count, asset_count))
    covariance_matrix = (factor_loadings @ factor_loadings.T) / asset_count
    covariance_matrix = covariance_matrix * 0.01
    covariance_matrix += np.eye(asset_count) * 0.015

    dataset = {
        "data_source": "simulated_fallback",
        "asset_names": [f"Strategy_{index}" for index in range(1, asset_count + 1)],
        "expected_returns": expected_returns,
        "covariance_matrix": covariance_matrix,
        "annualized": True,
        "trading_days_per_year": None,
        "source_notes": source_notes,
    }
    validate_portfolio_inputs(
        dataset["asset_names"],
        dataset["expected_returns"],
        dataset["covariance_matrix"],
    )
    return dataset


def _resolve_uci_path(raw_dir):
    canonical_path = raw_dir / CANONICAL_FILENAME
    if canonical_path.exists():
        return canonical_path

    local_path = raw_dir / LOCAL_UCI_FILENAME
    if local_path.exists():
        return local_path

    return None


def _load_uci_dataset(data_path):
    period_tables = {
        sheet_name: _parse_period_sheet(data_path, sheet_name)
        for sheet_name in (*PERIOD_SHEETS, ALL_PERIOD_SHEET)
    }
    period_returns = _period_metric_table(period_tables, "Annual Return")

    expected_returns, expected_ids, expected_note = _expected_returns_from_uci(
        period_tables,
        period_returns,
    )
    covariance_matrix, covariance_ids, covariance_note = _covariance_from_period_returns(
        period_returns,
    )

    common_ids = [strategy_id for strategy_id in expected_ids if strategy_id in covariance_ids]
    if len(common_ids) < 2:
        covariance_matrix, covariance_ids, covariance_note = _covariance_from_total_risk(
            period_tables,
        )
        common_ids = [strategy_id for strategy_id in expected_ids if strategy_id in covariance_ids]
    if len(common_ids) < 2:
        raise ValueError("UCI data did not yield at least two aligned strategies")

    expected_index = {strategy_id: index for index, strategy_id in enumerate(expected_ids)}
    covariance_index = {strategy_id: index for index, strategy_id in enumerate(covariance_ids)}
    expected_positions = [expected_index[strategy_id] for strategy_id in common_ids]
    covariance_positions = [covariance_index[strategy_id] for strategy_id in common_ids]

    aligned_expected_returns = expected_returns[expected_positions]
    aligned_covariance = covariance_matrix[np.ix_(covariance_positions, covariance_positions)]
    asset_names = [f"Strategy_{strategy_id}" for strategy_id in common_ids]

    source_notes = (
        "UCI Stock Portfolio Performance is not raw date/symbol/close price data; "
        "each ID is treated as one candidate stock-selection weighting strategy. "
        "PSO optimizes allocation weights across these strategies. "
        f"{expected_note} {covariance_note} "
        "Annual Return is already a performance indicator, so no 252-trading-day "
        "annualization is applied."
    )

    return {
        "data_source": "uci",
        "asset_names": asset_names,
        "expected_returns": aligned_expected_returns,
        "covariance_matrix": aligned_covariance,
        "annualized": True,
        "trading_days_per_year": None,
        "source_notes": source_notes,
    }


def _parse_period_sheet(data_path, sheet_name):
    raw = pd.read_excel(data_path, sheet_name=sheet_name, header=None, engine="openpyxl")
    if raw.shape[0] < 3:
        raise ValueError(f"{sheet_name} does not contain enough rows")

    group_row = raw.iloc[0].ffill()
    field_row = raw.iloc[1]
    columns = [_build_column_name(group_row.iloc[index], field_row.iloc[index]) for index in raw.columns]

    table = raw.iloc[2:].copy()
    table.columns = columns
    table = table.dropna(how="all")
    id_column = _find_id_column(table)
    table[id_column] = pd.to_numeric(table[id_column], errors="coerce")
    table = table.dropna(subset=[id_column])
    table[id_column] = table[id_column].astype(int)
    return table


def _build_column_name(group_name, field_name):
    field = str(field_name).strip()
    group = "" if pd.isna(group_name) else str(group_name).strip().lower()

    if _normalize_token(field) == "id":
        return "ID"
    if "original investment performance" in group:
        return f"original_{field}"
    if "normalized" in group and "performance" in group:
        return f"normalized_{field}"
    if "stock-picking concept" in group:
        return f"concept_{field}"
    return field


def _find_id_column(table):
    for column in table.columns:
        if _normalize_token(column) == "id":
            return column
    raise ValueError("ID column was not found")


def _find_metric_column(table, metric_name, preferred_prefix="original_"):
    metric_token = _normalize_token(metric_name)
    preferred_matches = [
        column
        for column in table.columns
        if str(column).startswith(preferred_prefix)
        and metric_token in _normalize_token(column)
    ]
    if preferred_matches:
        return preferred_matches[0]

    matches = [
        column
        for column in table.columns
        if metric_token in _normalize_token(column)
    ]
    if matches:
        return matches[0]

    raise ValueError(f"{metric_name} column was not found")


def _numeric_metric_by_id(table, metric_name):
    id_column = _find_id_column(table)
    metric_column = _find_metric_column(table, metric_name)
    values = pd.to_numeric(table[metric_column], errors="coerce")
    series = pd.Series(values.to_numpy(dtype=float), index=table[id_column].astype(int))
    series = series.replace([np.inf, -np.inf], np.nan).dropna()
    if series.shape[0] < 2:
        raise ValueError(f"{metric_name} did not produce at least two numeric rows")
    return series.sort_index(), str(metric_column)


def _period_metric_table(period_tables, metric_name):
    series_by_period = {}
    for sheet_name in PERIOD_SHEETS:
        series, _ = _numeric_metric_by_id(period_tables[sheet_name], metric_name)
        series_by_period[sheet_name] = series
    table = pd.DataFrame(series_by_period).dropna(how="any")
    if table.shape[0] < 2:
        raise ValueError(f"{metric_name} period table has fewer than two strategies")
    return table


def _expected_returns_from_uci(period_tables, period_returns):
    try:
        annual_return, field_name = _numeric_metric_by_id(
            period_tables[ALL_PERIOD_SHEET],
            "Annual Return",
        )
        note = f"expected_returns come from sheet '{ALL_PERIOD_SHEET}', field '{field_name}'."
        return annual_return.to_numpy(dtype=float), annual_return.index.to_list(), note
    except Exception:
        expected = period_returns.mean(axis=1)
        note = (
            "expected_returns come from the mean of original Annual Return across "
            "1st/2nd/3rd/4th period sheets."
        )
        return expected.to_numpy(dtype=float), expected.index.to_list(), note


def _covariance_from_period_returns(period_returns):
    returns_matrix = period_returns.T.to_numpy(dtype=float)
    covariance_matrix = np.cov(returns_matrix, rowvar=False)
    if covariance_matrix.shape != (period_returns.shape[0], period_returns.shape[0]):
        raise ValueError("period-level covariance matrix has invalid shape")

    note = (
        "covariance_matrix is estimated from period-level original Annual Return "
        "observations across the 1st/2nd/3rd/4th period sheets."
    )
    return covariance_matrix, period_returns.index.to_list(), note


def _covariance_from_total_risk(period_tables):
    total_risk, field_name = _numeric_metric_by_id(
        period_tables[ALL_PERIOD_SHEET],
        "Total Risk",
    )
    covariance_matrix = np.diag(total_risk.to_numpy(dtype=float) ** 2)
    note = (
        f"diagonal covariance fallback uses sheet '{ALL_PERIOD_SHEET}', field "
        f"'{field_name}'; cross-strategy correlations are not estimated."
    )
    return covariance_matrix, total_risk.index.to_list(), note


def _normalize_token(value):
    return re.sub(r"[^a-z0-9]+", "", str(value).lower())
