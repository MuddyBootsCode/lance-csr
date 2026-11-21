# Issue 186 verification

The measured candidate is [c3e3a29](https://github.com/MuddyBootsCode/lance-csr/commit/c3e3a294d761dba724fc622c082eed2ceeb542e4) against upstream `c9cd09659e7deb2516b88d8c6f65ead5f2b3a9b6`. The [patch](branch.patch) SHA-256 is `b521f96a426de834af817367672c36047d36735f00905e9db39ad89bcc031601`.

- [Performance report](performance.md) with the named and unnamed comparisons, timing distributions and suite results.
- [Test logs](tests) with Rust and Python results, lint and docs checks, and the issue reproduction on both builds.
- [Standard benchmark runs](sf1) with all 16 logs and per-round timings. JSON measurements are in seconds and report tables are in milliseconds.
- [Standard physical plans](suite-plans) for each wheel and storage mode, including same-build IC3 repeats. [Focused plans and execution profiles](plans) cover the tree and SF1 tag workloads.
- [Tree samples](focus.jsonl), [SF1 tag samples](focus-sf1.jsonl) and [machine load at run start](machine-load.jsonl).

Build both release wheels and prepare the datasets using the [upstream harness](https://github.com/hyperdimensionalcomputingai/lance-csr/blob/c9cd09659e7deb2516b88d8c6f65ead5f2b3a9b6/CONTRIBUTING.md#build-the-benchmark-harness). The report identifies the benchmark runner revisions. For the focused workloads, create an output directory and run these commands in the runner environment with the corresponding wheel:

```sh
python focus.py main1 OUT
python focus_sf1.py OUT main1 PATH_TO_COMPLEX_GRAPH_LANCE
```

Repeat with run labels `branch1`, `main2` and `branch2`. The scripts check endpoint IDs independently on each run. Local paths have been shortened in the transcripts. The JSON exports retain per-round timings and omit machine-identifying metadata.
