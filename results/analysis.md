# Graph Database Benchmark Analysis
## 1. Benchmark Configuration

- Databases: Neo4j, Memgraph, FalkorDB
- Queries: 6
- Measured runs per query/database: 100
- Total measured executions: 1800
- Primary metric: median latency
- Additional metrics: P90, P95, P99, average, maximum latency, standard deviation and coefficient of variation
## 2. Overall Results

### Fastest Database by Query
- **point_lookup**: FalkorDB (0.480 ms median)
- **knows_lookup**: FalkorDB (0.566 ms median)
- **person_company_city**: Memgraph (0.589 ms median)
- **two_hop_traversal**: FalkorDB (0.642 ms median)
- **company_aggregation**: FalkorDB (2.112 ms median)
- **short_path**: FalkorDB (1.095 ms median)

### Number of Fastest Results

- Neo4j: 0
- Memgraph: 1
- FalkorDB: 5

## 3. Average Median Latency

| Database | Average of Query Medians |
|---|---:|
| Neo4j | 2.975 ms |
| Memgraph | 1.055 ms |
| FalkorDB | 0.923 ms |

## 4. Query-Level Findings

### Point Lookup

**FalkorDB** was fastest with a median latency of **0.480 ms**.

- Neo4j: 3.293 ms median

- Memgraph: 0.611 ms median

- FalkorDB: 0.480 ms median


### Knows Lookup

**FalkorDB** was fastest with a median latency of **0.566 ms**.

- Neo4j: 2.809 ms median

- Memgraph: 0.708 ms median

- FalkorDB: 0.566 ms median


### Person Company City

**Memgraph** was fastest with a median latency of **0.589 ms**.

- Neo4j: 2.345 ms median

- Memgraph: 0.589 ms median

- FalkorDB: 0.644 ms median


### Two Hop Traversal

**FalkorDB** was fastest with a median latency of **0.642 ms**.

- Neo4j: 1.901 ms median

- Memgraph: 0.678 ms median

- FalkorDB: 0.642 ms median


### Company Aggregation

**FalkorDB** was fastest with a median latency of **2.112 ms**.

- Neo4j: 4.688 ms median

- Memgraph: 2.463 ms median

- FalkorDB: 2.112 ms median


### Short Path

**FalkorDB** was fastest with a median latency of **1.095 ms**.

- Neo4j: 2.816 ms median

- Memgraph: 1.278 ms median

- FalkorDB: 1.095 ms median


## 5. Latency Stability

Tail latency is evaluated using P95 and P99 rather than median latency alone.

### Neo4j

- Average CV: **195.01%**
- Highest P99: **92.241 ms** for `point_lookup`

### Memgraph

- Average CV: **246.97%**
- Highest P99: **47.017 ms** for `short_path`

### FalkorDB

- Average CV: **34.90%**
- Highest P99: **2.951 ms** for `company_aggregation`

The database with the lowest average CV has the most stable latency across the tested queries. A high P99 relative to the median indicates occasional latency spikes.

## 6. Important Observations

- **FalkorDB** has the lowest average median latency across the tested queries (0.923 ms).
- **Neo4j** has the highest average median latency across the tested queries (2.975 ms).
- Median latency represents typical query performance, while P95 and P99 expose tail-latency behavior.
- A database can have a good median while still having poor tail latency if occasional slow executions occur.

## 7. Conclusion

Based on the measured median latency, FalkorDB performed best overall across this benchmark configuration. The fastest database was determined independently for each query using median latency.

The results are specific to this benchmark environment and should not be interpreted as a universal ranking of graph databases. Hardware limits, container CPU and memory limits, dataset size, indexes, query plans, database versions, configuration and workload characteristics can materially change the results.

## 8. Generated Charts

- `charts/median_latency.png`
- `charts/p95_latency.png`
- `charts/p99_latency.png`
- `charts/latency_variability.png`
