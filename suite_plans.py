import os, sys, contextlib, io
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import query
out, variant = Path(sys.argv[1]), sys.argv[2]
suite = Path.cwd().parent.name
mode = os.environ["LANCE_CSR_MODE"]
class Captured(Exception):
    pass
class Capture:
    def execute(self, *args):
        raise Captured(args)
if suite.endswith("-complex"):
    count = 14
    engine, target, module = query.engine(), Capture(), query
else:
    count = 30
    module = query.q
    cfg = module.build_config()
    datasets = module.load_datasets(module.GRAPH_ROOT)
    engine = module.CypherEngine(cfg, datasets)
    target = module.QueryContext(cfg, datasets, Capture())
folder = out / "suite-plans" / suite / mode / variant
folder.mkdir(parents=True, exist_ok=True)
for n in ([int(sys.argv[3])] if len(sys.argv) > 3 else range(1, count + 1)):
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            getattr(module, f"run_query{n}")(target)
    except Captured as cap:
        plan = engine.explain(*cap.args[0])
        (folder / f"{n}.txt").write_text(plan.split("physical_plan", 1)[1])
    else:
        raise RuntimeError(f"query {n} did not reach engine")

