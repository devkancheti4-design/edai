"""Time per check on this computer, one process alone: a fixed random sample of test windows.

    python3 -I scripts/bench.py <nasa_run> <data dir> <n> <out.json>

Takes n windows at random (seed 1) from all test windows of all channels, as the monitor meets them (repeats
included), asks each in one process, and reports the median and 90th-percentile time of
the solve call by who answered."""
import csv
import json
import random
import subprocess
import sys

import numpy as np

RUN, DATA, N, OUT = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
rows = list(csv.DictReader(open(f"{DATA}/labeled_anomalies.csv")))
chans = list(dict.fromkeys(r["chan_id"] for r in rows))
allw = []
for c in chans:
    r = np.rint(np.load(f"{DATA}/test/{c}.npy", allow_pickle=False)[:, 0] * 10000).astype(np.int64)
    allw += [(c, k, r[k:k + 12]) for k in range(len(r) - 13)]
rng = random.Random(1)
pick = rng.sample(range(len(allw)), N)
text = "".join(f"{i} S 12 {' '.join(map(str, allw[j][2]))}\n" for i, j in enumerate(pick))
res = {}
for name, cmd in (("brain", [RUN]),):
    out = subprocess.run(cmd, input=text, capture_output=True, text=True, check=True).stdout.splitlines()
    by = {}
    for ln in out:
        d = dict(kv.split("=", 1) for kv in ln.split()[1:])
        by.setdefault(d["by"], []).append(int(d["ns"]))
    allns = [v for vs in by.values() for v in vs]
    res[name] = {"windows": len(out), "median_ms_all": round(float(np.median(allns)) / 1e6, 3), "mean_ms_all": round(float(np.mean(allns)) / 1e6, 3),
                 "by": {b: {"n": len(v), "median_ms": round(float(np.median(v)) / 1e6, 4), "p90_ms": round(float(np.percentile(v, 90)) / 1e6, 4)}
                        for b, v in sorted(by.items())}}
json.dump({"sample": N, "seed": 1, **res}, open(OUT, "w"), indent=1)
for name, d in res.items():
    print(f"{name}: {d['windows']} windows, median {d['median_ms_all']} ms, mean {d['mean_ms_all']} ms; " +
          "; ".join(f"{b} {v['n']} median {v['median_ms']} ms" for b, v in d["by"].items()))
