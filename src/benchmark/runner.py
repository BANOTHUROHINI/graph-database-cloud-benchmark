import csv
import math
import os
import statistics
import time
from pathlib import Path

from dotenv import load_dotenv
from falkordb import FalkorDB
from neo4j import GraphDatabase

from queries import QUERIES, DEFAULT_PARAMS


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

RESULTS_DIR = Path("results")

SUMMARY_FILE = RESULTS_DIR / "benchmark_results.csv"
RAW_FILE = RESULTS_DIR / "benchmark_raw.csv"
COMPARISON_FILE = RESULTS_DIR / "benchmark_comparison.csv"

WARMUP_RUNS = 5
MEASURED_RUNS = 100

OUTLIER_STD_MULTIPLIER = 3


# ============================================================
# STATISTICS
# ============================================================

def percentile(values, percentile_value):
    """Calculate percentile using linear interpolation."""

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
    """Calculate latency statistics."""

    if not timings:
        return {
            "runs": 0,
            "min_ms": 0.0,
            "avg_ms": 0.0,
            "median_ms": 0.0,
            "p90_ms": 0.0,
            "p95_ms": 0.0,
            "p99_ms": 0.0,
            "max_ms": 0.0,
            "stdev_ms": 0.0,
            "cv_percent": 0.0,
            "outlier_count": 0,
        }

    mean = statistics.mean(timings)
    median = statistics.median(timings)

    stdev = (
        statistics.stdev(timings)
        if len(timings) > 1
        else 0.0
    )

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
            if mean
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
    Warm up the database and measure query latency.

    Five warm-up executions are discarded.
    One hundred executions are measured.
    """

    print(
        f"    {database} -> {query_name}"
    )

    # Warm-up
    for _ in range(WARMUP_RUNS):
        execute_query()

    timings = []

    # Measured executions
    for _ in range(MEASURED_RUNS):

        start = time.perf_counter()

        execute_query()

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        timings.append(elapsed_ms)

    stats = calculate_statistics(timings)

    summary = {
        "database": database,
        "query": query_name,
        **stats,
    }

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

                summary, raw = measure_query(
                    lambda q=query: session.run(
                        q,
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

                summary, raw = measure_query(
                    lambda q=query: session.run(
                        q,
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

    graph = db.select_graph("benchmark")

    summaries = []
    raw_results = []

    for query_name, query in QUERIES.items():

        summary, raw = measure_query(
            lambda q=query: graph.query(
                q,
                params=DEFAULT_PARAMS,
            ),
            query_name,
            "FalkorDB",
        )

        summaries.append(summary)
        raw_results.extend(raw)

    return summaries, raw_results


# ============================================================
# COGNODB
# ============================================================

def benchmark_cognodb():

    uri = os.getenv("COGNODB_URI")
    username = os.getenv(
        "COGNODB_USERNAME",
        "cognodb",
    )
    password = os.getenv(
        "COGNODB_PASSWORD"
    )

    if not uri:
        raise RuntimeError(
            "COGNODB_URI is not set in .env"
        )

    if not password:
        raise RuntimeError(
            "COGNODB_PASSWORD is not set in .env"
        )

    driver = GraphDatabase.driver(
        uri,
        auth=(
            username,
            password,
        ),
    )

    driver.verify_connectivity()

    summaries = []
    raw_results = []

    try:

        with driver.session() as session:

            for query_name, query in QUERIES.items():

                summary, raw = measure_query(
                    lambda q=query: session.run(
                        q,
                        **DEFAULT_PARAMS,
                    ).consume(),
                    query_name,
                    "CognoDB",
                )

                summaries.append(summary)
                raw_results.extend(raw)

    finally:
        driver.close()

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

        available = {
            database: result["median_ms"]
            for database, result in databases.items()
        }

        fastest_database = min(
            available,
            key=available.get,
        )

        row = {
            "query": query,
            "fastest_database": fastest_database,
            "fastest_median_ms": available[
                fastest_database
            ],
        }

        # ----------------------------------------------------
        # Every database
        # ----------------------------------------------------

        for database in [
            "Neo4j",
            "Memgraph",
            "FalkorDB",
            "CognoDB",
        ]:

            result = databases.get(database)

            prefix = database.lower()

            if result:

                row[
                    f"{prefix}_median_ms"
                ] = result["median_ms"]

                row[
                    f"{prefix}_p95_ms"
                ] = result["p95_ms"]

                row[
                    f"{prefix}_p99_ms"
                ] = result["p99_ms"]

            else:

                row[
                    f"{prefix}_median_ms"
                ] = ""

                row[
                    f"{prefix}_p95_ms"
                ] = ""

                row[
                    f"{prefix}_p99_ms"
                ] = ""

        # ----------------------------------------------------
        # Speedup against Neo4j
        # ----------------------------------------------------

        neo4j = databases.get("Neo4j")

        if neo4j:

            neo4j_median = neo4j[
                "median_ms"
            ]

            for database in [
                "Memgraph",
                "FalkorDB",
                "CognoDB",
            ]:

                result = databases.get(
                    database
                )

                prefix = database.lower()

                if result and result["median_ms"] > 0:

                    row[
                        f"{prefix}_speedup_vs_neo4j"
                    ] = (
                        neo4j_median
                        / result["median_ms"]
                    )

                else:

                    row[
                        f"{prefix}_speedup_vs_neo4j"
                    ] = ""

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

        "cognodb_median_ms",
        "cognodb_p95_ms",
        "cognodb_p99_ms",

        "memgraph_speedup_vs_neo4j",
        "falkordb_speedup_vs_neo4j",
        "cognodb_speedup_vs_neo4j",
    ]

    with open(
        COMPARISON_FILE,
        "w",
        newline="",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(rows)


# ============================================================
# PRINT RESULTS
# ============================================================

def print_results(results):

    print()
    print("=" * 125)
    print("BENCHMARK RESULTS")
    print("=" * 125)

    for result in results:

        print(
            f"{result['database']:10} | "
            f"{result['query']:22} | "
            f"median={result['median_ms']:.3f} ms | "
            f"p95={result['p95_ms']:.3f} ms | "
            f"p99={result['p99_ms']:.3f} ms | "
            f"avg={result['avg_ms']:.3f} ms | "
            f"max={result['max_ms']:.3f} ms | "
            f"CV={result['cv_percent']:.2f}% | "
            f"outliers={result['outlier_count']}"
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
    print("=" * 80)
    print("FASTEST DATABASE BY MEDIAN LATENCY")
    print("=" * 80)

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

    print("=" * 80)
    print("GRAPH DATABASE CLOUD BENCHMARK")
    print("=" * 80)

    print(
        f"Warm-up runs: {WARMUP_RUNS}"
    )

    print(
        f"Measured runs: {MEASURED_RUNS}"
    )

    print()

    all_summaries = []
    all_raw_results = []

    # --------------------------------------------------------
    # Neo4j
    # --------------------------------------------------------

    print("Benchmarking Neo4j...")

    summaries, raw = benchmark_neo4j()

    all_summaries.extend(summaries)
    all_raw_results.extend(raw)

    # --------------------------------------------------------
    # Memgraph
    # --------------------------------------------------------

    print()
    print("Benchmarking Memgraph...")

    summaries, raw = benchmark_memgraph()

    all_summaries.extend(summaries)
    all_raw_results.extend(raw)

    # --------------------------------------------------------
    # FalkorDB
    # --------------------------------------------------------

    print()
    print("Benchmarking FalkorDB...")

    summaries, raw = benchmark_falkordb()

    all_summaries.extend(summaries)
    all_raw_results.extend(raw)

    # --------------------------------------------------------
    # CognoDB
    # --------------------------------------------------------

    print()
    print("Benchmarking CognoDB...")

    summaries, raw = benchmark_cognodb()

    all_summaries.extend(summaries)
    all_raw_results.extend(raw)

    # --------------------------------------------------------
    # Save results
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
    # Print results
    # --------------------------------------------------------

    print()
    print("Benchmark completed.")

    print(
        f"Summary: {SUMMARY_FILE}"
    )

    print(
        f"Raw timings: {RAW_FILE}"
    )

    print(
        f"Comparison: {COMPARISON_FILE}"
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