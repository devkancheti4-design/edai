"""Extra: the paper's own error thresholding (nonparametric, with pruning, its published settings) applied to the edai
brain's forecasts instead of the LSTM's.  No setting is tuned and no label is used before the score.

    python3 -I scripts/paper_threshold.py <data dir> <answers dir> <out.json>
    python3 -I scripts/paper_threshold.py <data dir> --lstm <y_hat dir> <out.json> [c2]

The second form is the check of this port: the same steps on the paper's own LSTM forecasts (telemanom's stored
y_hat of its 2018-05-19 run; forecast i is of reading i + 250).  With c2, telemanom's exception for channel C-2 is
made too, as its code does.

The forecast of reading t is the brain's first answer from the 12 readings before it (its estimate from the net
where it said CANNOT).  The steps follow telemanom/errors.py (Hundman et al., (c) 2018 Caltech, BSD-style licence)
one by one: error e = |forecast - reading|; EWMA smoothing with span 70 x 30 x 0.05 = 105; the first 250 smoothed
errors set to the mean of the first 500; windows of 30 batches of 70 errors moving one batch at a time; in each, the
threshold z in 2.5 .. 11.5 that best trades the drop in mean and spread against the number of anomalous points and
sequences (each point widened by 99), for the errors and for the errors turned upside down; the size guards (errors
above 5% of the window's 5-95% range and above 0.05, spread above 5% of the readings' spread); new points only from
each window's last batch (the first window ignores its first 500, 250 or 0 errors by length); pruning with p = 0.13;
each point widened by 100; touching points joined.  One change: telemanom skips the start-up smoothing for channel C-2
because its anomaly comes early; that exception comes from knowing the label, so it is not made here."""
import csv
import importlib.util
import json
import os
import sys

import numpy as np

spec = importlib.util.spec_from_file_location("detect_lib", os.path.join(os.path.dirname(os.path.abspath(__file__)), "detect_lib.py"))
lib = importlib.util.module_from_spec(spec); spec.loader.exec_module(lib)
LSTM = len(sys.argv) > 3 and sys.argv[2] == "--lstm"
if LSTM:
    DATA, YHAT, OUT = sys.argv[1], sys.argv[3], sys.argv[4]
    C2 = len(sys.argv) > 5 and sys.argv[5] == "c2"
else:
    DATA, ANS, OUT = sys.argv[1:4]
    C2 = False
BATCH, WINDOW, SMOOTH, BUFFER, P, L_S, SD_LIM = 70, 30, 0.05, 100, 0.13, 250, 12.0
SCALE = 10000.0
OFFSET = 250 if LSTM else 12    # the first forecast is of reading 12 (window 0 gives readings 0..11); the LSTM's of 250


def ewm_mean(x, span):
    """pandas' DataFrame.ewm(span).mean() with adjust=True"""
    a = 2.0 / (span + 1.0)
    out = np.empty(len(x)); num = den = 0.0
    for i, v in enumerate(x):
        num = v + (1 - a) * num; den = 1.0 + (1 - a) * den
        out[i] = num / den
    return out


def groups(idx):
    """consecutive runs of sorted unique indices -> [(first, last)], single points left out"""
    if len(idx) == 0:
        return []
    idx = np.asarray(idx, dtype=np.int64)
    br = np.nonzero(np.diff(idx) != 1)[0]
    starts = np.concatenate([[0], br + 1]); ends = np.concatenate([br, [len(idx) - 1]])
    return [(int(idx[s]), int(idx[e])) for s, e in zip(starts, ends) if idx[s] != idx[e]]


def widen(i_anom, n, lo, hi):
    if len(i_anom) == 0:
        return np.array([], dtype=np.int64)
    b = np.arange(lo, hi)
    w = np.concatenate([i_anom, (i_anom[:, None] + b).ravel(), (i_anom[:, None] - b).ravel()])
    return np.unique(w[(w >= 0) & (w < n)])


