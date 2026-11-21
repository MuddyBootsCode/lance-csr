# Issue 186 performance evidence

The baseline is upstream main at `c9cd09659e7deb2516b88d8c6f65ead5f2b3a9b6`. The branch is the same revision plus the patch in this folder. Both release wheels use Rust 1.96.0 and the same macOS SDK. Measurements were taken on AC power. Elapsed times include the query's planning and execution. The feature-specific timings exclude client conversion and validation.

## Chain-of-title example

The graph is a four-level tree of 4,681 parties and 4,680 relationships. Each internal node has eight children. Stored direction reverses between levels and edges use three different types. An optional query seeded at the root returns the same 584 distinct parties within three hops on every successful run. Baseline unnamed queries raise an unsupported-feature error.

Each cell is the median of 12 timed executions in milliseconds after one correctness check. The branch alternates named and unnamed queries within each run. Each build runs twice in alternating order. The final column compares the average of the two unnamed branch medians with the average of the two named baseline medians.

| Storage | CSR | Main named 1 | Main named 2 | Branch unnamed 1 | Branch unnamed 2 | Branch named 1 | Branch named 2 | Change |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| memory | False | 2.149 | 2.165 | 2.041 | 2.096 | 2.213 | 2.115 | -4.1% |
| memory | True | 2.091 | 2.097 | 2.059 | 2.122 | 2.032 | 2.176 | -0.1% |
| lazy | False | 3.069 | 3.045 | 2.948 | 3.000 | 3.017 | 3.051 | -2.7% |
| lazy | True | 2.999 | 2.999 | 2.944 | 2.896 | 3.012 | 3.002 | -2.6% |

## SF1 tag hierarchy

The same traversal is applied to the unmodified SF1 Tag, Tagclass, hasType and isSubclassOf tables. Seeds have the lowest and highest nonzero degree in the participating subgraph. The query requests distinct Tag endpoints reached within two or three hops. An independent traversal verifies the returned IDs against the actual stored relationships, including the optional null row when appropriate. CSR is enabled. Each cell is the median of eight timed executions, in milliseconds.

| Storage | Seed ID | Degree | Hop bound | Non-null IDs | Main named 1 | Main named 2 | Branch unnamed 1 | Branch unnamed 2 | Branch named 1 | Branch named 2 | Change |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| memory | 46 | 2 | 2 | 9 | 3.987 | 3.836 | 3.996 | 3.854 | 3.951 | 3.930 | +0.3% |
| memory | 46 | 2 | 3 | 88 | 3.866 | 3.889 | 3.829 | 4.127 | 3.911 | 4.075 | +2.6% |
| memory | 182 | 5062 | 2 | 5061 | 5.782 | 5.855 | 5.329 | 5.603 | 5.738 | 5.946 | -6.1% |
| memory | 182 | 5062 | 3 | 9901 | 8.063 | 8.109 | 6.789 | 6.838 | 8.100 | 8.167 | -15.7% |
| lazy | 46 | 2 | 2 | 9 | 5.009 | 5.095 | 4.965 | 5.007 | 4.936 | 5.076 | -1.3% |
| lazy | 46 | 2 | 3 | 88 | 5.042 | 5.129 | 4.865 | 4.972 | 4.967 | 4.947 | -3.3% |
| lazy | 182 | 5062 | 2 | 5061 | 6.889 | 6.857 | 6.393 | 6.585 | 6.908 | 7.001 | -5.6% |
| lazy | 182 | 5062 | 3 | 9901 | 9.304 | 9.123 | 7.954 | 7.741 | 9.155 | 9.081 | -14.8% |

## Same-build comparison

On the same branch wheel, omitting the path name reduced median latency on the high-degree, three-hop SF1 query by about 16% in memory and 14% on disk. Both runs showed the difference. The low-degree and eight-way tree samples did not show a consistent gain beyond timing variation. The high-degree traversal produced 9,901 trails and 9,901 distinct endpoints. These timings use a bound starting node. Queries with only the far endpoint filtered may enumerate trails from many more starting nodes.

The unnamed multi-type form uses the named form’s trail semantics. It can return to a node via a different parallel relationship, and it cannot reuse the same stored relationship later in the trail. The existing anonymous single-type traversal skips immediate backtracking.

