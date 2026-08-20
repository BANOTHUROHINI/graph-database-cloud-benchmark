import csv
from pathlib import Path
import matplotlib.pyplot as plt


RESULTS_DIR = Path("results")
CHARTS_DIR = RESULTS_DIR / "charts"

RESULTS_FILE = RESULTS_DIR / "benchmark_results.csv"
COMPARISON_FILE = RESULTS_DIR / "benchmark_comparison.csv"
ANALYSIS_FILE = RESULTS_DIR / "analysis.md"


def load_csv(path):
    with open(path, newline="") as file:
        return list(csv.DictReader(file))


def create_median_chart(results):
    queries = sorted(set(row["query"] for row in results))
    databases = ["Neo4j", "Memgraph", "FalkorDB"]

    x = range(len(queries))
    width = 0.25

    plt.figure(figsize=(12, 6))

    for index, database in enumerate(databases):
        values = []

        for query in queries:
            row = next(
                r for r in results
                if r["database"] == database
                and r["query"] == query
            )

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
        list(x),
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
    databases = ["Neo4j", "Memgraph", "FalkorDB"]

    x = range(len(queries))
    width = 0.25

    plt.figure(figsize=(12, 6))

    for index, database in enumerate(databases):
        values = []

        for query in queries:
            row = next(
                r for r in results
                if r["database"] == database
                and r["query"] == query
            )

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
        list(x),
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


def create_stability_chart(results):
    databases = ["Neo4j", "Memgraph", "FalkorDB"]

    cv_values = []

    for database in databases:
        values = [
            float(row["cv_percent"])
            for row in results
            if row["database"] == database
        ]

        cv_values.append(
            sum(values) / len(values)
        )

    plt.figure(figsize=(8, 5))

    plt.bar(
        databases,
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


def create_analysis(results, comparison):
    fastest_counts = {}

    for row in comparison:
        database = row["fastest_database"]

        fastest_counts[database] = (
            fastest_counts.get(database, 0) + 1
        )

    neo4j_medians = [
        float(row["median_ms"])
        for row in results
        if row["database"] == "Neo4j"
    ]

    memgraph_medians = [
        float(row["median_ms"])
        for row in results
        if row["database"] == "Memgraph"
    ]

    falkordb_medians = [
        float(row["median_ms"])
        for row in results
        if row["database"] == "FalkorDB"
    ]

    def average(values):
        return sum(values) / len(values)

    analysis = f"""# Graph Database Benchmark Analysis

## 1. Benchmark Configuration

- Databases: Neo4j, Memgraph, FalkorDB
- Queries: 6
- Warm-up runs: 5
- Measured runs per query: 100
- Total measured executions: 1,800
- Primary metric: median latency
- Additional metrics: P95, P99, average, maximum latency and coefficient of variation

## 2. Overall Results

### Fastest database by query

"""

    for row in comparison:
        analysis += (
            f"- **{row['query']}**: "
            f"{row['fastest_database']} "
            f"({float(row['fastest_median_ms']):.3f} ms median)\\n"
        )

    analysis += f"""
### Number of fastest results

- Neo4j: {fastest_counts.get("Neo4j", 0)}
- Memgraph: {fastest_counts.get("Memgraph", 0)}
- FalkorDB: {fastest_counts.get("FalkorDB", 0)}

## 3. Average Median Latency

| Database | Average of Query Medians |
|---|---:|
| Neo4j | {average(neo4j_medians):.3f} ms |
| Memgraph | {average(memgraph_medians):.3f} ms |
| FalkorDB | {average(falkordb_medians):.3f} ms |

## 4. Query-Level Findings

### Point Lookup

FalkorDB recorded the lowest median latency at approximately
0.415 ms, followed closely by Memgraph at approximately
0.455 ms. Neo4j recorded approximately 1.076 ms.

### Knows Lookup

Memgraph was fastest with a median of approximately
0.531 ms. FalkorDB followed at approximately 0.571 ms,
while Neo4j recorded approximately 1.145 ms.

### Person-Company-City Traversal

Memgraph achieved the lowest median latency at approximately
0.453 ms. FalkorDB recorded approximately 0.592 ms,
while Neo4j recorded approximately 1.097 ms.

### Two-Hop Traversal

Memgraph was fastest with approximately 0.522 ms median latency.
FalkorDB was approximately 0.601 ms and Neo4j approximately
1.095 ms.

### Company Aggregation

FalkorDB recorded the lowest median latency at approximately
1.938 ms, narrowly beating Memgraph at approximately
1.961 ms. Neo4j recorded approximately 3.163 ms.

### Shortest Path

FalkorDB was fastest with approximately 0.935 ms median latency.
Memgraph recorded approximately 1.029 ms and Neo4j approximately
1.737 ms.

## 5. Latency Stability

The results show a major difference in tail behavior.

Neo4j has very large P99 values for several queries. For example:

- Point lookup P99: approximately 70.933 ms
- Two-hop traversal P99: approximately 74.655 ms
- Shortest path P99: approximately 68.442 ms

Memgraph also shows occasional large outliers.

FalkorDB is substantially more stable for most queries, although
the shortest-path workload contains one large outlier.

## 6. Important Observation

Median latency alone does not tell the entire story.

For this benchmark, Neo4j's median latency is reasonably low, but
its P99 latency is dramatically higher for several workloads.
This indicates occasional latency spikes.

Memgraph provides the best median performance for three of the
six queries.

FalkorDB provides the best median performance for three of the
six queries and generally shows lower variability.

## 7. Conclusion

For the tested workload:

1. **FalkorDB and Memgraph outperform Neo4j on median latency.**
2. **Memgraph is fastest for traversal-heavy queries such as
   knows_lookup, person_company_city and two_hop_traversal.**
3. **FalkorDB is fastest for point lookup, aggregation and
   shortest-path workloads.**
4. **Neo4j shows significantly higher tail latency in this local
   benchmark environment.**
5. The results should not be interpreted as a universal ranking of
   graph databases because workload size, hardware, indexes,
   configuration, query plans and deployment architecture can
   materially affect performance.

## 8. Generated Charts

- `charts/median_latency.png`
- `charts/p95_latency.png`
- `charts/latency_variability.png`
"""

    with open(ANALYSIS_FILE, "w") as file:
        file.write(analysis)


def main():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    results = load_csv(RESULTS_FILE)
    comparison = load_csv(COMPARISON_FILE)

    create_median_chart(results)
    create_p95_chart(results)
    create_stability_chart(results)
    create_analysis(results, comparison)

    print("Analysis completed.")
    print(f"Analysis: {ANALYSIS_FILE}")
    print(f"Charts: {CHARTS_DIR}")


if __name__ == "__main__":
    main()