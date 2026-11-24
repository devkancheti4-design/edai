"""Ask the edai brain about every window of every NASA telemetry channel (train and test), and save its answers.

    python3 -I scripts/run_brain.py <nasa_run> <data dir> <out dir> <framing> [workers]

framing
  seq    14 readings in a row: the first 12 given as a sequence, the brain asked the next two (aa_solve_sequence).
         A window ends at every reading from the 14th on.
  fill   the same 14 readings as edai's trend problems: 12 given as examples (x = 0, 10 .. 130), the 4th and 9th
         held back and asked (aa_solve_rule).
Readings are the channel's telemetry value (column 0, pre-scaled by NASA to about -1 .. 1) times 10,000, rounded.
The brain's answer depends only on the window, so each distinct window is asked once and its answer reused.

Saves <out dir>/<chan>_<split>.npz with, for every window (index = the window's last reading):
  by     0 CANNOT, 1 AM, 2 SPLITTER, 3 NET, 4 AM estimate
  ans    the two answers (0 for CANNOT), est the net's two estimates when it ran, check its self-check (thousandths)
  truth  the two real readings asked about, ns the time of the solve call
and <out dir>/run.json with the counts and times."""
import concurrent.futures as cf
import csv
import json
import os
import subprocess
import sys
import time

import numpy as np

RUN, DATA, OUT, FRAMING = sys.argv[1:5]
WORKERS = int(sys.argv[5]) if len(sys.argv) > 5 else 10
SCALE, W = 10000, 14
HOLD = (3, 8) if FRAMING == "fill" else (12, 13)
GIVEN = [i for i in range(W) if i not in HOLD]
BY = {"CANNOT": 0, "AM": 1, "SPLITTER": 2, "NET": 3, "AMEST": 4}
os.makedirs(OUT, exist_ok=True)


def windows(r):
    """r: whole-number readings -> (keys, truths), one per window ending at r[13], r[14], ..."""
    keys, truth = [], []
    for s in range(len(r) - W + 1):
        seg = r[s:s + W]
        keys.append(tuple(int(seg[i]) for i in GIVEN)); truth.append((int(seg[HOLD[0]]), int(seg[HOLD[1]])))
    return keys, truth


def line(i, k):
    if FRAMING == "seq":
        return f"{i} S 12 {' '.join(map(str, k))}\n"
    xs = [10 * j for j in GIVEN]
    return f"{i} R 12 {' '.join(map(str, xs))} {' '.join(map(str, k))} 2 {10 * HOLD[0]} {10 * HOLD[1]}\n"


def ask(uniq):
    """uniq: [key] -> [dict] answers in the same order"""
    chunks = [list(range(w, len(uniq), WORKERS)) for w in range(WORKERS)]

    def run(idx):
        if not idx:
            return {}
        text = "".join(line(i, uniq[i]) for i in idx)
        out = subprocess.run([RUN], input=text, capture_output=True, text=True, check=True).stdout
        res = {}
        for ln in out.splitlines():
            p = ln.split()
            d = dict(kv.split("=", 1) for kv in p[1:])
            if "error" in d:
                raise RuntimeError(ln)
            res[int(p[0])] = d
        return res

    res = {}
    with cf.ThreadPoolExecutor(WORKERS) as ex:
        for r in ex.map(run, chunks):
            res.update(r)
    return [res[i] for i in range(len(uniq))]


rows = list(csv.DictReader(open(f"{DATA}/labeled_anomalies.csv")))
chans = list(dict.fromkeys(r["chan_id"] for r in rows))          # P-2 is listed twice: one channel, asked once
series = {}
for c in chans:
    for split in ("train", "test"):
        v = np.load(f"{DATA}/{split}/{c}.npy", allow_pickle=False)[:, 0]
        series[(c, split)] = np.rint(v * SCALE).astype(np.int64)

all_keys, per = {}, {}
for (c, split), r in series.items():
    keys, truth = windows(r)
    per[(c, split)] = (keys, truth)
    for k in keys:
        all_keys.setdefault(k, len(all_keys))
uniq = list(all_keys)
n_win = sum(len(k) for k, _ in per.values())
print(f"{FRAMING}: {n_win} windows, {len(uniq)} distinct, {WORKERS} workers", flush=True)
t0 = time.time()
ans = ask(uniq)
wall = time.time() - t0
print(f"asked in {wall:.0f} s", flush=True)

summary = {"framing": FRAMING, "scale": SCALE, "windows": n_win, "distinct_windows": len(uniq),
           "wall_s": round(wall, 1), "workers": WORKERS, "channels": {}}
ns_all = np.array([int(a["ns"]) for a in ans], dtype=np.int64)
by_all = np.array([BY[a["by"]] for a in ans], dtype=np.int8)
summary["ns_per_call"] = {"median": int(np.median(ns_all)), "mean": int(ns_all.mean()), "p90": int(np.percentile(ns_all, 90)),
                          "max": int(ns_all.max())}
summary["ns_by_answer"] = {b: {"calls": int((by_all == v).sum()), "median_ns": int(np.median(ns_all[by_all == v]))}
                           for b, v in BY.items() if (by_all == v).any()}
for (c, split), (keys, truth) in per.items():
    ids = np.array([all_keys[k] for k in keys], dtype=np.int64)
    sub = [ans[i] for i in ids]
    by = np.array([BY[a["by"]] for a in sub], dtype=np.int8)
    a01 = np.array([[0, 0] if a["by"] == "CANNOT" else list(map(int, a["ans"].split(","))) for a in sub], dtype=np.int64).reshape(-1, 2)
    est = np.array([list(map(int, a["est"].split(","))) if "est" in a else [0, 0] for a in sub], dtype=np.int64).reshape(-1, 2)
    chk = np.array([int(a.get("check", -1)) for a in sub], dtype=np.int16)
    np.savez_compressed(f"{OUT}/{c}_{split}.npz", by=by, ans=a01, est=est, check=chk, truth=np.array(truth, dtype=np.int64).reshape(-1, 2),
                        ns=ns_all[ids], first=W - 1)
    cnt = {b: int((by == v).sum()) for b, v in BY.items() if (by == v).any()}
    summary["channels"].setdefault(c, {})[split] = cnt
json.dump(summary, open(f"{OUT}/run.json", "w"), indent=1)
print(json.dumps({k: summary[k] for k in ("windows", "distinct_windows", "wall_s", "ns_per_call", "ns_by_answer")}, indent=1))
