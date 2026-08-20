# Graph Database Cloud Benchmark

A reproducible benchmark comparing graph database performance using identical datasets, workloads, and measurement methodology.

## Objective

This project evaluates graph database query performance across multiple graph database platforms.

The benchmark focuses on:

- Query latency
- Median latency
- P95 and P99 latency
- Latency variability
- Outlier behavior
- Relative performance between databases

The benchmark is designed to be reproducible and transparent.

## Databases

The current benchmark compares:

- Neo4j
- Memgraph
- FalkorDB

## Dataset

The benchmark uses a synthetic graph dataset containing:

- Persons
- Companies
- Cities
- `KNOWS` relationships
- `WORKS_AT` relationships
- `LIVES_IN` relationships

The dataset is stored in the `data/` directory.

## Workloads

Six query workloads are benchmarked:

1. Point lookup
2. Knows lookup
3. Person-company-city traversal
4. Two-hop traversal
5. Company aggregation
6. Shortest path

## Benchmark Methodology

Each query is executed using:

- 5 warm-up runs
- 100 measured runs

The benchmark records:

- Minimum latency
- Average latency
- Median latency
- P90 latency
- P95 latency
- P99 latency
- Maximum latency
- Standard deviation
- Coefficient of variation
- Outlier count

## Results

### Fastest Database by Median Latency

| Workload | Fastest Database | Median Latency |
|---|---|---:|
| Point lookup | FalkorDB | 0.415 ms |
| Knows lookup | Memgraph | 0.531 ms |
| Person-company-city | Memgraph | 0.453 ms |
| Two-hop traversal | Memgraph | 0.522 ms |
| Company aggregation | FalkorDB | 1.938 ms |
| Shortest path | FalkorDB | 0.935 ms |

### Summary

FalkorDB achieved the lowest median latency in 3 of the 6 workloads.

Memgraph achieved the lowest median latency in the other 3 workloads.

Neo4j was not the fastest database for any of the six tested workloads.

FalkorDB also demonstrated relatively low latency variability across most workloads, while Neo4j showed significant tail-latency spikes in several workloads.

These results apply specifically to the tested dataset, hardware, database configuration, and workloads. They should not be interpreted as a universal ranking of graph databases.

## Results Files

Benchmark results are available in the `results/` directory:

- `benchmark_results.csv` — summarized benchmark statistics
- `benchmark_raw.csv` — raw timing measurements
- `benchmark_comparison.csv` — database comparison
- `analysis.md` — benchmark analysis

Charts are available in:

`results/charts/`

Including:

- Median latency
- P95 latency
- Latency variability

## Project Structure

```text
graph-database-cloud-benchmark/
│
├── data/
│   ├── cities.csv
│   ├── companies.csv
│   ├── knows.csv
│   ├── lives_in.csv
│   ├── persons.csv
│   └── works_at.csv
│
├── results/
│   ├── analysis.md
│   ├── benchmark_results.csv
│   ├── benchmark_raw.csv
│   ├── benchmark_comparison.csv
│   └── charts/
│
├── src/
│   └── benchmark/
│       ├── analyze.py
│       ├── dataset.py
│       ├── load_data.py
│       ├── queries.py
│       └── runner.py
│
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md

