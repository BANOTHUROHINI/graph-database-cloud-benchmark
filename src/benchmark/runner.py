import csv
import math
import statistics
import time
from pathlib import Path

from falkordb import FalkorDB
from neo4j import GraphDatabase

from queries import QUERIES, DEFAULT_PARAMS


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_DIR = Path("results")

SUMMARY_FILE = RESULTS_DIR / "benchmark_results.csv"
RAW_FILE = RESULTS_DIR / "benchmark_raw.csv"
COMPARISON_FILE = RESULTS_DIR / "benchmark_comparison.csv"

WARMUP_RUNS = 5
MEASURED_RUNS = 100

# Outlier threshold:
# A run is considered a high-latency outlier if it is above
# median + 3 * standard deviation.
OUTLIER_STD_MULTIPLIER = 3


# ============================================================
# STATISTICS
# ============================================================

def percentile(values, percentile_value):
    """
    Calculate percentile using linear interpolation.
    percentile_value should be between 0 and 1.
    """

    values = sorted(values)

    if not values:
        return 0.0

    position = (len(values) - 1) * percentile_value

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return values[lower]

    weight = position - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * weight
    )


def calculate_statistics(timings):
    """
    Calculate complete latency statistics.
    """

    mean = statistics.mean(timings)
    median = statistics.median(timings)

    if len(timings) > 1:
        stdev = statistics.stdev(timings)
    else:
        stdev = 0.0

    # Detect unusually slow executions.
    threshold = (
        median
        + OUTLIER_STD_MULTIPLIER * stdev
    )

    outliers = [
        value
        for value in timings
        if value > threshold
    ]

    return {
        "runs": len(timings),
        "min_ms": min(timings),
        "avg_ms": mean,
        "median_ms": median,
        "p90_ms": percentile(timings, 0.90),
        "p95_ms": percentile(timings, 0.95),
        "p99_ms": percentile(timings, 0.99),
        "max_ms": max(timings),
        "stdev_ms": stdev,
        "cv_percent": (
            (stdev / mean) * 100
            if mean != 0
            else 0.0
        ),
        "outlier_count": len(outliers),
    }


# ============================================================
# QUERY MEASUREMENT
# ============================================================

def measure_query(
    execute_query,
    query_name,
    database,
):
    """
    Warm up the database and then measure query latency.
    """

    # --------------------------------------------------------
    # Warm-up
    # --------------------------------------------------------

    for _ in range(WARMUP_RUNS):
        execute_query()

    timings = []

    # --------------------------------------------------------
    # Measured runs
    # --------------------------------------------------------

    for run_number in range(
        1,
        MEASURED_RUNS + 1,
    ):

        start = time.perf_counter()

        execute_query()

        elapsed_ms = (
            time.perf_counter()
            - start
        ) * 1000

        timings.append(elapsed_ms)

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    stats = calculate_statistics(timings)

    summary = {
        "database": database,
        "query": query_name,
        **stats,
    }

    # --------------------------------------------------------
    # Raw results
    # --------------------------------------------------------

    raw_results = []

    for run_number, timing in enumerate(
        timings,
        start=1,
    ):

        raw_results.append({
            "database": database,
            "query": query_name,
            "run": run_number,
            "latency_ms": timing,
        })

    return summary, raw_results


# ============================================================
# NEO4J
# ============================================================

def benchmark_neo4j():

    driver = GraphDatabase.driver(
        "bolt://localhost:7687",
        auth=(
            "neo4j",
            "benchmarkpassword",
        ),
    )

    driver.verify_connectivity()

    summaries = []
    raw_results = []

    try:

        with driver.session(
            database="neo4j"
        ) as session:

            for query_name, query in QUERIES.items():

                print(
                    f"  Neo4j -> {query_name}"
                )

                summary, raw = measure_query(
                    lambda: session.run(
                        query,
                        **DEFAULT_PARAMS,
                    ).consume(),
                    query_name,
                    "Neo4j",
                )

                summaries.append(summary)
                raw_results.extend(raw)

    finally:

        driver.close()

    return summaries, raw_results


