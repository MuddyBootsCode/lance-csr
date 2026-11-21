"""Time the bounded OPTIONAL MATCH from issue 186 on a deterministic 8-ary tree."""
import json
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import sys
import lance
import pyarrow as pa
from lance_csr import CypherEngine, GraphConfig

run, directory = sys.argv[1], Path(sys.argv[2])
kinds = ["SUCCEEDED_BY", "DECEDENT_OF", "DISTRIBUTED_TO"]
edges = {kind: ([], []) for kind in kinds}
start, stop = 0, 1
for depth in range(4):
    for parent in range(start, stop):
        for child in range(8 * parent + 1, 8 * parent + 9):
            src, dst = edges[kinds[(parent + child) % 3]]
            a, b = (parent, child) if depth % 2 else (child, parent)
            src.append(a)
            dst.append(b)
    start, stop = stop, 8 * stop + 1
cfg = GraphConfig.builder().node_table("Entity", "id")
tables = {"Entity": pa.table({"id": list(range(stop)), "name": [f"party-{i}" for i in range(stop)]})}
for kind, (src, dst) in edges.items():
    cfg = cfg.rel_table(kind, "Entity", "Entity", "src", "dst")
    tables[kind] = pa.table({"src": src, "dst": dst})
cfg = cfg.build()
disk = directory / "focus-data"
disk.mkdir(exist_ok=True)
datasets = {}
for name, table in tables.items():
    path = disk / (name + ".lance")
    datasets[name] = lance.dataset(path) if path.exists() else lance.write_dataset(table, path)
query = ("MATCH (s:Entity {id: 0}) OPTIONAL MATCH (s)-[:SUCCEEDED_BY|DECEDENT_OF|DISTRIBUTED_TO*1..3]-(q:Entity) "
         "RETURN DISTINCT q.id AS id ORDER BY id")
expected = list(range(1, 585))
for mode, data in [("memory", tables), ("lazy", datasets)]:
    for csr in [False, True]:
        engine = CypherEngine(cfg, data, use_csr=csr)
        samples = {}
        for shape in ["named", "unnamed"]:
            q = query.replace("OPTIONAL MATCH ", "OPTIONAL MATCH p = ") if shape == "named" else query
            if shape == "unnamed" and run.startswith("main"):
                try:
                    engine.execute(q)
                except NotImplementedError as exc:
                    assert "alternation" in str(exc)
                    continue
                raise AssertionError("baseline unexpectedly supports unnamed query")
            assert engine.execute(q).column("id").to_pylist() == expected
            (directory / f"plan-{run}-{mode}-{int(csr)}-{shape}.txt").write_text(engine.explain(q))
            if run.endswith("1") and csr:
                (directory / f"profile-{run}-{mode}-{shape}.txt").write_text(engine.explain(q, analyze=True))
            samples[shape] = []
        for i in range(12):
            order = list(samples) if i % 2 == 0 else list(reversed(samples))
            for shape in order:
                q = query.replace("OPTIONAL MATCH ", "OPTIONAL MATCH p = ") if shape == "named" else query
                before = perf_counter_ns()
                result = engine.execute(q)
                duration = (perf_counter_ns() - before) / 1e6
                assert result.column("id").to_pylist() == expected
                samples[shape].append(duration)
        for shape, times in samples.items():
            print(json.dumps(dict(run=run, mode=mode, csr=csr, shape=shape, nodes=stop, edges=stop-1, results=len(expected), median_ms=median(times), samples_ms=times)), flush=True)