class Window:
    def __init__(self, e_s_all, y_all, start, end, num, n_total):
        self.e_s = e_s_all[start:end]; self.num = num
        self.mean = float(np.mean(self.e_s)); self.sd = float(np.std(self.e_s))
        self.e_s_inv = self.mean + (self.mean - self.e_s)
        self.eps = {False: self.mean + SD_LIM * self.sd, True: self.mean + SD_LIM * self.sd}
        y = y_all[start:end]
        self.sd_values = float(np.std(y))
        hi, lo = np.percentile(y, [95, 5]); self.inter_range = float(hi - lo)
        self.ignore = 2 * L_S if n_total >= 2500 else (L_S if n_total >= 1800 else 0)
        self.i_anom = {False: np.array([], dtype=np.int64), True: np.array([], dtype=np.int64)}
        self.E_seq = {False: [], True: []}
        self.non_anom_max = {False: -1e6, True: -1e6}

    def find_epsilon(self, inv):
        e_s = self.e_s_inv if inv else self.e_s
        best = -1e7
        for z in np.arange(2.5, SD_LIM, 0.5):
            eps = self.mean + self.sd * z
            pruned = e_s[e_s < eps]
            i_anom = widen(np.nonzero(e_s >= eps)[0], len(e_s), 1, BUFFER)
            if len(i_anom) > 0:
                E_seq = groups(i_anom)
                mpd = (self.mean - np.mean(pruned)) / self.mean
                spd = (self.sd - np.std(pruned)) / self.sd
                score = (mpd + spd) / (len(E_seq) ** 2 + len(i_anom))
                if score >= best and len(E_seq) <= 5 and len(i_anom) < len(e_s) * 0.5:
                    best = score; self.eps[inv] = self.mean + z * self.sd

    def compare(self, all_i_anom, inv):
        e_s = self.e_s_inv if inv else self.e_s
        eps = self.eps[inv]
        if not (self.sd > 0.05 * self.sd_values or max(self.e_s) > 0.05 * self.inter_range) or not max(self.e_s) > 0.05:
            return
        i_anom = np.nonzero((e_s >= eps) & (e_s > 0.05 * self.inter_range))[0]
        if len(i_anom) == 0:
            return
        i_anom = widen(i_anom, len(e_s), 1, BUFFER + 1)
        i_anom = i_anom[i_anom >= self.ignore] if self.num == 0 else i_anom[i_anom >= len(e_s) - BATCH]
        pos = self.num * BATCH
        cand = np.setdiff1d(np.arange(len(e_s)) + pos, np.append(all_i_anom, i_anom + pos)) - pos
        self.non_anom_max[inv] = float(np.max(e_s[np.unique(cand)]))
        self.i_anom[inv] = i_anom; self.E_seq[inv] = groups(i_anom)

    def prune(self, inv):
        E_seq, e_s = self.E_seq[inv], (self.e_s_inv if inv else self.e_s)
        if len(E_seq) == 0:
            return
        mx = np.array([max(e_s[a:b + 1]) for a, b in E_seq])
        srt = np.append(np.sort(mx)[::-1], [self.non_anom_max[inv]])
        remove = []
        for i in range(len(srt) - 1):
            if (srt[i] - srt[i + 1]) / srt[i] < P:
                remove += list(np.nonzero(mx == srt[i])[0])
            else:
                remove = []
        keep = [s for j, s in enumerate(E_seq) if j not in set(remove)]
        if not keep:
            self.i_anom[inv] = np.array([], dtype=np.int64); return
        k = np.concatenate([np.arange(a, b + 1) for a, b in keep])
        self.i_anom[inv] = self.i_anom[inv][np.isin(self.i_anom[inv], k)]


def detect(e, y, skip_start=False):
    n = len(e)
    e_s = ewm_mean(e, int(BATCH * WINDOW * SMOOTH))
    if not skip_start:
        e_s[:L_S] = np.mean(e_s[:L_S * 2])
    window_size = WINDOW
    n_windows = int((n - BATCH * window_size) / BATCH)
    while n_windows < 0:
        window_size -= 1
        n_windows = int((n - BATCH * window_size) / BATCH)
    all_i = np.array([], dtype=np.int64)
    for i in range(n_windows + 1):
        prior = i * BATCH
        end = n if i == n_windows else window_size * BATCH + i * BATCH
        w = Window(e_s, y, prior, end, i, n)
        for inv in (False, True):
            w.find_epsilon(inv)
        for inv in (False, True):
            w.compare(all_i, inv)
        if len(w.i_anom[False]) == 0 and len(w.i_anom[True]) == 0:
            continue
        for inv in (False, True):
            w.prune(inv)
        if len(w.i_anom[False]) == 0 and len(w.i_anom[True]) == 0:
            continue
        both = np.unique(np.append(w.i_anom[False], w.i_anom[True])).astype(np.int64)
        all_i = np.append(all_i, both + prior)
    return [(a + OFFSET, b + OFFSET) for a, b in groups(np.unique(all_i))]


rows = list(csv.DictReader(open(f"{DATA}/labeled_anomalies.csv")))
preds, info = {}, {}
for c in dict.fromkeys(r["chan_id"] for r in rows):
    if LSTM:
        fc = np.load(f"{YHAT}/{c}.npy", allow_pickle=False)
        y = np.load(f"{DATA}/test/{c}.npy", allow_pickle=False)[OFFSET:OFFSET + len(fc), 0]
    else:
        te = lib.load(ANS, c, "test")
        fc = np.where(te["by"] != 0, te["ans"][:, 0], te["est"][:, 0]) / SCALE    # forecast of reading k + 12
        y = te["truth"][:, 0] / SCALE
    e = np.abs(fc - y)
    preds[c] = detect(e, y, skip_start=C2 and c == "C-2")
    info[c] = {"predicted": preds[c], "mean_error": round(float(e.mean()), 5)}
tot = {"SMAP": [0, 0, 0], "MSL": [0, 0, 0]}
per_row = []
for r in rows:
    tp, fp, fn, _ = lib.evaluate(preds[r["chan_id"]], json.loads(r["anomaly_sequences"]))
    per_row.append((r["chan_id"], tp, fp, fn))
    for j, v in enumerate((tp, fp, fn)):
        tot[r["spacecraft"]][j] += v
score = {k: lib.prf(*v) for k, v in tot.items()}
score["Total"] = lib.prf(*[tot["SMAP"][j] + tot["MSL"][j] for j in range(3)])
json.dump({"score": score, "channels": info, "rows": per_row}, open(OUT, "w"), indent=1)
print("the paper's thresholding on " + ("the paper's LSTM forecasts" + (" (C-2 exception made)" if C2 else "") if LSTM else "the brain's forecasts") + ":")
for k in ("SMAP", "MSL", "Total"):
    s = score[k]
    print(f"  {k:6s} TP {s['tp']:3d} FP {s['fp']:3d} FN {s['fn']:3d}  precision {100 * s['precision']:5.1f}%  recall {100 * s['recall']:5.1f}%  F0.5 {s['f05']:.3f}")
