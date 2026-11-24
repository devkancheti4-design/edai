# Protocol, fixed before any test label was looked at (2026-11-24, about 09:30 IST)

The detector and its scoring were written down here before the brain's flags were scored against
`labeled_anomalies.csv`. Anything tried after this point is reported as an extra, beside this one, never instead of it.
This is that text as written, except that two planned extras that are not part of this folder are left out.

## The brain's question (the same for every channel, train and test)

- Readings: column 0 of each channel's `.npy` (NASA's telemetry value, pre-scaled to about -1 .. 1) times 10,000,
  rounded to a whole number.
- A window is 14 readings in a row, as in edai's trend problems: 12 given, 2 asked. Here the 2 asked are the next two
  readings (`aa_solve_sequence` on the 12, a monitor's forecast). One window ends at every reading from the 14th on.
- The brain answers (AM, SPLITTER exact; NET, AM estimate) or says CANNOT. Its miss is the larger of its two errors
  against the two real readings.

## The detector (no setting is tuned; everything comes from the channel's own training data)

For each channel, on its training data (normal running):
- `worst miss` = the largest miss of any answered training window;
- `longest CANNOT run` = the most CANNOT windows in a row.

On the channel's test data a window raises an alarm when
- the brain answers and misses by more than its `worst miss` (it never missed that badly in normal running), or
- the brain says CANNOT and the CANNOT run it is in has become longer than the `longest CANNOT run`.

A channel with no answered training window gets no miss alarms. The alarm's time is the window's last reading.

## Scoring (as the paper and the telemanom code do it)

- Each alarm time is widened by 100 readings each side and touching alarms are joined into one predicted sequence,
  as telemanom does (`error_buffer: 100`).
- telemanom's `evaluate_sequences`: a predicted sequence that overlaps a labelled sequence is a true positive for the
  first labelled sequence it overlaps (only once per labelled sequence); one that overlaps none is a false positive;
  a labelled sequence that no predicted sequence overlaps is a false negative.
- Every row of `labeled_anomalies.csv` is scored on its own (P-2 has two rows, with the same predictions), which gives
  the paper's 82 channels and 105 sequences (SMAP 69, MSL 36).
- Precision = TP / (TP + FP), recall = TP / (TP + FN), F0.5 = 1.25 P R / (0.25 P + R), for SMAP, MSL and both.

## Extras planned (each reported beside the main result)

- Edai's own trend framing (the 4th and 9th of 14 readings asked, `aa_solve_rule`), same detector.
- If any setting is ever tuned on labels, it is tuned on SMAP only and the result reported on MSL.