A separate case discovered in review reproduces on both upstream main and the branch. A **named** path inside an EXISTS predicate with a parameter in its endpoint property map can fail with an unbound placeholder. The new unnamed case is planned for each execution with the supplied parameter values. This patch leaves the existing named case for separate consideration.

Each cell with two ranges shows the interquartile range of timings within each run. The percentage compares the averages of the two run medians on the same branch wheel.

| Graph | Storage | CSR | Seed | Hops | Unnamed vs named on branch | Named IQRs, ms | Unnamed IQRs, ms |
|---|---|---|---|---:|---:|---|---|
| eight-way tree | memory | False | root | 3 | -4.4% | 2.12–2.25 / 2.03–2.17 | 2.02–2.12 / 2.06–2.15 |
| eight-way tree | memory | True | root | 3 | -0.6% | 2.00–2.13 / 2.16–2.21 | 2.00–2.11 / 2.09–2.16 |
| eight-way tree | lazy | False | root | 3 | -2.0% | 2.98–3.16 / 2.98–3.10 | 2.90–3.02 / 2.90–3.04 |
| eight-way tree | lazy | True | root | 3 | -2.9% | 2.99–3.07 / 2.97–3.04 | 2.89–3.01 / 2.81–2.93 |
| SF1 tag hierarchy | memory | True | 46 | 2 | -0.4% | 3.88–4.05 / 3.89–4.02 | 3.92–4.06 / 3.80–3.92 |
| SF1 tag hierarchy | memory | True | 46 | 3 | -0.4% | 3.89–3.95 / 4.05–4.14 | 3.79–3.85 / 4.04–4.14 |
| SF1 tag hierarchy | memory | True | 182 | 2 | -6.4% | 5.64–5.80 / 5.91–5.99 | 5.27–5.35 / 5.52–5.65 |
| SF1 tag hierarchy | memory | True | 182 | 3 | -16.2% | 8.04–8.16 / 8.11–8.33 | 6.66–6.87 / 6.81–6.90 |
| SF1 tag hierarchy | lazy | True | 46 | 2 | -0.4% | 4.87–5.01 / 4.98–5.31 | 4.91–5.01 / 4.91–5.52 |
| SF1 tag hierarchy | lazy | True | 46 | 3 | -0.8% | 4.89–4.99 / 4.92–5.01 | 4.84–4.95 / 4.95–4.98 |
| SF1 tag hierarchy | lazy | True | 182 | 2 | -6.7% | 6.79–6.97 / 6.88–7.04 | 6.32–6.51 / 6.44–6.62 |
| SF1 tag hierarchy | lazy | True | 182 | 3 | -13.9% | 9.02–9.31 / 9.04–9.22 | 7.87–8.09 / 7.63–7.89 |

## Execution plans

<details>
<summary>main, named, physical EXPLAIN</summary>

```text
SortPreservingMergeExec: [id@0 ASC NULLS LAST]
  SortExec: expr=[id@0 ASC NULLS LAST], preserve_partitioning=[true]
    AggregateExec: mode=FinalPartitioned, gby=[id@0 as id], aggr=[]
      RepartitionExec: partitioning=Hash([id@0], 18), input_partitions=18
        AggregateExec: mode=Partial, gby=[id@0 as id], aggr=[]
          ProjectionExec: expr=[q__id@0 as id]
            HashJoinExec: mode=CollectLeft, join_type=Left, on=[(s__id@0, __optional__s__id@0)], projection=[q__id@2], NullsEqual: true
              ProjectionExec: expr=[id@0 as s__id]
                FilterExec: id@0 = 0
                  KeyStatisticsExec: distinct=[id=4681]
                    DataSourceExec: partitions=1, partition_sizes=[1]
              ProjectionExec: expr=[s__id@0 as __optional__s__id, q__id@2 as q__id]
                PathMatchExec: p edge inventory
                  AggregateExec: mode=FinalPartitioned, gby=[s__id@0 as s__id, s__name@1 as s__name], aggr=[], ordering_mode=PartiallySorted([0])
                    RepartitionExec: partitioning=Hash([s__id@0, s__name@1], 18), input_partitions=18
                      AggregateExec: mode=Partial, gby=[s__id@0 as s__id, s__name@1 as s__name], aggr=[], ordering_mode=PartiallySorted([0])
                        RepartitionExec: partitioning=RoundRobinBatch(18), input_partitions=1
                          ProjectionExec: expr=[id@0 as s__id, name@1 as s__name]
                            FilterExec: id@0 = 0
                              KeyStatisticsExec: distinct=[id=4681]
                                DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[id=4681]
                    DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[dst=1089, src=520]
                    DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[dst=1601, src=520]
                    DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[dst=1601, src=520]
                    DataSourceExec: partitions=1, partition_sizes=[1]
```

