#!/bin/bash
# bash run_all.sh [data dir]: every number in README.md, from NASA's files (README.md says where to get them; the
# default data dir is data/).  About 75 minutes on 10 cores of an M-series Mac (edai's trend framing is about an hour
# of it).  Writes out/, the same files as results/.
set -e
cd "$(dirname "$0")"
DATA=${1:-data}
make
mkdir -p out

# 1. the brain on every window (the next two of 14 readings), train and test, and the protocol's detector
python3 -I scripts/run_brain.py ./nasa_run "$DATA" out/seq seq 10 | tee out/seq.log
cp out/seq/run.json out/run-seq.json
python3 -I scripts/summarize.py "$DATA" out/seq out/summary-seq.json | tee out/summary-seq.txt
python3 -I scripts/detect.py "$DATA" out/seq out/detect-seq.json | tee out/detect-seq.txt
python3 -I scripts/by_class.py "$DATA" out/detect-seq.json | tee out/by-class.txt
# extras on these answers: the paper's thresholding (no label used), and settings tuned on SMAP, scored on MSL
python3 -I -W ignore scripts/paper_threshold.py "$DATA" out/seq out/paper-threshold-seq.json | tee out/paper-threshold-seq.txt
python3 -I scripts/by_class.py "$DATA" out/paper-threshold-seq.json | tee -a out/by-class.txt
python3 -I scripts/tune.py "$DATA" out/seq out/tune-seq.json | tee out/tune-seq.txt
# time per check, one process alone
python3 -I scripts/bench.py ./nasa_run "$DATA" 3000 out/bench.json | tee out/bench.txt

# 2. edai's own trend framing (the 4th and 9th of 14 readings asked), the same detector
python3 -I scripts/run_brain.py ./nasa_run "$DATA" out/fill fill 10 | tee out/fill.log
cp out/fill/run.json out/run-fill.json
python3 -I scripts/summarize.py "$DATA" out/fill out/summary-fill.json | tee out/summary-fill.txt
python3 -I scripts/detect.py "$DATA" out/fill out/detect-fill.json | tee out/detect-fill.txt
python3 -I scripts/by_class.py "$DATA" out/detect-fill.json | tee -a out/by-class.txt

# 3. the check of the paper's thresholding on its own LSTM forecasts (needs the paper run's forecasts, see README.md)
Y="$DATA/lstm/data/data/2018-05-19_15.00.10/y_hat"
if [ -d "$Y" ]; then
  python3 -I -W ignore scripts/paper_threshold.py "$DATA" --lstm "$Y" out/paper-threshold-lstm.json | tee out/paper-threshold-lstm.txt
  python3 -I scripts/by_class.py "$DATA" out/paper-threshold-lstm.json | tee -a out/by-class.txt
  python3 -I -W ignore scripts/paper_threshold.py "$DATA" --lstm "$Y" out/paper-threshold-lstm-c2.json c2 | tee out/paper-threshold-lstm-c2.txt
fi
