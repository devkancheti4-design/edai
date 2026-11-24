"""Recall by the paper's anomaly class (point / contextual), as in its Table 4, for saved detector results.

    python3 -I scripts/by_class.py <data dir> <detector json> [...]"""
import csv, importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location("detect_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "detect_lib.py"))
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)
rows = list(csv.DictReader(open(f"{sys.argv[1]}/labeled_anomalies.csv")))
for f in sys.argv[2:]:
    d = json.load(open(f)); ch = d["channels"]
    cnt = {}
    for r in rows:
        lab = json.loads(r["anomaly_sequences"]); cls = [x.strip() for x in r["class"].strip("[]").split(",")]
        _, _, _, matched = lib.evaluate([tuple(p) for p in ch[r["chan_id"]]["predicted"]], lab)
        for i, c in enumerate(cls):
            for k in (r["spacecraft"], "Total"):
                n, h = cnt.get((k, c), (0, 0)); cnt[(k, c)] = (n + 1, h + (i in matched))
    print(os.path.basename(f) + ":  " + "  ".join(f"{k} {c} {h}/{n} = {100 * h / n:.1f}%" for (k, c), (n, h) in sorted(cnt.items())))