# ============================================================
# MEMGRAPH
# ============================================================

def benchmark_memgraph():

    driver = GraphDatabase.driver(
        "bolt://localhost:7688",
    )

    driver.verify_connectivity()

    summaries = []
    raw_results = []

    try:

        with driver.session() as session:

            for query_name, query in QUERIES.items():

                print(
                    f"  Memgraph -> {query_name}"
                )

                summary, raw = measure_query(
                    lambda: session.run(
                        query,
                        **DEFAULT_PARAMS,
                    ).consume(),
                    query_name,
                    "Memgraph",
                )

                summaries.append(summary)
                raw_results.extend(raw)

    finally:

        driver.close()

    return summaries, raw_results


# ============================================================
# FALKORDB
# ============================================================

def benchmark_falkordb():

    db = FalkorDB(
        host="localhost",
        port=6379,
    )

    graph = db.select_graph(
        "benchmark"
    )

    summaries = []
    raw_results = []

    for query_name, query in QUERIES.items():

        print(
            f"  FalkorDB -> {query_name}"
        )

        summary, raw = measure_query(
            lambda: graph.query(
                query,
                params=DEFAULT_PARAMS,
            ),
            query_name,
            "FalkorDB",
        )

        summaries.append(summary)
        raw_results.extend(raw)

    return summaries, raw_results


# ============================================================
# SAVE SUMMARY
# ============================================================