</details>

<details>
<summary>branch, unnamed, physical EXPLAIN</summary>

```text
SortPreservingMergeExec: [id@0 ASC NULLS LAST]
  SortExec: expr=[id@0 ASC NULLS LAST], preserve_partitioning=[true]
    AggregateExec: mode=FinalPartitioned, gby=[id@0 as id], aggr=[]
      RepartitionExec: partitioning=Hash([id@0], 18), input_partitions=18
        AggregateExec: mode=Partial, gby=[id@0 as id], aggr=[]
          ProjectionExec: expr=[q__id@0 as id]
            HashJoinExec: mode=CollectLeft, join_type=Left, on=[(s__id@0, __optional__s__id@0)], projection=[q__id@2], NullsEqual: true
              ProjectionExec: expr=[id@0 as s__id]
                FilterExec: id@0 = 0
                  KeyStatisticsExec: distinct=[id=4681]
                    DataSourceExec: partitions=1, partition_sizes=[1]
              ProjectionExec: expr=[s__id@0 as __optional__s__id, q__id@2 as q__id]
                PathMatchExec: endpoints edge inventory
                  AggregateExec: mode=FinalPartitioned, gby=[s__id@0 as s__id, s__name@1 as s__name], aggr=[], ordering_mode=PartiallySorted([0])
                    RepartitionExec: partitioning=Hash([s__id@0, s__name@1], 18), input_partitions=18
                      AggregateExec: mode=Partial, gby=[s__id@0 as s__id, s__name@1 as s__name], aggr=[], ordering_mode=PartiallySorted([0])
                        RepartitionExec: partitioning=RoundRobinBatch(18), input_partitions=1
                          ProjectionExec: expr=[id@0 as s__id, name@1 as s__name]
                            FilterExec: id@0 = 0
                              KeyStatisticsExec: distinct=[id=4681]
                                DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[id=4681]
                    DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[dst=1089, src=520]
                    DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[dst=1601, src=520]
                    DataSourceExec: partitions=1, partition_sizes=[1]
                  KeyStatisticsExec: distinct=[dst=1601, src=520]
                    DataSourceExec: partitions=1, partition_sizes=[1]
```

</details>


The baseline workaround has a PathMatchExec with a named path. The new form has one endpoint-only PathMatchExec. Both read the same participating node and relationship tables, build a query-local inventory, and track the stored edges used by each trail. Only the named form constructs an Arrow path value for every output row. The raw timings include the corresponding [named EXPLAIN ANALYZE](plans/profile-main1-memory-named.txt) and [unnamed EXPLAIN ANALYZE](plans/profile-branch1-memory-unnamed.txt) outputs. The operator still emits boundary property columns. Highly connected graphs can have many trails to the same endpoint before DISTINCT runs.

graph-benchmark-ldbc lazy 30 differ: none
graph-benchmark-ldbc memory 30 differ: none
graph-benchmark-ldbc-complex lazy 14 differ: 3
graph-benchmark-ldbc-complex memory 14 differ: 3
The 30-query suite had identical physical plans for all 30 queries in both modes. Thirteen of the 14 complex queries also matched line for line in each mode after stripping display padding. IC3 alone printed a different order for two ANDed equality predicates on the Place scan. Three additional EXPLAINs per mode on the baseline reproduced both orders. The operators, columns, graph traversal and predicates matched. IC3 mean timing changed by −0.7% in memory and +1.2% in lazy mode.

All 16 official suite runs passed their expected answers. The benchmark process was the only validation slot in use at each run start. Per-query means, baseline repeat deltas and geometric means follow. For the feature-specific queries the named workaround runs on current upstream, and the unnamed spelling raises NotImplementedError there. On the branch, the exact published issue query returned [2, 3, 4, 5] in required and optional matches, with CSR enabled and disabled.

