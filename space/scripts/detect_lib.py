"""Shared pieces of the NASA scoring: the brain's saved answers, CANNOT runs, telemanom's grouping and scoring."""
import numpy as np

BUFFER = 100                              # telemanom's error_buffer: each alarm widened by 100 readings each side


def load(ans_dir, c, split):
    z = np.load(f"{ans_dir}/{c}_{split}.npz", allow_pickle=False)
    d = {k: z[k] for k in ("by", "ans", "est", "truth")}
    d["first"] = int(z["first"])
    d["miss"] = np.where(d["by"] != 0, np.abs(d["ans"] - d["truth"]).max(axis=1), -1)
    return d


def runs(mask):
    """the length of the run of True each element is in, counted up to and including it (0 where False)"""
    mask = np.asarray(mask, dtype=bool)
    idx = np.arange(len(mask))
    last_false = np.maximum.accumulate(np.where(~mask, idx, -1))
    return np.where(mask, idx - last_false, 0)


def sequences(times, n, buffer=BUFFER):
    """alarm times (indices of readings) -> predicted sequences, widened and joined as telemanom does"""
    if len(times) == 0:
        return []
    marked = np.zeros(n + 1, dtype=bool)
    for t in times:
        marked[max(0, t - buffer):min(n, t + buffer + 1)] = True
    d = np.diff(np.concatenate([[0], marked.astype(np.int8)]))
    starts, ends = np.nonzero(d == 1)[0], np.nonzero(d == -1)[0] - 1
    return [(int(a), int(b)) for a, b in zip(starts, ends) if a != b]


def evaluate(pred, labelled):
    """telemanom's evaluate_sequences: (tp, fp, fn, the labelled sequences found)"""
    tp = fp = 0; matched = []
    for a, b in pred:
        hits = [i for i, (la, lb) in enumerate(labelled) if not (b < la or a > lb)]
        if hits:
            if hits[0] not in matched:
                matched.append(hits[0]); tp += 1
        else:
            fp += 1
    return tp, fp, len(labelled) - len(matched), matched


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 1.25 * p * r / (0.25 * p + r) if p + r else 0.0
    return {"tp": tp, "fp": fp, "fn": fn, "precision": round(p, 4), "recall": round(r, 4), "f05": round(f, 4)}
