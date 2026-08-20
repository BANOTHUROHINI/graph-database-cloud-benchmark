from pathlib import Path


def test_dataset_files_exist():
    data_dir = Path("data")

    expected_files = [
        "cities.csv",
        "companies.csv",
        "knows.csv",
        "lives_in.csv",
        "persons.csv",
        "works_at.csv",
    ]

    for filename in expected_files:
        assert (data_dir / filename).exists(), f"Missing {filename}"


def test_result_files_exist():
    results_dir = Path("results")

    expected_files = [
        "benchmark_results.csv",
        "benchmark_raw.csv",
        "benchmark_comparison.csv",
        "analysis.md",
    ]

    for filename in expected_files:
        assert (results_dir / filename).exists(), f"Missing {filename}"