The release patch SHA-256 is b521f96a426de834af817367672c36047d36735f00905e9db39ad89bcc031601. Rust passed 738 tests with 11 ignored. Python passed 1,763 tests with one skipped. Formatting, Clippy, Ruff, Pyright, spelling, the strict documentation build and 18 executable Cypher examples passed. The guide's optional separate 100K-person example dataset was unavailable; the two required SF1 benchmark datasets were present and exercised.

The new operator follows the existing inventory's ID and label rules. IDs must be signed integers or uint8/16/32. Each endpoint needs a known label. The directed, single-type, unbounded, multi-segment and comma-separated forms do not enter the new standalone fast path.

## Standard SF1 suites

# Issue 186 benchmark comparison

Baseline commit `c9cd09659e7deb2516b88d8c6f65ead5f2b3a9b6`. Branch build uses the same commit plus `branch.patch` (SHA-256 `b521f96a426de834af817367672c36047d36735f00905e9db39ad89bcc031601`).

Both release wheels were built on Apple M5 Max with 128 GiB, macOS 27.0.1, Rust 1.96.0 and the macOS 26.2 Command Line Tools SDK.

Each workload ran twice per wheel in each storage mode. Lower latency is faster. The load averages and active validation slots at the start of each run are in `machine-load.jsonl`.

## graph-benchmark-ldbc

Runner commit `199852076ba8dceb345e18eeb2f8ac04c73f3ea1`.

### memory

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 0.706 | 0.703 | 0.728 | 0.697 | +1.1% | -0.4% |
| test_benchmark_query2 | 0.588 | 0.602 | 0.698 | 0.571 | +6.6% | +2.3% |
| test_benchmark_query3 | 0.680 | 0.917 | 0.680 | 0.672 | -15.3% | +34.9% |
| test_benchmark_query4 | 0.541 | 0.549 | 0.532 | 0.655 | +8.9% | +1.4% |
| test_benchmark_query5 | 1.022 | 1.033 | 1.015 | 1.032 | -0.4% | +1.0% |
| test_benchmark_query6 | 0.471 | 0.467 | 0.461 | 0.477 | -0.1% | -0.7% |
| test_benchmark_query7 | 1.251 | 1.246 | 1.204 | 1.238 | -2.2% | -0.4% |
| test_benchmark_query8 | 1.021 | 0.790 | 0.783 | 0.789 | -13.2% | -22.7% |
| test_benchmark_query9 | 0.924 | 0.867 | 0.888 | 0.898 | -0.3% | -6.1% |
| test_benchmark_query10 | 0.884 | 0.879 | 1.010 | 0.885 | +7.4% | -0.6% |
| test_benchmark_query11 | 1.647 | 2.079 | 1.854 | 1.667 | -5.5% | +26.3% |
| test_benchmark_query12 | 0.764 | 0.800 | 0.776 | 0.949 | +10.3% | +4.7% |
| test_benchmark_query13 | 0.839 | 0.818 | 0.853 | 0.850 | +2.8% | -2.6% |
| test_benchmark_query14 | 0.563 | 0.571 | 0.567 | 0.586 | +1.7% | +1.5% |
| test_benchmark_query15 | 0.601 | 0.609 | 0.614 | 0.621 | +2.1% | +1.4% |
| test_benchmark_query16 | 0.716 | 0.704 | 0.721 | 0.763 | +4.5% | -1.7% |
| test_benchmark_query17 | 1.318 | 1.061 | 1.122 | 1.059 | -8.3% | -19.5% |
| test_benchmark_query18 | 0.732 | 0.731 | 0.737 | 0.732 | +0.4% | -0.2% |
| test_benchmark_query19 | 1.097 | 1.147 | 1.411 | 1.094 | +11.6% | +4.5% |
| test_benchmark_query20 | 1.627 | 1.736 | 1.493 | 1.700 | -5.0% | +6.7% |
| test_benchmark_query21 | 0.892 | 0.791 | 0.782 | 0.849 | -3.1% | -11.4% |
| test_benchmark_query22 | 0.774 | 0.761 | 0.771 | 0.763 | -0.0% | -1.7% |
| test_benchmark_query23 | 0.788 | 0.792 | 0.813 | 0.808 | +2.6% | +0.6% |
| test_benchmark_query24 | 0.737 | 0.731 | 0.760 | 0.738 | +2.1% | -0.8% |
| test_benchmark_query25 | 0.873 | 0.866 | 0.860 | 0.850 | -1.7% | -0.8% |
| test_benchmark_query26 | 0.955 | 0.796 | 0.839 | 0.796 | -6.6% | -16.6% |
| test_benchmark_query27 | 0.906 | 0.896 | 1.111 | 0.949 | +14.4% | -1.0% |
| test_benchmark_query28 | 1.408 | 1.670 | 1.458 | 1.493 | -4.1% | +18.7% |
| test_benchmark_query29 | 0.794 | 0.777 | 0.770 | 0.885 | +5.4% | -2.1% |
| test_benchmark_query30 | 9.512 | 9.568 | 10.128 | 9.625 | +3.5% | +0.6% |

