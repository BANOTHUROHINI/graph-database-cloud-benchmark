import csv
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path("results")
CHARTS_DIR = RESULTS_DIR / "charts"

RESULTS_FILE = RESULTS_DIR / "benchmark_results.csv"
COMPARISON_FILE = RESULTS_DIR / "benchmark_comparison.csv"
ANALYSIS_FILE = RESULTS_DIR / "analysis.md"


DATABASES = ["Neo4j", "Memgraph", "FalkorDB"]


def load_csv(path):
    with open(path, newline="") as file:
        return list(csv.DictReader(file))


def get_row(results, database, query):
    for row in results:
        if row["database"] == database and row["query"] == query:
            return row

    raise ValueError(
        f"Missing result for database={database}, query={query}"
    )


def average(values):
    if not values:
        return 0.0

    return sum(values) / len(values)


def create_median_chart(results):
    queries = sorted(set(row["query"] for row in results))

    x = list(range(len(queries)))
    width = 0.25

    plt.figure(figsize=(12, 6))

    for index, database in enumerate(DATABASES):
        values = []

        for query in queries:
            row = get_row(results, database, query)
            values.append(float(row["median_ms"]))

        positions = [
            value + (index - 1) * width
            for value in x
        ]

        plt.bar(
            positions,
            values,
            width=width,
            label=database,
        )

    plt.xticks(
        x,
        queries,
        rotation=30,
        ha="right",
    )

    plt.ylabel("Median Latency (ms)")
    plt.title("Median Query Latency Comparison")
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        CHARTS_DIR / "median_latency.png",
        dpi=200,
    )

    plt.close()


def create_p95_chart(results):
    queries = sorted(set(row["query"] for row in results))

    x = list(range(len(queries)))
    width = 0.25

    plt.figure(figsize=(12, 6))

    for index, database in enumerate(DATABASES):
        values = []

        for query in queries:
            row = get_row(results, database, query)
            values.append(float(row["p95_ms"]))

        positions = [
            value + (index - 1) * width
            for value in x
        ]

        plt.bar(
            positions,
            values,
            width=width,
            label=database,
        )

    plt.xticks(
        x,
        queries,
        rotation=30,
        ha="right",
    )

    plt.ylabel("P95 Latency (ms)")
    plt.title("P95 Query Latency Comparison")
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        CHARTS_DIR / "p95_latency.png",
        dpi=200,
    )

    plt.close()


def create_p99_chart(results):
    queries = sorted(set(row["query"] for row in results))

    x = list(range(len(queries)))
    width = 0.25

    plt.figure(figsize=(12, 6))

    for index, database in enumerate(DATABASES):
        values = []

        for query in queries:
            row = get_row(results, database, query)
            values.append(float(row["p99_ms"]))

        positions = [
            value + (index - 1) * width
            for value in x
        ]

        plt.bar(
            positions,
            values,
            width=width,
            label=database,
        )

    plt.xticks(
        x,
        queries,
        rotation=30,
        ha="right",
    )

    plt.ylabel("P99 Latency (ms)")
    plt.title("P99 Query Latency Comparison")
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        CHARTS_DIR / "p99_latency.png",
        dpi=200,
    )

    plt.close()


def create_stability_chart(results):
    cv_values = []

    for database in DATABASES:
        values = [
            float(row["cv_percent"])
            for row in results
            if row["database"] == database
        ]

        cv_values.append(average(values))

    plt.figure(figsize=(8, 5))

    plt.bar(
        DATABASES,
        cv_values,
    )

    plt.ylabel("Average CV (%)")
    plt.title("Latency Variability by Database")

    plt.tight_layout()

    plt.savefig(
        CHARTS_DIR / "latency_variability.png",
        dpi=200,
    )

    plt.close()


def calculate_fastest_counts(comparison):
    counts = {
        database: 0
        for database in DATABASES
    }

    for row in comparison:
        database = row["fastest_database"]

        if database not in counts:
            counts[database] = 0

        counts[database] += 1

    return counts


def calculate_average_medians(results):
    averages = {}

    for database in DATABASES:
        values = [
            float(row["median_ms"])
            for row in results
            if row["database"] == database
        ]

        averages[database] = average(values)

    return averages


def create_query_findings(comparison):
    lines = []

    for row in comparison:
        query = row["query"]
        fastest = row["fastest_database"]
        fastest_median = float(row["fastest_median_ms"])

        lines.append(
            f"### {query.replace('_', ' ').title()}\n\n"
            f"**{fastest}** was fastest with a median latency "
            f"of **{fastest_median:.3f} ms**.\n"
        )

        for database in DATABASES:
            median_key = f"{database.lower()}_median_ms"

            if median_key in row:
                median = float(row[median_key])

                lines.append(
                    f"- {database}: {median:.3f} ms median\n"
                )

        lines.append("")

    return "\n".join(lines)


def create_tail_analysis(results):
    lines = [
        "## 5. Latency Stability",
        "",
        "Tail latency is evaluated using P95 and P99 rather than "
        "median latency alone.",
        "",
    ]

    for database in DATABASES:
        rows = [
            row
            for row in results
            if row["database"] == database
        ]

        p99_values = [
            (row["query"], float(row["p99_ms"]))
            for row in rows
        ]

        highest_query, highest_p99 = max(
            p99_values,
            key=lambda item: item[1],
        )

        cv_values = [
            float(row["cv_percent"])
            for row in rows
        ]

        avg_cv = average(cv_values)

        lines.append(
            f"### {database}\n\n"
            f"- Average CV: **{avg_cv:.2f}%**\n"
            f"- Highest P99: **{highest_p99:.3f} ms** "
            f"for `{highest_query}`\n"
        )

    lines.append(
        "The database with the lowest average CV has the most "
        "stable latency across the tested queries. A high P99 "
        "relative to the median indicates occasional latency spikes."
    )

    return "\n".join(lines)


