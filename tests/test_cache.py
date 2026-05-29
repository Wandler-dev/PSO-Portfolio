import subprocess

import numpy as np

import backend.app.cache as cache
from backend.app.presets import DEMO_PRESETS, list_presets
from backend.app.schemas import OptimizeRequest


def sample_dataset():
    return {
        "data_source": "uci",
        "asset_names": ["Strategy_1", "Strategy_2", "Strategy_3"],
        "expected_returns": np.array([0.10, 0.14, 0.08]),
        "covariance_matrix": np.eye(3),
        "annualized": True,
        "trading_days_per_year": None,
        "source_notes": "test dataset",
    }


def test_same_request_builds_same_cache_key():
    dataset = sample_dataset()
    request = OptimizeRequest(particles=20, iterations=50, monte_carlo_samples=2000)

    first_key = cache.build_cache_key(dataset, request)
    second_key = cache.build_cache_key(dataset, request)

    assert first_key == second_key


def test_different_parameters_build_different_cache_keys():
    dataset = sample_dataset()
    first = OptimizeRequest(particles=20, iterations=50, monte_carlo_samples=2000)
    second = OptimizeRequest(particles=21, iterations=50, monte_carlo_samples=2000)

    assert cache.build_cache_key(dataset, first) != cache.build_cache_key(dataset, second)


def test_memory_cache_round_trip(tmp_path, monkeypatch):
    cache_path = tmp_path / "optimization_cache.json"
    monkeypatch.setattr(cache, "DEFAULT_CACHE_PATH", cache_path)
    cache.clear_memory_cache()

    cache.set_cached_response("cache-key", {"cache_hit": False, "value": 1})

    assert cache.cache_size() == 1
    assert cache.get_cached_response("cache-key") == {"cache_hit": False, "value": 1}


def test_file_cache_round_trip(tmp_path, monkeypatch):
    cache_path = tmp_path / "optimization_cache.json"
    monkeypatch.setattr(cache, "DEFAULT_CACHE_PATH", cache_path)
    cache.clear_memory_cache()

    cache.set_cached_response("cache-key", {"cache_hit": False, "value": 2})
    cache.clear_memory_cache()

    assert cache.get_cached_response("cache-key") == {"cache_hit": False, "value": 2}


def test_damaged_file_cache_is_ignored(tmp_path, monkeypatch):
    cache_path = tmp_path / "optimization_cache.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(cache, "DEFAULT_CACHE_PATH", cache_path)
    cache.clear_memory_cache()

    assert cache.load_file_cache() == {}
    assert cache.get_cached_response("missing") is None


def test_demo_presets_are_defined_in_one_place():
    assert set(DEMO_PRESETS) == {"conservative", "balanced", "aggressive"}
    preset_names = {preset["preset_name"] for preset in list_presets()}
    assert preset_names == set(DEMO_PRESETS)


def test_data_cache_files_are_not_tracked_by_git():
    result = subprocess.run(
        ["git", "ls-files", "data/cache"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == ""
