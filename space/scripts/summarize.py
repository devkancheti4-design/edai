"""Who answered, how well and how fast: the brain's answers on every NASA window, by spacecraft and by part.

    python3 -I scripts/summarize.py <data dir> <answers dir> <out.json>

For train and test of SMAP and MSL: windows, the share answered by each of AM, SPLITTER, NET, AM estimate and CANNOT,
, the median and 90th-percentile miss of the answered windows (in NASA's -1 .. 1 units), the exact answers'
miss, and the channels where AM answered at least once.  Times: the solve call's own time, per distinct window."""
import csv
import json
import sys

import numpy as np

DATA, ANS, OUT = sys.argv[1:4]
NAMES = ["CANNOT", "AM", "SPLITTER", "NET", "AMEST"]
SCALE = 10000.0
rows = list(csv.DictReader(open(f"{DATA}/labeled_anomalies.csv")))
craft = {r["chan_id"]: r["spacecraft"] for r in rows}
chans = list(dict.fromkeys(r["chan_id"] for r in rows))
rep = {}
for sc in ("SMAP", "MSL", "both"):
    for split in ("train", "test"):
        cs = [c for c in chans if sc == "both" or craft[c] == sc]
        by_all, miss_all, exact_miss, am_chans = [], [], [], []
        for c in cs:
            z = np.load(f"{ANS}/{c}_{split}.npz", allow_pickle=False)
            by = z["by"]; miss = np.abs(z["ans"] - z["truth"]).max(axis=1) / SCALE
            by_all.append(by); miss_all.append(miss[by != 0])
            ex = (by == 1) | (by == 2)
            exact_miss.append(miss[ex])
            if (by == 1).any():
                am_chans.append(c)
        by = np.concatenate(by_all); m = np.concatenate(miss_all); em = np.concatenate(exact_miss)
        n = len(by)
        d = {"channels": len(cs), "windows": n,
             "share": {NAMES[v]: round(float((by == v).mean()), 4) for v in range(5) if (by == v).any()},
             "count": {NAMES[v]: int((by == v).sum()) for v in range(5) if (by == v).any()},
             "answered_share": round(float((by != 0).mean()), 4),
             "miss_median": round(float(np.median(m)), 5) if len(m) else None,
             "miss_p90": round(float(np.percentile(m, 90)), 5) if len(m) else None,
             "exact_windows": int(len(em)), "exact_miss_zero_share": round(float((em == 0).mean()), 4) if len(em) else None,
             "exact_miss_p90": round(float(np.percentile(em, 90)), 5) if len(em) else None,
             "channels_with_am": len(am_chans)}
        rep[f"{sc}/{split}"] = d
json.dump(rep, open(OUT, "w"), indent=1)
for k, d in rep.items():
    sh = "  ".join(f"{a} {100 * b:.1f}%" for a, b in d["share"].items())
    print(f"{k:11s} {d['windows']:7d} windows  {sh}")
    print(f"{'':11s} answered {100 * d['answered_share']:.1f}%, miss median {d['miss_median']} p90 {d['miss_p90']}; exact {d['exact_windows']} "
          f"(miss 0 in {d['exact_miss_zero_share']}), AM on {d['channels_with_am']} of {d['channels']} channels")