def create_analysis(results, comparison):
    fastest_counts = calculate_fastest_counts(comparison)
    average_medians = calculate_average_medians(results)

    total_queries = len(comparison)
    measured_runs = (
        int(results[0]["runs"])
        if results
        else 0
    )

    database_count = len(DATABASES)

    total_measured_executions = (
        total_queries
        * measured_runs
        * database_count
    )

    analysis = []

    analysis.append("# Graph Database Benchmark Analysis\n")

    analysis.append(
        "## 1. Benchmark Configuration\n\n"
    )

    analysis.append(
        f"- Databases: {', '.join(DATABASES)}\n"
        f"- Queries: {total_queries}\n"
        f"- Measured runs per query/database: {measured_runs}\n"
        f"- Total measured executions: "
        f"{total_measured_executions}\n"
        "- Primary metric: median latency\n"
        "- Additional metrics: P90, P95, P99, average, "
        "maximum latency, standard deviation and coefficient "
        "of variation\n"
    )

    analysis.append(
        "## 2. Overall Results\n\n"
        "### Fastest Database by Query\n"
    )

    for row in comparison:
        query = row["query"]
        database = row["fastest_database"]
        median = float(row["fastest_median_ms"])

        analysis.append(
            f"- **{query}**: {database} "
            f"({median:.3f} ms median)\n"
        )

    analysis.append(
        "\n### Number of Fastest Results\n\n"
        f"- Neo4j: {fastest_counts.get('Neo4j', 0)}\n"
        f"- Memgraph: {fastest_counts.get('Memgraph', 0)}\n"
        f"- FalkorDB: {fastest_counts.get('FalkorDB', 0)}\n"
    )

    analysis.append(
        "\n## 3. Average Median Latency\n\n"
        "| Database | Average of Query Medians |\n"
        "|---|---:|\n"
        f"| Neo4j | {average_medians['Neo4j']:.3f} ms |\n"
        f"| Memgraph | {average_medians['Memgraph']:.3f} ms |\n"
        f"| FalkorDB | {average_medians['FalkorDB']:.3f} ms |\n"
    )

    analysis.append(
        "\n## 4. Query-Level Findings\n\n"
    )

    analysis.append(
        create_query_findings(comparison)
    )

    analysis.append(
        "\n"
        + create_tail_analysis(results)
        + "\n"
    )

    analysis.append(
        "\n## 6. Important Observations\n\n"
    )

    fastest_database = min(
        average_medians,
        key=average_medians.get,
    )

    slowest_database = max(
        average_medians,
        key=average_medians.get,
    )

    analysis.append(
        f"- **{fastest_database}** has the lowest average "
        f"median latency across the tested queries "
        f"({average_medians[fastest_database]:.3f} ms).\n"
    )

    analysis.append(
        f"- **{slowest_database}** has the highest average "
        f"median latency across the tested queries "
        f"({average_medians[slowest_database]:.3f} ms).\n"
    )

    analysis.append(
        "- Median latency represents typical query performance, "
        "while P95 and P99 expose tail-latency behavior.\n"
    )

    analysis.append(
        "- A database can have a good median while still having "
        "poor tail latency if occasional slow executions occur.\n"
    )

    analysis.append(
        "\n## 7. Conclusion\n\n"
    )

    analysis.append(
        f"Based on the measured median latency, {fastest_database} "
        "performed best overall across this benchmark configuration. "
        "The fastest database was determined independently for each "
        "query using median latency.\n\n"
    )

    analysis.append(
        "The results are specific to this benchmark environment and "
        "should not be interpreted as a universal ranking of graph "
        "databases. Hardware limits, container CPU and memory limits, "
        "dataset size, indexes, query plans, database versions, "
        "configuration and workload characteristics can materially "
        "change the results.\n"
    )

    analysis.append(
        "\n## 8. Generated Charts\n\n"
        "- `charts/median_latency.png`\n"
        "- `charts/p95_latency.png`\n"
        "- `charts/p99_latency.png`\n"
        "- `charts/latency_variability.png`\n"
    )

    with open(ANALYSIS_FILE, "w") as file:
        file.write("".join(analysis))


def main():
    CHARTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    results = load_csv(
        RESULTS_FILE
    )

    comparison = load_csv(
        COMPARISON_FILE
    )

    if not results:
        raise RuntimeError(
            "benchmark_results.csv is empty."
        )

    if not comparison:
        raise RuntimeError(
            "benchmark_comparison.csv is empty."
        )

    create_median_chart(
        results
    )

    create_p95_chart(
        results
    )

    create_p99_chart(
        results
    )

    create_stability_chart(
        results
    )

    create_analysis(
        results,
        comparison,
    )

    print(
        "Analysis completed."
    )

    print(
        f"Analysis: {ANALYSIS_FILE}"
    )

    print(
        f"Charts: {CHARTS_DIR}"
    )


if __name__ == "__main__":
    main()
