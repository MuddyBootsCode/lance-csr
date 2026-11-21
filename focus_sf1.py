"""Compare real SF1 Tag/Tagclass traversal with a typed, edge-distinct reference."""
import json, sys
from collections import defaultdict
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import lance
from lance_csr import CypherEngine, GraphConfig

root = Path(sys.argv[3])
out, run = Path(sys.argv[1]), sys.argv[2]
names = {"Tag":"Tag", "Tagclass":"Tagclass", "hasType":"tag_hasType_tagclass", "isSubclassOf":"tagclass_isSubclassOf_tagclass"}
ds = {k:lance.dataset(root / (v+".lance")) for k,v in names.items()}
tables = {k:v.to_table() for k,v in ds.items()}
cfg = (GraphConfig.builder().node_table("Tag","id").node_table("Tagclass","id")
       .rel_table("hasType","Tag","Tagclass","src","dst")
       .rel_table("isSubclassOf","Tagclass","Tagclass","src","dst").build())
adj = defaultdict(list)
for k,left in [("hasType","Tag"),("isSubclassOf","Tagclass")]:
    for i,(s,t) in enumerate(zip(tables[k]["src"].to_pylist(),tables[k]["dst"].to_pylist())):
        a,b = (left,s),("Tagclass",t)
        adj[a].append((b,(k,i)))
        if a != b:
            adj[b].append((a,(k,i)))
seeds = sorted((len(adj["Tagclass",i]),i) for i in tables["Tagclass"]["id"].to_pylist() if adj["Tagclass",i])
for mode,data in [("memory",tables),("lazy",ds)]:
    engine = CypherEngine(cfg,data,use_csr=True)
    for degree,seed in [seeds[0],seeds[-1]]:
        for bound in (2,3):
            expected = set()
            def visit(node,used):
                if used and node[0]=="Tag":
                    expected.add(node[1])
                if len(used)<bound:
                    for n,e in adj[node]:
                        if e not in used:
                            visit(n,used|{e})
            visit(("Tagclass",seed),set())
            expected = sorted(expected) or [None]
            base = (f"MATCH (s:Tagclass {{id: {seed}}}) OPTIONAL MATCH (s)-[:hasType|isSubclassOf*1..{bound}]-(q:Tag) "
                    "RETURN DISTINCT q.id AS id ORDER BY id")
            shapes = {"named":base.replace("OPTIONAL MATCH ","OPTIONAL MATCH p = ")}
            if run.startswith("branch"):
                shapes["unnamed"]=base
            samples={s:[] for s in shapes}
            for shape,q in shapes.items():
                assert engine.execute(q).column("id").to_pylist()==expected
                (out/f"sf1-plan-{run}-{mode}-{seed}-{bound}-{shape}.txt").write_text(engine.explain(q))
            for i in range(8):
                for shape in (list(shapes) if i%2==0 else list(reversed(shapes))):
                    before=perf_counter_ns()
                    result=engine.execute(shapes[shape])
                    samples[shape].append((perf_counter_ns()-before)/1e6)
                    assert result.column("id").to_pylist()==expected
            for shape,times in samples.items():
                print(json.dumps(dict(run=run,mode=mode,shape=shape,seed=seed,degree=degree,bound=bound,
                    rows=len(expected),non_null=sum(i is not None for i in expected),median_ms=median(times),samples_ms=times)),flush=True)

