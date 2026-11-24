"""Extra (after the protocol's score was known): the detector with three settings, tuned on SMAP's labels only and then
scored once on MSL, which the tuning never saw.

    python3 -I scripts/tune.py <data dir> <answers dir> <out.json>

Settings (each channel's figures still come from its own training data):
  floor   a miss must also be at least this share of NASA's full scale (-1 .. 1, i.e. 20,000 units)
  margin  a miss must be more than margin x the worst miss on the training data
  cannot  CANNOT alarms off, or on when the run is longer than k x the longest training run
The grid is searched for the best F0.5 on SMAP; ties go to the simpler setting (smaller floor, smaller margin)."""
import csv
import itertools
import json
import sys

import numpy as np

import importlib.util
import os
spec = importlib.util.spec_from_file_location("detect_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "detect_lib.py"))
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)
DATA, ANS, OUT = sys.argv[1:4]

FULL = 20000
rows = list(csv.DictReader(open(f"{DATA}/labeled_anomalies.csv")))
chans = list(dict.fromkeys(r["chan_id"] for r in rows))
craft = {r["chan_id"]: r["spacecraft"] for r in rows}
pre = {}
for c in chans:
    tr, te = lib.load(ANS, c, "train"), lib.load(ANS, c, "test")
    ans_tr = tr["by"] != 0
    pre[c] = dict(worst=int(tr["miss"][ans_tr].max()) if ans_tr.any() else None,
                  longest=int(lib.runs(tr["by"] == 0).max(initial=0)),
                  miss=te["miss"], run=lib.runs(te["by"] == 0), first=te["first"], n=len(te["by"]) + te["first"])


def score(floor, margin, cannot, crafts):
    tot = [0, 0, 0]; preds = {}
    for c in chans:
        if craft[c] not in crafts:
            continue
        p = pre[c]
        lim = None if p["worst"] is None else max(margin * p["worst"], floor * FULL)
        flag = (p["miss"] > lim) if lim is not None else np.zeros(len(p["miss"]), bool)
        if cannot:
            flag = flag | (p["run"] > cannot * p["longest"])
        preds[c] = lib.sequences(np.nonzero(flag)[0] + p["first"], p["n"])
    for r in rows:
        if r["spacecraft"] in crafts:
            tp, fp, fn, _ = lib.evaluate(preds[r["chan_id"]], json.loads(r["anomaly_sequences"]))
            tot[0] += tp; tot[1] += fp; tot[2] += fn
    return lib.prf(*tot)


grid = list(itertools.product([0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2], [1, 1.5, 2, 3, 5], [0, 1, 2, 4]))
res = []
for f, m, k in grid:
    s = score(f, m, k, {"SMAP"})
    res.append((s["f05"], -f, -m, -k if k else 0, (f, m, k), s))
res.sort(key=lambda x: (x[0], x[1], x[2], x[3]), reverse=True)
best = res[0][4]
out = {"grid": len(grid), "best_on_smap": dict(zip(("floor", "margin", "cannot"), best)),
       "SMAP_tuned_on": res[0][5], "MSL_held_out": score(*best, {"MSL"}), "Total": score(*best, {"SMAP", "MSL"}),
       "protocol_setting_for_reference": {"SMAP": score(0, 1, 1, {"SMAP"}), "MSL": score(0, 1, 1, {"MSL"})},
       "top10_on_smap": [dict(setting=dict(zip(("floor", "margin", "cannot"), r[4])), smap=r[5]) for r in res[:10]]}
json.dump(out, open(OUT, "w"), indent=1)
print(f"searched {len(grid)} settings on SMAP; best: floor {best[0]}, margin {best[1]}, cannot {best[2]}")
for k in ("SMAP_tuned_on", "MSL_held_out", "Total"):
    s = out[k]
    print(f"  {k:14s} TP {s['tp']:3d} FP {s['fp']:3d} FN {s['fn']:3d}  precision {100 * s['precision']:5.1f}%  recall {100 * s['recall']:5.1f}%  F0.5 {s['f05']:.3f}")