Geometric mean of per-query branch/main ratios: 1.0043.

### lazy

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 1.220 | 1.190 | 1.207 | 1.183 | -0.8% | -2.4% |
| test_benchmark_query2 | 1.388 | 1.392 | 1.373 | 1.366 | -1.5% | +0.3% |
| test_benchmark_query3 | 0.821 | 0.793 | 0.791 | 0.810 | -0.8% | -3.5% |
| test_benchmark_query4 | 0.945 | 0.926 | 0.904 | 0.924 | -2.3% | -2.0% |
| test_benchmark_query5 | 2.471 | 1.983 | 1.960 | 1.960 | -12.0% | -19.8% |
| test_benchmark_query6 | 0.797 | 0.829 | 0.855 | 0.801 | +1.8% | +3.9% |
| test_benchmark_query7 | 1.265 | 1.354 | 1.373 | 1.420 | +6.7% | +7.0% |
| test_benchmark_query8 | 1.559 | 1.534 | 1.538 | 1.545 | -0.3% | -1.6% |
| test_benchmark_query9 | 1.286 | 1.249 | 1.272 | 1.340 | +3.0% | -2.9% |
| test_benchmark_query10 | 1.130 | 1.104 | 1.108 | 1.117 | -0.4% | -2.3% |
| test_benchmark_query11 | 2.041 | 2.031 | 2.008 | 2.085 | +0.5% | -0.5% |
| test_benchmark_query12 | 4.511 | 4.430 | 4.398 | 4.453 | -1.0% | -1.8% |
| test_benchmark_query13 | 1.302 | 1.179 | 1.210 | 1.199 | -2.9% | -9.5% |
| test_benchmark_query14 | 0.888 | 0.762 | 0.770 | 0.761 | -7.2% | -14.2% |
| test_benchmark_query15 | 0.856 | 0.988 | 0.978 | 0.947 | +4.4% | +15.4% |
| test_benchmark_query16 | 1.008 | 1.030 | 1.033 | 1.008 | +0.2% | +2.2% |
| test_benchmark_query17 | 1.725 | 1.811 | 1.683 | 1.673 | -5.1% | +5.0% |
| test_benchmark_query18 | 1.415 | 1.409 | 1.370 | 1.367 | -3.1% | -0.4% |
| test_benchmark_query19 | 1.615 | 1.539 | 1.556 | 1.541 | -1.8% | -4.7% |
| test_benchmark_query20 | 39.998 | 39.700 | 39.775 | 39.437 | -0.6% | -0.7% |
| test_benchmark_query21 | 0.860 | 0.837 | 0.838 | 0.807 | -3.1% | -2.7% |
| test_benchmark_query22 | 1.307 | 1.161 | 1.212 | 1.147 | -4.4% | -11.2% |
| test_benchmark_query23 | 1.327 | 1.521 | 1.294 | 1.371 | -6.4% | +14.6% |
| test_benchmark_query24 | 1.035 | 1.031 | 1.000 | 1.032 | -1.6% | -0.4% |
| test_benchmark_query25 | 1.322 | 1.295 | 1.271 | 1.273 | -2.8% | -2.1% |
| test_benchmark_query26 | 1.081 | 1.040 | 1.064 | 1.102 | +2.1% | -3.8% |
| test_benchmark_query27 | 1.447 | 1.465 | 1.409 | 1.394 | -3.8% | +1.2% |
| test_benchmark_query28 | 1.954 | 2.051 | 1.945 | 1.937 | -3.1% | +5.0% |
| test_benchmark_query29 | 1.201 | 1.154 | 1.133 | 1.078 | -6.1% | -3.9% |
| test_benchmark_query30 | 12.674 | 13.316 | 12.409 | 12.359 | -4.7% | +5.1% |

