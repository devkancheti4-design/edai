# Space: edai on NASA spacecraft telemetry

The same brain, unchanged (the library in `brain/`, version 1.2), watching NASA JPL's public spacecraft telemetry:
the SMAP satellite and the Curiosity rover (MSL), the benchmark of Hundman et al., KDD 2018 ("telemanom"): 82
channels and 105 labelled anomalies. Every window of every channel is one question to the brain: here are 12 readings
in a row, what are the next two?

**In short** (every number is below, with how it was made):

- **AM answers on real spacecraft telemetry.** AM, the exact-rule part, answers 39.5% of all test windows (SMAP
  42.0%, MSL 24.6%), on 65 of the 81 channels, and its forecast is exactly right in 95.7% of those. Asked the other
  way (the 4th and 9th of 14 readings hidden, x → y) it answers only 0.6%: how the question is asked matters more
  than the data.
- **Detection, as fixed before scoring** ([`PROTOCOL.md`](PROTOCOL.md): an alarm when the brain misses by more than it
  ever did on the channel's training data, or says CANNOT for longer than it ever did there): **77 of the 105
  anomalies found (recall 73.3%), with 140 false alarms (precision 35.5%)**. The paper's LSTM: recall 80.0%,
  precision 87.5%.
- **On equal terms**, with the paper's own thresholding ported and checked against the paper's own run (the same
  result on 77 of 82 channels): the paper's LSTM forecasts give precision 86.9% and recall 81.9%; the brain's
  forecasts give **precision 82.9% and recall 55.2%** (MSL 94.7% and 50.0%). Nothing was tuned and no label was used.
  The LSTM is trained on each channel's history and also sees the commands sent to the spacecraft (24 or 54 extra
  inputs per reading). The brain has no training run: it learns from each window's 12 readings alone, sees only the
  telemetry value, and needs about 8 KB of memory.

## The data

Nothing from NASA is copied here. Put the files in `data/` (or pass another folder to `run_all.sh`):

