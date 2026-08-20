# Graph Database Benchmark Analysis

## Overview

This benchmark compares Neo4j, Memgraph, and FalkorDB using six graph query workloads:

- Point lookup
- Knows lookup
- Person-company-city traversal
- Two-hop traversal
- Company aggregation
- Shortest path

Each query was warmed up for 5 runs and measured for 100 runs.

## Results

FalkorDB achieved the lowest median latency for:

- point_lookup: 0.415 ms
- company_aggregation: 1.938 ms
- short_path: 0.935 ms

Memgraph achieved the lowest median latency for:

- knows_lookup: 0.531 ms
- person_company_city: 0.453 ms
- two_hop_traversal: 0.522 ms

Neo4j was not the fastest workload for any of the six tested queries.

## Stability

FalkorDB showed substantially lower latency variability for most workloads. Its coefficient of variation was below 25% for knows_lookup, person_company_city, two_hop_traversal, and company_aggregation.

Neo4j showed large tail-latency spikes, with p99 latency reaching approximately 59–75 ms for several queries despite median latency near 1–3 ms.

Memgraph was generally faster than Neo4j at the median, but some workloads also contained large outliers.

## Conclusion

For this benchmark environment and workload, FalkorDB and Memgraph provided lower median latency than Neo4j. FalkorDB was the fastest overall for three workloads and showed particularly consistent latency for most queries. Memgraph was fastest for three traversal-oriented workloads.

These results are specific to the tested dataset, hardware, configuration, and query workloads and should not be interpreted as a universal ranking of the databases.