Geometric mean of per-query branch/main ratios: 0.9803.

## graph-benchmark-ldbc-complex

Runner commit `a332324f2d4660b03d1d429d8ef99767af3981e5`.

### memory

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 23.430 | 23.834 | 22.957 | 22.977 | -2.8% | +1.7% |
| test_benchmark_query2 | 2.523 | 2.586 | 2.550 | 2.581 | +0.4% | +2.5% |
| test_benchmark_query3 | 21.858 | 20.893 | 21.269 | 21.197 | -0.7% | -4.4% |
| test_benchmark_query4 | 6.158 | 6.308 | 6.639 | 6.404 | +4.6% | +2.4% |
| test_benchmark_query5 | 38.757 | 39.340 | 40.512 | 40.629 | +3.9% | +1.5% |
| test_benchmark_query6 | 20.702 | 20.601 | 22.545 | 20.829 | +5.0% | -0.5% |
| test_benchmark_query7 | 9.542 | 9.780 | 9.477 | 9.347 | -2.6% | +2.5% |
| test_benchmark_query8 | 2.405 | 2.444 | 2.415 | 2.372 | -1.3% | +1.6% |
| test_benchmark_query9 | 35.762 | 35.538 | 35.834 | 35.730 | +0.4% | -0.6% |
| test_benchmark_query10 | 14.997 | 14.992 | 14.723 | 14.547 | -2.4% | -0.0% |
| test_benchmark_query11 | 3.059 | 3.134 | 3.107 | 3.349 | +4.2% | +2.5% |
| test_benchmark_query12 | 15.104 | 15.643 | 14.842 | 14.798 | -3.6% | +3.6% |
| test_benchmark_query13 | 1.158 | 1.143 | 1.135 | 1.131 | -1.5% | -1.3% |
| test_benchmark_query14 | 241.467 | 248.242 | 245.194 | 243.433 | -0.2% | +2.8% |

Geometric mean of per-query branch/main ratios: 1.0021.

### lazy

| Query | Main 1 ms | Main 2 ms | Branch 1 ms | Branch 2 ms | Mean change | Baseline repeat change |
|---|---:|---:|---:|---:|---:|---:|
| test_benchmark_query1 | 36.235 | 35.691 | 34.300 | 35.179 | -3.4% | -1.5% |
| test_benchmark_query2 | 25.584 | 24.728 | 25.075 | 25.578 | +0.7% | -3.3% |
| test_benchmark_query3 | 156.647 | 157.030 | 159.983 | 157.395 | +1.2% | +0.2% |
| test_benchmark_query4 | 13.536 | 14.517 | 13.986 | 14.213 | +0.5% | +7.2% |
| test_benchmark_query5 | 69.120 | 69.096 | 69.888 | 71.437 | +2.2% | -0.0% |
| test_benchmark_query6 | 25.009 | 22.299 | 23.642 | 23.204 | -1.0% | -10.8% |
| test_benchmark_query7 | 14.260 | 14.112 | 13.931 | 13.750 | -2.4% | -1.0% |
| test_benchmark_query8 | 3.391 | 3.481 | 3.533 | 3.396 | +0.8% | +2.6% |
| test_benchmark_query9 | 207.231 | 227.554 | 207.964 | 204.019 | -5.2% | +9.8% |
| test_benchmark_query10 | 23.430 | 24.082 | 23.665 | 23.260 | -1.2% | +2.8% |
| test_benchmark_query11 | 5.860 | 5.740 | 5.687 | 6.192 | +2.4% | -2.1% |
| test_benchmark_query12 | 19.406 | 19.460 | 19.419 | 17.884 | -4.0% | +0.3% |
| test_benchmark_query13 | 1.752 | 1.430 | 1.443 | 1.414 | -10.2% | -18.4% |
| test_benchmark_query14 | 251.289 | 250.865 | 268.708 | 249.240 | +3.1% | -0.2% |

Geometric mean of per-query branch/main ratios: 0.9876.


## Interpretation

The standard suites retained the same traversal and operator structure. Baseline repeats also reproduced the IC3 filter-order variation. Together with the baseline timing spread, these results show no measurable suite-wide regression or speedup.

