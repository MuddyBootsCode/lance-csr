"""Compare the valid and conflicting label cases from the review."""
import json
import sys
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import pyarrow as pa
from lance_csr import CypherEngine, GraphConfig

out, run = Path(sys.argv[1]), sys.argv[2]
cfg = (GraphConfig.builder().node_table("X","id").node_table("Y","id")
       .rel_table("A","Y","Y","src","dst").rel_table("B","Y","Y","src","dst").build())
tables = {"X":pa.table({"id":[1]}), "Y":pa.table({"id":[1,2,3]}),
          "A":pa.table({"src":[1],"dst":[2]}), "B":pa.table({"src":[3],"dst":[2]})}
for csr in (False, True):
    engine = CypherEngine(cfg, tables, use_csr=csr)
    for shape, binding in (("named","p = "),("unnamed","")):
        query = "MATCH (s:Y {id:1}) MATCH " + binding + "(s:Y)-[:A|B*1..2]-(q:Y) RETURN q.id"
        try:
            invalid = sorted(engine.execute(query.replace("(s:Y {", "(s:X {")).column(0).to_pylist())
            assert run.startswith("before") and invalid == [2,3]
        except ValueError as exc:
            assert run.startswith("after") and "already has label 'X', cannot redefine as 'Y'" in str(exc)
            invalid = "rejected"
        (out/f"bound-{run}-{int(csr)}-{shape}.txt").write_text(engine.explain(query))
        for _ in range(8):
            assert sorted(engine.execute(query).column(0).to_pylist()) == [2,3]
        samples = []
        for _ in range(100):
            start = perf_counter_ns()
            result = engine.execute(query)
            samples.append((perf_counter_ns()-start)/1e6)
            assert sorted(result.column(0).to_pylist()) == [2,3]
        print(json.dumps(dict(run=run,csr=csr,shape=shape,invalid=invalid,valid=[2,3],
                              median_ms=median(samples),samples_ms=samples)), flush=True)
