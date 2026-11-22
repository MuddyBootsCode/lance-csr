import pyarrow as pa
from lance_csr import CypherEngine,GraphConfig
cfg=(GraphConfig.builder().node_table("X","id").node_table("Y","id").rel_table("A","Y","Y","src","dst").rel_table("B","Y","Y","src","dst").build())
eng=CypherEngine(cfg, {"X":pa.table({"id":[1]}),"Y":pa.table({"id":[1,2,3]}),"A":pa.table({"src":[1],"dst":[2]}),"B":pa.table({"src":[3],"dst":[2]})})
for binding in ("","p = "):
    for src in ("(s:X {id:1})","(s:Y {id:1})","(q:X {id:1})","(q:Y {id:1})"):
        for pattern in (("(s)","(q:Y)"),("(s)","(q)")) if src.startswith("(s") else (("(s:Y)","(q)"),("(s:Y)","(q:Y)")):
            query=f"MATCH {src} MATCH {binding}{pattern[0]}-[:A|B*1..2]-{pattern[1]} RETURN s.id AS s, q.id AS q"
            try: result=eng.execute(query).to_pylist()
            except Exception as exc: result=str(exc).splitlines()[0]
            print(query, result)