def save_summary(results):

    RESULTS_DIR.mkdir(
        exist_ok=True
    )

    fieldnames = [
        "database",
        "query",
        "runs",
        "min_ms",
        "avg_ms",
        "median_ms",
        "p90_ms",
        "p95_ms",
        "p99_ms",
        "max_ms",
        "stdev_ms",
        "cv_percent",
        "outlier_count",
    ]

    with open(
        SUMMARY_FILE,
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


# ============================================================
# SAVE RAW RESULTS
# ============================================================

def save_raw(results):

    RESULTS_DIR.mkdir(
        exist_ok=True
    )

    fieldnames = [
        "database",
        "query",
        "run",
        "latency_ms",
    ]

    with open(
        RAW_FILE,
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)


# ============================================================
# SAVE DATABASE COMPARISON
# ============================================================

def save_comparison(results):

    RESULTS_DIR.mkdir(
        exist_ok=True
    )

    grouped = {}

    for result in results:

        query = result["query"]

        if query not in grouped:
            grouped[query] = {}

        grouped[query][
            result["database"]
        ] = result

    rows = []

    for query, databases in grouped.items():

        neo4j = databases.get("Neo4j")
        memgraph = databases.get("Memgraph")
        falkordb = databases.get("FalkorDB")

        # ----------------------------------------------------
        # Find fastest database using median latency
        # ----------------------------------------------------

        available = {
            database: result["median_ms"]
            for database, result in databases.items()
        }

        fastest_database = min(
            available,
            key=available.get,
        )

        fastest_median = available[
            fastest_database
        ]

        row = {
            "query": query,
            "fastest_database": fastest_database,
            "fastest_median_ms": fastest_median,
        }

        # ----------------------------------------------------
        # Median latency
        # ----------------------------------------------------

        for database, result in databases.items():

            prefix = database.lower()

            row[
                f"{prefix}_median_ms"
            ] = result["median_ms"]

            row[
                f"{prefix}_p95_ms"
            ] = result["p95_ms"]

            row[
                f"{prefix}_p99_ms"
            ] = result["p99_ms"]

        # ----------------------------------------------------
        # Speedup against Neo4j
        # ----------------------------------------------------

        if neo4j:

            neo4j_median = (
                neo4j["median_ms"]
            )

            if memgraph:

                row[
                    "memgraph_speedup_vs_neo4j"
                ] = (
                    neo4j_median
                    / memgraph["median_ms"]
                )

            if falkordb:

                row[
                    "falkordb_speedup_vs_neo4j"
                ] = (
                    neo4j_median
                    / falkordb["median_ms"]
                )

        rows.append(row)

    fieldnames = [
        "query",
        "fastest_database",
        "fastest_median_ms",

        "neo4j_median_ms",
        "neo4j_p95_ms",
        "neo4j_p99_ms",

        "memgraph_median_ms",
        "memgraph_p95_ms",
        "memgraph_p99_ms",

        "falkordb_median_ms",
        "falkordb_p95_ms",
        "falkordb_p99_ms",

        "memgraph_speedup_vs_neo4j",
        "falkordb_speedup_vs_neo4j",
    ]

    with open(
        COMPARISON_FILE,
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(results):

    print()
    print(
        "=" * 125
    )
    print(
        "BENCHMARK RESULTS"
    )
    print(
        "=" * 125
    )

    for result in results:

        print(
            f"{result['database']:10} | "
            f"{result['query']:22} | "
            f"median="
            f"{result['median_ms']:.3f} ms | "
            f"p95="
            f"{result['p95_ms']:.3f} ms | "
            f"p99="
            f"{result['p99_ms']:.3f} ms | "
            f"avg="
            f"{result['avg_ms']:.3f} ms | "
            f"max="
            f"{result['max_ms']:.3f} ms | "
            f"CV="
            f"{result['cv_percent']:.2f}% | "
            f"outliers="
            f"{result['outlier_count']}"
        )


# ============================================================
# PRINT WINNERS
# ============================================================

def print_winners(results):

    grouped = {}

    for result in results:

        query = result["query"]

        if query not in grouped:
            grouped[query] = []

        grouped[query].append(result)

    print()
    print(
        "=" * 80
    )
    print(
        "FASTEST DATABASE BY MEDIAN LATENCY"
    )
    print(
        "=" * 80
    )

    for query, database_results in grouped.items():

        winner = min(
            database_results,
            key=lambda result:
                result["median_ms"],
        )

        print(
            f"{query:25} -> "
            f"{winner['database']:10} "
            f"({winner['median_ms']:.3f} ms)"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "Starting benchmark..."
    )

    print(
        f"\nWarm-up runs: "
        f"{WARMUP_RUNS}"
    )

    print(
        f"Measured runs: "
        f"{MEASURED_RUNS}"
    )

    print()

    all_summaries = []
    all_raw_results = []

    # --------------------------------------------------------
    # Neo4j
    # --------------------------------------------------------

    print(
        "Benchmarking Neo4j..."
    )

    summaries, raw = benchmark_neo4j()

    all_summaries.extend(
        summaries
    )

    all_raw_results.extend(
        raw
    )

    # --------------------------------------------------------
    # Memgraph
    # --------------------------------------------------------

    print()
    print(
        "Benchmarking Memgraph..."
    )

    summaries, raw = benchmark_memgraph()

    all_summaries.extend(
        summaries
    )

    all_raw_results.extend(
        raw
    )

    # --------------------------------------------------------
    # FalkorDB
    # --------------------------------------------------------

    print()
    print(
        "Benchmarking FalkorDB..."
    )

    summaries, raw = benchmark_falkordb()

    all_summaries.extend(
        summaries
    )

    all_raw_results.extend(
        raw
    )

    # --------------------------------------------------------
    # Save files
    # --------------------------------------------------------

    save_summary(
        all_summaries
    )

    save_raw(
        all_raw_results
    )

    save_comparison(
        all_summaries
    )

    # --------------------------------------------------------
    # Print output
    # --------------------------------------------------------

    print()

    print(
        "Benchmark completed."
    )

    print()

    print(
        f"Summary: "
        f"{SUMMARY_FILE}"
    )

    print(
        f"Raw timings: "
        f"{RAW_FILE}"
    )

    print(
        f"Comparison: "
        f"{COMPARISON_FILE}"
    )

    print_results(
        all_summaries
    )

    print_winners(
        all_summaries
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()