| | |
|---|---|
| Source | the telemanom project (github.com/khundman/telemanom). Its original data link (`s3-us-west-2.amazonaws.com/telemanom/data.zip`) answered 403 Access Denied on 2026-11-24; its README now points to Kaggle, dataset `patrickfleith/nasa-anomaly-detection-dataset-smap-msl` |
| What is needed | `data/train/<chan>.npy` and `data/test/<chan>.npy` for the 81 channels (162 files, 172,886,976 bytes), and `data/labeled_anomalies.csv` (3,956 bytes, sha256 057ce2d6…; also at `raw.githubusercontent.com/khundman/telemanom/master/labeled_anomalies.csv`) |
| For the check of the paper's thresholding only | the paper run's own LSTM forecasts and log, in the same Kaggle dataset: `data/data/2018-05-19_15.00.10/y_hat/*.npy` (82 files) and `params.log`, 3,950,662 bytes, kept under `data/lstm/` with the same path |
| Checks made | every file has the name and size of the official Kaggle list (412 files, 272,154,634 bytes; its only extra data file is `T-10`, which has no label); every channel's test length equals its `num_values`; the test lengths minus telemanom's 260 starting values give exactly the paper's 429,735 (SMAP) and 66,709 (MSL) values evaluated |
| Channels | 81; the label file has 82 rows because P-2 is listed twice (two different labels). Every row is scored on its own, as telemanom does: 82 channels, 105 sequences (SMAP 69, MSL 36; 62 "point", 43 "contextual") |
| Values | column 0 of each file (NASA's telemetry value; the other 24 or 54 columns are commands, not used). NASA says values are scaled to -1 .. 1 by the test set's min and max; 11 MSL channels go outside (M-6 up to 258.1, F-5 to 6.95) |
| Readings | train 196,321, test 509,555 (517,764 counting P-2 twice) |

## The question

- Readings are the value times 10,000, rounded to a whole number.
- A window is 14 readings in a row: 12 given, 2 asked. Here the 2 asked are the **next
  two** (`aa_solve_sequence` on the 12): a monitor's forecast. One window ends at every reading from the 14th on:
  195,268 training and 508,502 test windows, 344,576 of them distinct (each distinct window is asked once).
- The brain answers (AM or SPLITTER exact, NET an estimate) or says CANNOT. The miss is the larger of its two errors
  against the real next two readings.

## Who answered

`results/summary-seq.txt`:

| | windows | AM | NET | CANNOT | AM exactly right | AM on channels |
|---|---|---|---|---|---|---|
| SMAP train | 137,302 | 43.9% | 26.6% | 29.5% | 95.0% | 45 of 54 |
| SMAP test | 435,124 | 42.0% | 27.7% | 30.2% | 95.7% | 48 of 54 |
| MSL train | 57,966 | 31.9% | 32.5% | 35.5% | 96.7% | 17 of 27 |
| MSL test | 73,378 | 24.6% | 38.4% | 37.1% | 95.5% | 17 of 27 |
| all train | 195,268 | 40.3% | 28.3% | 31.3% | 95.4% | 62 of 81 |
| all test | 508,502 | 39.5% | 29.2% | 31.2% | 95.7% | 65 of 81 |

SPLITTER and AM estimate never answered. Of all answered test windows, the median miss is 0 and 90% miss by under
0.0722 (NASA units; the full scale is 2).

Most of AM's answers are a reading that holds: twelve readings of -3278 on P-1 give -3278, -3278. Others are steady
steps (G-6: -9931, -9924, … rising by 7 give -9847, -9840) and a jump followed by a steady level. Where the 12
readings fit more than one rule, AM gives its shortest, which need not be the spacecraft's: on D-6, twelve readings of
4096 (16³) got 4913 and 5832 (17³ and 18³), while the real readings stayed 4096. That is why 4.3% of AM's test answers
miss.

Time with 10 processes at once on an M-series Mac that was also busy with other work (`results/run-seq.json`): a
median of 18.1 ms per distinct window (AM 5.3 ms, NET 18.4 ms, CANNOT 18.0 ms); all 344,576 distinct windows in
697 s. One process alone: see "Time per check".

## Detection

Scored as the paper and the telemanom code score it ([`PROTOCOL.md`](PROTOCOL.md)): each alarm widened by 100
readings each side and joined, as telemanom does (`error_buffer: 100`); a predicted sequence overlapping a labelled
one is a true positive (once per labelled sequence), one overlapping none is a false positive, a labelled sequence
nothing overlaps is a false negative. F0.5 = 1.25 P R / (0.25 P + R). A second implementation, telemanom's own
set-based code, gave the same counts.

| | TP | FP | FN | precision | recall | F0.5 |
|---|---|---|---|---|---|---|
| **The protocol (fixed before scoring)**, SMAP | 56 | 110 | 13 | 33.7% | 81.2% | 0.382 |
| MSL | 21 | 30 | 15 | 41.2% | 58.3% | 0.438 |
| both | 77 | 140 | 28 | 35.5% | 73.3% | 0.396 |
| **The paper's thresholding on the brain's forecasts** (nothing tuned, no label used), SMAP | 40 | 11 | 29 | 78.4% | 58.0% | 0.733 |
| MSL | 18 | 1 | 18 | 94.7% | 50.0% | 0.804 |
| both | 58 | 12 | 47 | 82.9% | 55.2% | 0.753 |
| **The same thresholding on the paper's LSTM forecasts** (the check of the port), SMAP | 62 | 12 | 7 | 83.8% | 89.9% | 0.849 |
| MSL | 24 | 1 | 12 | 96.0% | 66.7% | 0.882 |
| both | 86 | 13 | 19 | 86.9% | 81.9% | 0.858 |
| **The paper's own run** (its `params.log`, 2018-05-19), both | 84 | 11 | 21 | 88.4% | 80.0% | 0.866 |
| **The paper, Table 2** (LSTM + nonparametric thresholding with pruning), SMAP | | | | 85.5% | 85.5% | 0.71 |
| MSL | | | | 92.6% | 69.4% | 0.69 |
| both | | | | 87.5% | 80.0% | 0.71 |
| **Tuned on SMAP's labels, scored on MSL** (extra), SMAP (tuned on, optimistic) | 34 | 1 | 35 | 97.1% | 49.3% | 0.813 |
| MSL (never seen by the tuning) | 10 | 3 | 26 | 76.9% | 27.8% | 0.568 |
| **The other way of asking** (the 4th and 9th of 14 asked), the protocol, SMAP | 55 | 161 | 14 | 25.5% | 79.7% | 0.295 |
| MSL | 21 | 24 | 15 | 46.7% | 58.3% | 0.486 |
| both | 76 | 185 | 29 | 29.1% | 72.4% | 0.331 |

- **The paper's F0.5 column** does not follow from its own precision and recall with the usual formula (that gives
  0.855, 0.868 and 0.859); the paper gives no formula. Compare precision and recall.
- **The protocol's false alarms** are spread over 39 channels (D-5 alone 22; P-2 7 on each of its two rows). Two
  causes: channels that barely moved in training get a tiny "worst miss" (D-5: 10 units = 0.001; P-14: 3 units, from
  its 19 answered training windows), so ordinary test movement looks new; and CANNOT runs longer than in training
  (E-3). The paper's code guards against the first with size tests (an error must be at least 5% of the window's
  5-95% range, and above 0.05); the protocol has no such guard.
