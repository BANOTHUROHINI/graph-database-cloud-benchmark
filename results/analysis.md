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
- **point_lookup**: FalkorDB (0.486 ms median)
- **knows_lookup**: FalkorDB (0.539 ms median)
- **person_company_city**: FalkorDB (0.651 ms median)
- **two_hop_traversal**: FalkorDB (0.681 ms median)
- **company_aggregation**: FalkorDB (2.057 ms median)
- **short_path**: FalkorDB (1.080 ms median)

### Number of Fastest Results

- Neo4j: 0
- Memgraph: 0
- FalkorDB: 6

## 3. Average Median Latency

| Database | Average of Query Medians |
|---|---:|
| Neo4j | 1.950 ms |
| Memgraph | 1.135 ms |
| FalkorDB | 0.916 ms |

## 4. Query-Level Findings

### Point Lookup

**FalkorDB** was fastest with a median latency of **0.486 ms**.

- Neo4j: 1.422 ms median

- Memgraph: 0.670 ms median

- FalkorDB: 0.486 ms median


### Knows Lookup

**FalkorDB** was fastest with a median latency of **0.539 ms**.

- Neo4j: 1.459 ms median

- Memgraph: 0.877 ms median

- FalkorDB: 0.539 ms median


### Person Company City

**FalkorDB** was fastest with a median latency of **0.651 ms**.

- Neo4j: 1.382 ms median

- Memgraph: 0.766 ms median

- FalkorDB: 0.651 ms median


### Two Hop Traversal

**FalkorDB** was fastest with a median latency of **0.681 ms**.

- Neo4j: 1.565 ms median

- Memgraph: 0.730 ms median

- FalkorDB: 0.681 ms median


### Company Aggregation

**FalkorDB** was fastest with a median latency of **2.057 ms**.

- Neo4j: 3.538 ms median

- Memgraph: 2.533 ms median

- FalkorDB: 2.057 ms median


### Short Path

**FalkorDB** was fastest with a median latency of **1.080 ms**.

- Neo4j: 2.332 ms median

- Memgraph: 1.234 ms median

- FalkorDB: 1.080 ms median


## 5. Latency Stability

Tail latency is evaluated using P95 and P99 rather than median latency alone.

### Neo4j

- Average CV: **274.70%**
- Highest P99: **84.209 ms** for `point_lookup`

### Memgraph

- Average CV: **236.30%**
- Highest P99: **47.429 ms** for `short_path`

### FalkorDB

- Average CV: **15.09%**
- Highest P99: **4.173 ms** for `company_aggregation`

The database with the lowest average CV has the most stable latency across the tested queries. A high P99 relative to the median indicates occasional latency spikes.

## 6. Important Observations

- **FalkorDB** has the lowest average median latency across the tested queries (0.916 ms).
- **Neo4j** has the highest average median latency across the tested queries (1.950 ms).
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
