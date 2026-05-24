"""Profile the expected UCI stock portfolio Excel dataset.

This script is intentionally read-only for data/raw. It profiles only the
frozen target path used by stage 2A and writes a Markdown report for review.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

import pandas as pd

try:
    import openpyxl
except ImportError as exc:  # pragma: no cover - exercised by local environment
    raise SystemExit(
        "openpyxl is required to read .xlsx files. "
        "Install it in the portfolio-pso conda environment, for example: "
        "mamba install -n portfolio-pso -c conda-forge openpyxl"
    ) from exc


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CANONICAL_DATA_PATH = RAW_DIR / "uci_stock_portfolio_performance.xlsx"
LOCAL_DATA_PATH = RAW_DIR / "stock portfolio performance data set.xlsx"
REPORT_PATH = PROJECT_ROOT / "docs" / "uci_dataset_profile.md"


def _markdown_list(values: Iterable[object]) -> str:
    items = list(values)
    if not items:
        return "- none"
    return "\n".join(f"- `{item}`" for item in items)


def _series_table(title: str, values: pd.Series) -> str:
    lines = [f"### {title}", "", "| column | value |", "| --- | --- |"]
    for column, value in values.items():
        lines.append(f"| `{column}` | `{value}` |")
    return "\n".join(lines)


def _preview_block(df: pd.DataFrame) -> str:
    if df.empty:
        return "```text\n<empty sheet>\n```"
    preview = df.head(5).to_string(index=False)
    return f"```text\n{preview}\n```"


def _columns_with_percent_strings(df: pd.DataFrame) -> list[str]:
    result: list[str] = []
    for column in df.columns:
        values = df[column].dropna()
        if values.map(lambda value: isinstance(value, str) and "%" in value).any():
            result.append(str(column))
    return result


def _non_numeric_columns(df: pd.DataFrame) -> list[str]:
    return [
        str(column)
        for column in df.columns
        if not pd.api.types.is_numeric_dtype(df[column])
    ]


def _numeric_columns(df: pd.DataFrame) -> list[str]:
    return [
        str(column)
        for column in df.columns
        if pd.api.types.is_numeric_dtype(df[column])
    ]


def _suitability_judgment(sheet_profiles: list[dict[str, object]]) -> str:
    lines = [
        "## expected_returns / covariance_matrix 初步判断",
        "",
    ]
    if not sheet_profiles:
        lines.append("- 未读取到 sheet，无法判断是否适合计算。")
        return "\n".join(lines)

    direct_candidates = [
        profile
        for profile in sheet_profiles
        if profile["rows"] >= 2
        and len(profile["numeric_columns"]) >= 2
        and not profile["percent_columns"]
        and not profile["non_numeric_columns"]
    ]
    numeric_candidates = [
        profile
        for profile in sheet_profiles
        if profile["rows"] >= 2 and len(profile["numeric_columns"]) >= 2
    ]

    if direct_candidates:
        sheet_names = ", ".join(str(profile["sheet_name"]) for profile in direct_candidates)
        lines.append(
            "- 初步判断：存在全部字段为数值型且维度满足要求的 sheet，"
            f"可能可直接用于计算 `expected_returns` 和 `covariance_matrix`：{sheet_names}。"
        )
        lines.append("- 但仍需在下一阶段确认每行是否代表时间样本、每列是否代表资产价格或收益率。")
    elif numeric_candidates:
        sheet_names = ", ".join(str(profile["sheet_name"]) for profile in numeric_candidates)
        lines.append(
            "- 初步判断：不建议直接对整个数据集计算 `expected_returns` / `covariance_matrix`。"
        )
        lines.append(
            f"- 原因：以下 sheet 虽有足够数值列，但仍包含非数值字段或需进一步确认字段含义：{sheet_names}。"
        )
        lines.append("- 后续 `data_loader.py` 应先识别时间字段、资产字段、价格或收益率字段，再生成标准收益率矩阵。")
    else:
        lines.append(
            "- 初步判断：当前 sheet 未呈现可直接计算协方差矩阵的宽表数值结构。"
        )
        lines.append("- 后续需要先完成字段解释、数值转换和表结构整理。")

    percent_sheets = [
        str(profile["sheet_name"])
        for profile in sheet_profiles
        if profile["percent_columns"]
    ]
    if percent_sheets:
        lines.append(f"- 注意：{', '.join(percent_sheets)} 存在带 `%` 的字符串，计算前必须转换为数值比例。")

    non_numeric_sheets = [
        str(profile["sheet_name"])
        for profile in sheet_profiles
        if profile["non_numeric_columns"]
    ]
    if non_numeric_sheets:
        lines.append(
            f"- 注意：{', '.join(non_numeric_sheets)} 存在非数值字段，计算前必须明确保留或剔除规则。"
        )

    return "\n".join(lines)


def _raw_files() -> list[str]:
    if not RAW_DIR.exists():
        return []
    return sorted(path.name for path in RAW_DIR.iterdir() if path.is_file())


def _resolve_data_path() -> Path:
    if CANONICAL_DATA_PATH.exists():
        return CANONICAL_DATA_PATH
    return LOCAL_DATA_PATH


def _write_missing_report() -> None:
    report = [
        "# UCI 数据集画像",
        "",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 规范目标文件：`{CANONICAL_DATA_PATH.relative_to(PROJECT_ROOT)}`",
        f"- 本地确认文件：`{LOCAL_DATA_PATH.relative_to(PROJECT_ROOT)}`",
        "- 文件状态：未找到目标文件",
        f"- openpyxl：可用，版本 `{openpyxl.__version__}`",
        "",
        "## data/raw 已发现文件",
        "",
        _markdown_list(_raw_files()),
        "",
        "## 画像结果",
        "",
        "未读取 Excel sheet。阶段二 A 要求检查的目标路径不存在，脚本未对其他 raw 文件做替代读取。",
    ]
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")


def _profile_workbook() -> list[str]:
    data_path = _resolve_data_path()
    excel_file = pd.ExcelFile(data_path, engine="openpyxl")
    report: list[str] = [
        "# UCI 数据集画像",
        "",
        f"- 生成时间：{datetime.now().isoformat(timespec='seconds')}",
        f"- 规范目标文件：`{CANONICAL_DATA_PATH.relative_to(PROJECT_ROOT)}`",
        f"- 实际读取文件：`{data_path.relative_to(PROJECT_ROOT)}`",
        "- 文件状态：已找到",
        f"- openpyxl：可用，版本 `{openpyxl.__version__}`",
        f"- sheet 数量：{len(excel_file.sheet_names)}",
        "",
        "## Sheet 列表",
        "",
        _markdown_list(excel_file.sheet_names),
    ]

    summaries: list[str] = []
    sheet_profiles: list[dict[str, object]] = []
    sheet_sections: list[str] = []
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        rows, columns = df.shape
        percent_columns = _columns_with_percent_strings(df)
        non_numeric_columns = _non_numeric_columns(df)
        numeric_columns = _numeric_columns(df)

        summaries.append(f"- {sheet_name}: {rows} rows x {columns} columns")
        sheet_profiles.append(
            {
                "sheet_name": sheet_name,
                "rows": rows,
                "columns": columns,
                "numeric_columns": numeric_columns,
                "percent_columns": percent_columns,
                "non_numeric_columns": non_numeric_columns,
            }
        )

        sheet_sections.extend(
            [
                "",
                f"## Sheet: {sheet_name}",
                "",
                f"- 行数：{rows}",
                f"- 列数：{columns}",
                "- 列名：",
                _markdown_list(df.columns),
                "",
                _series_table("每列 dtype", df.dtypes.astype(str)),
                "",
                _series_table("每列缺失值数量", df.isna().sum()),
                "",
                "### 前 5 行样例",
                "",
                _preview_block(df),
                "",
                "### 带 % 的字符串",
                "",
                f"- 是否出现：{'是' if percent_columns else '否'}",
                "- 出现列：",
                _markdown_list(percent_columns),
                "",
                "### 非数值字段",
                "",
                f"- 是否存在：{'是' if non_numeric_columns else '否'}",
                "- 字段：",
                _markdown_list(non_numeric_columns),
            ]
        )

    report.extend(["", _suitability_judgment(sheet_profiles)])
    report.extend(sheet_sections)
    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")
    return summaries


def main() -> int:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    data_path = _resolve_data_path()

    if not data_path.exists():
        _write_missing_report()
        print(f"canonical_target_file={CANONICAL_DATA_PATH.relative_to(PROJECT_ROOT)}")
        print(f"local_confirmed_file={LOCAL_DATA_PATH.relative_to(PROJECT_ROOT)}")
        print("found=false")
        print(f"openpyxl_version={openpyxl.__version__}")
        print("raw_files=" + ", ".join(_raw_files()))
        print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
        return 0

    summaries = _profile_workbook()
    print(f"canonical_target_file={CANONICAL_DATA_PATH.relative_to(PROJECT_ROOT)}")
    print(f"actual_file={data_path.relative_to(PROJECT_ROOT)}")
    print("found=true")
    print(f"openpyxl_version={openpyxl.__version__}")
    print("sheets_profiled:")
    for summary in summaries:
        print(summary)
    print(f"report={REPORT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