- **The paper's thresholding** (`scripts/paper_threshold.py`) follows telemanom's `errors.py` step by step: EWMA
  smoothing (span 105), windows of 30 x 70 errors moving one batch of 70 at a time, the z search 2.5 .. 11.5 for the
  errors and for the errors turned upside down, the size guards, pruning with p = 0.13, the 100-reading widening. The
  brain's forecast where it said CANNOT is its net's own estimate. **Check:** on the paper's own LSTM forecasts it gives
  the same TP, FP and FN as the paper's 2018 run on 77 of the 82 rows; the other 5 differ by one each (P-1, E-12,
  E-13 one more found; G-3, T-1 one more false alarm), likely telemanom code changes since that run (for one, the
  index shift of its PR #27). Recall by class on the LSTM forecasts: SMAP point 95.3% and MSL contextual 58.8%, both
  exactly the paper's Table 4. telemanom skips its start-up smoothing for C-2 because that anomaly comes early, an
  exception made from the label; it is not made for the brain. Made for the LSTM, it gives 87 / 13 / 18 (87.0%,
  82.9%).
- **Tuning on SMAP** (`scripts/tune.py`, 140 settings: a floor of 0 to 20% of the full scale under which a miss is
  ignored, a margin of 1 to 5 times the worst training miss, CANNOT alarms off or at 1, 2 or 4 times the longest
  training run): best on SMAP was floor 0.5%, margin 2, CANNOT alarms off. On MSL it gives 76.9% precision and 27.8%
  recall.
- **The other way of asking** (`aa_solve_rule`, x = 0, 10 .. 130, the 4th and 9th held back; `results/summary-fill.txt`):
  NET 73.6%, CANNOT 25.8%, AM 0.6% and SPLITTER 22 windows of the 508,502 test windows; AM on 15 channels. 68 minutes on 10 cores (`results/run-fill.json`; a median of 115 ms a
  window: rules of x → y take AM's full search).
- Of the 105 labelled anomalies, 46 are found by both the protocol and the paper's thresholding on the brain, 31 only
  by the protocol, 12 only by the thresholding, 16 by neither. 11 of those 16 are "contextual" (the paper's class:
  values within the normal range), and 8 of the 16 stay entirely within the range of the 500 readings before them.
- Recall by the paper's anomaly class (its Table 4; `scripts/by_class.py`, `results/by-class.txt`):

  | | point, SMAP | point, MSL | point, both | contextual, SMAP | contextual, MSL | contextual, both |
  |---|---|---|---|---|---|---|
  | the protocol | 39/43 = 90.7% | 16/19 = 84.2% | 55/62 = 88.7% | 17/26 = 65.4% | 5/17 = 29.4% | 22/43 = 51.2% |
  | the paper's thresholding on the brain | 30/43 = 69.8% | 13/19 = 68.4% | 43/62 = 69.4% | 10/26 = 38.5% | 5/17 = 29.4% | 15/43 = 34.9% |
  | the same on the LSTM forecasts | 41/43 = 95.3% | 14/19 = 73.7% | 55/62 = 88.7% | 21/26 = 80.8% | 10/17 = 58.8% | 31/43 = 72.1% |
  | paper, Table 4 | 95.3% | 78.9% | 90.3% | 76.0% | 58.8% | 69.0% |

## Time per check

One process alone on an M-series Mac, 3,000 test windows drawn at random (seed 1) as the monitor meets them
(`scripts/bench.py`, `results/bench.txt`):

| | windows | median time of the solve call |
|---|---|---|
| AM | 1,180 | 4.03 ms |
| NET | 909 | 12.6 ms |
| CANNOT | 911 | 12.8 ms |
| all (mean) | 3,000 | 9.32 ms |

The paper treats the readings as one a minute (its batches of 70 values are 70 minutes), so even the slowest check
is far inside the time between two readings.

## Replicate it

```bash
cd space
bash run_all.sh            # every number above into out/ (about 80 minutes on 10 cores); data/ as described above
```

`run_all.sh` lists every step and writes the same files as `results/`. On Linux, build first with
`make TARGET=linux-x86_64` (or `linux-aarch64`).

## Files

| File | What it does |
|---|---|
| `PROTOCOL.md` | the detector and scoring, written before the first score |
| `nasa_run.c`, `Makefile` | the brain on windows from standard input (a sequence or a rule); prints who answered, the answers, the time |
| `scripts/run_brain.py` | every window of every channel through `nasa_run`, answers saved per channel (`out/<run>/<chan>_<train|test>.npz`) |
| `scripts/summarize.py` | who answered, misses |
| `scripts/detect.py`, `scripts/detect_lib.py` | the protocol's detector, telemanom's grouping and scoring |
| `scripts/paper_threshold.py` | the paper's thresholding, on the brain's forecasts or the paper's own |
| `scripts/tune.py` | the SMAP-tuned settings, scored on MSL |
| `scripts/by_class.py`, `scripts/bench.py` | recall by class; time per check |
| `results/` | this run's outputs: who answered (`summary-*`), detection (`detect-*`, `paper-threshold-*`, `tune-seq`, `by-class.txt`), times (`run-*.json`, `bench.*`) |

telemanom's thresholding steps follow its `errors.py` (Hundman et al., © 2018 California Institute of Technology,
BSD-style licence).
