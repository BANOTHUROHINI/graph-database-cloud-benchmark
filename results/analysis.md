# Graph Database Benchmark Analysis

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

- **point_lookup**: FalkorDB (0.357 ms median)\n- **knows_lookup**: FalkorDB (0.426 ms median)\n- **person_company_city**: FalkorDB (0.493 ms median)\n- **two_hop_traversal**: FalkorDB (0.569 ms median)\n- **company_aggregation**: FalkorDB (1.801 ms median)\n- **short_path**: FalkorDB (0.941 ms median)\n
### Number of fastest results

- Neo4j: 0
- Memgraph: 0
- FalkorDB: 6

## 3. Average Median Latency

| Database | Average of Query Medians |
|---|---:|
| Neo4j | 1.410 ms |
| Memgraph | 0.953 ms |
| FalkorDB | 0.765 ms |

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
