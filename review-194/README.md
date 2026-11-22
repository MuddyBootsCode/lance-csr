# PR 194 follow-up verification

Candidate `ca7214e2fd5f6578c146c15721651e6e1b3eae2a`. The review example compares this revision with the original PR head `c3e3a294d761dba724fc622c082eed2ceeb542e4`. The standard SF1 suites compare the candidate with the PR base `c9cd09659e7deb2516b88d8c6f65ead5f2b3a9b6`.

## Review example

X and Y both contain ID 1. Only Y has edges. The conflicting query previously returned IDs 2 and 3. Both candidate runs reject the label change during planning. When both clauses specify Y, every run returns IDs 2 and 3.

Each cell is median end-to-end latency in milliseconds over 100 executions of the valid query, after eight warm-ups. The wheels alternated before/after twice. The first revised run was slower in all four configurations. On the second pair, both revisions were within 0.03 ms for every configuration. These short timings do not establish a repeatable latency cost or speedup.

| CSR | Path | Original PR 1 | Revised PR 1 | Original PR 2 | Revised PR 2 |
|---|---|---:|---:|---:|---:|
| False | named | 0.373 | 0.468 | 0.388 | 0.385 |
| False | unnamed | 0.360 | 0.423 | 0.392 | 0.367 |
| True | named | 0.364 | 0.373 | 0.390 | 0.363 |
| True | unnamed | 0.354 | 0.375 | 0.357 | 0.356 |

The physical plan for each valid query matched across all four runs. The new check runs once when the planner reuses the starting variable. The traversal operator has no additional work per row or per edge.

[Review fixture and timing code](bound_probe.py) · [Raw samples](bound.jsonl) · [EXPLAIN output](plans)

## Standard SF1 benchmarks

[All 88 query and storage combinations](comparison.md) · [All 16 run logs and per-round timings](sf1) · [Load at run start](machine-load.jsonl)

| Suite | Storage | Change in geometric mean latency vs PR base |
|---|---|---:|
| graph-benchmark-ldbc | memory | +1.8% |
| graph-benchmark-ldbc | lazy | +1.2% |
| graph-benchmark-ldbc-complex | memory | -5.2% |
| graph-benchmark-ldbc-complex | lazy | -4.3% |

The [16 related queries](tests/edge-after.log) covered omitted labels, previously bound end nodes and matching-label controls, with named and unnamed paths. They produced the same results on both PR revisions.

### Standard physical plan comparison

Each cell lists query numbers with a different physical EXPLAIN after stripping table borders and padding. The base and original PR plans come from the [original published evidence](https://github.com/MuddyBootsCode/lance-csr/tree/547ef786a5b74f219bf6b7622acf48d59dd546d4/suite-plans).

| Suite | Storage | Revised vs base | Revised vs original PR |
|---|---|---|---|
| graph-benchmark-ldbc | memory | None | None |
| graph-benchmark-ldbc | lazy | None | None |
| graph-benchmark-ldbc-complex | memory | 3 | 3 |
| graph-benchmark-ldbc-complex | lazy | None | 3 |

For IC3, the only difference was the display order of two ANDed equality filters on Place. Previous same-wheel EXPLAINs also showed both orders.

## Follow-up on timing outliers

Every query initially more than 20% slower was repeated twice per build, alternating builds with the same runner settings. Times are means in milliseconds.

| Suite | Mode | Query | Initial change | Main 1 | Main 2 | Branch 1 | Branch 2 | Repeat change |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| graph-benchmark-ldbc | memory | 12 | +26.8% | 0.882 | 0.793 | 0.809 | 0.824 | -2.5% |
| graph-benchmark-ldbc | lazy | 1 | +34.6% | 1.296 | 1.280 | 1.206 | 1.235 | -5.2% |
| graph-benchmark-ldbc | lazy | 2 | +34.9% | 1.401 | 1.393 | 1.391 | 1.363 | -1.5% |
| graph-benchmark-ldbc | lazy | 3 | +30.9% | 0.808 | 0.807 | 0.829 | 0.792 | +0.4% |
| graph-benchmark-ldbc | lazy | 4 | +35.3% | 0.939 | 0.930 | 0.970 | 0.939 | +2.1% |
| graph-benchmark-ldbc | lazy | 5 | +29.3% | 2.150 | 2.028 | 2.127 | 1.932 | -2.8% |
| graph-benchmark-ldbc | lazy | 6 | +40.1% | 0.943 | 0.748 | 0.892 | 0.727 | -4.2% |
| graph-benchmark-ldbc-complex | memory | 13 | +20.2% | 1.283 | 1.275 | 1.288 | 1.439 | +6.6% |

## Feature workload and tests

For the high-degree, three-hop SF1 traversal, all builds returned 9,901 distinct tags. The two in-memory medians on the revised unnamed form were 6.68 and 6.73 ms, compared with 8.32 and 8.12 ms on the upstream named workaround. Lazy Lance medians were 8.24 and 7.94 ms on the revised unnamed form and 9.49 and 9.87 ms on the upstream named form. These numbers compare the entire feature with the workaround.

The chain-of-title fixture checked 584 distinct endpoints. SF1 tag-hierarchy runs checked endpoint IDs against an independent traversal. [Tree timing samples](focus.jsonl) · [SF1 timing samples](focus-sf1.jsonl) · [Standard suite physical plans for the candidate](suite-plans) · [Local test and lint logs](tests)

The release wheel SHA-256 values were

- PR base — `cba848bbdb694fd4def67798e31116c46fd2a7fc5f2f8c16ddabbc99820afec8`
- Original PR — `01c8fec8523f5124c7a24de2508d497739941cab2ee2849f3249f9573bd719af`
- Revised PR — `23196e1cf3b53d07d66bdf89ee6eb45652e85b6b4b61a492a22bc8cb838d91fc`
