"""The edai health monitor on NASA's SMAP and MSL telemetry, scored as the paper scores it.

    python3 -I scripts/detect.py <data dir> <answers dir> <out.json>

The protocol's detector (PROTOCOL.md): an alarm when the brain misses by more than it ever did on the channel's
training data, or says CANNOT for longer than it ever did there.

Every setting comes from the channel's own training data; the labels are used only for the score at the end."""
import csv
import importlib.util
import json
import os
import sys

import numpy as np

spec = importlib.util.spec_from_file_location("detect_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "detect_lib.py"))
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)

DATA, ANS, OUT = sys.argv[1:4]
KIND = "brain"
CANNOT = 0


def profile(tr):
    answered = tr["by"] != CANNOT
    return {"worst_miss": int(tr["miss"][answered].max()) if answered.any() else None,
            "longest_cannot_run": int(lib.runs(tr["by"] == CANNOT).max(initial=0)),
            "answered_share": round(float(answered.mean()), 4)}


def alarms(te, p):
    answered = te["by"] != CANNOT
    miss = answered & (te["miss"] > p["worst_miss"]) if p["worst_miss"] is not None else np.zeros(len(answered), bool)
    cannot = lib.runs(te["by"] == CANNOT) > p["longest_cannot_run"]
    return miss | cannot, miss, cannot


rows = list(csv.DictReader(open(f"{DATA}/labeled_anomalies.csv")))
per_chan, preds = {}, {}
for c in dict.fromkeys(r["chan_id"] for r in rows):
    tr, te = lib.load(ANS, c, "train"), lib.load(ANS, c, "test")
    p = profile(tr)
    flag, miss, cannot = alarms(te, p)
    times = np.nonzero(flag)[0] + te["first"]           # window k ends at reading k + 13
    preds[c] = lib.sequences(times, len(te["by"]) + te["first"])
    per_chan[c] = dict(profile=p, test_windows=int(len(te["by"])), alarms=int(flag.sum()), predicted=preds[c],
                       miss_alarms=int(miss.sum()), cannot_alarms=int(cannot.sum()))

tot = {"SMAP": [0, 0, 0], "MSL": [0, 0, 0]}
row_results = []
for i, r in enumerate(rows):
    lab = json.loads(r["anomaly_sequences"])
    tp, fp, fn, matched = lib.evaluate(preds[r["chan_id"]], lab)
    for j, v in enumerate((tp, fp, fn)):
        tot[r["spacecraft"]][j] += v
    row_results.append(dict(row=i, chan=r["chan_id"], spacecraft=r["spacecraft"], labelled=lab,
                            found=[lab[m] for m in matched], tp=tp, fp=fp, fn=fn))
score = {k: lib.prf(*v) for k, v in tot.items()}
score["Total"] = lib.prf(*[tot["SMAP"][j] + tot["MSL"][j] for j in range(3)])
json.dump({"kind": KIND, "answers": ANS, "buffer": lib.BUFFER, "score": score, "channels": per_chan, "rows": row_results},
          open(OUT, "w"), indent=1)
print(f"{KIND} detector on {ANS}:")
print(f"  {'':6s} {'TP':>4s} {'FP':>4s} {'FN':>4s} {'precision':>9s} {'recall':>7s} {'F0.5':>6s}")
for k in ("SMAP", "MSL", "Total"):
    s = score[k]
    print(f"  {k:6s} {s['tp']:4d} {s['fp']:4d} {s['fn']:4d} {100 * s['precision']:8.1f}% {100 * s['recall']:6.1f}% {s['f05']:6.3f}")
