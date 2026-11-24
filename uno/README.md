# Uno: the brain in 2 KB, on a real Arduino Uno

The Arduino Uno's chip, the ATmega328P, is an 8-bit microcontroller running at 16 MHz, with **2 KB of RAM**, 32 KB of
flash and no floating-point hardware. A cut-down edition of the brain, the Uno edition, runs entirely on it: AM, AM's
splitter and a small net, in **782 bytes** of state.

**In short:**

- **9 of 9 right on a real Arduino Uno:** 3 exact rules, 3 noisy trends and 3 problems of pure noise, where the right
  answer is CANNOT.
- **Every one of its 9 lines was the same as the computer's:** who answered, both answers, the self-check, right or
  wrong.
- **Memory, measured on the chip:** at its peak, the whole program, brain included, used **1,901 of the 2,048 bytes**
  of RAM. 147 bytes were never touched.
- **Flash:** the whole program is **31,936 of the 32,256 bytes** an Uno program can use.
- **Time and power:** 92 minutes for the 9, on a board drawing 0.25 to 0.5 W.

A partner ran it on a real Arduino Uno on 22 November 2026. This folder holds the run's results: the board's log and
the computer's reference.

## The run

The 9 problems are the quick set of the 300-problem challenge (in this repository's history). Each gives 8 or 12
examples x → y and asks for 2 more answers. A trend is right within its tolerance; noise is right only as CANNOT.

| Problem | Kind | The right answer | The Uno's answer | By | Self-check | Time on the Uno |
|---|---|---|---|---|---|---|
| p000 | trend | 210.74 and 205.46 (± 25.5) | 210 and 204 | the net | 1000 | 13.6 min |
| p001 | noise | CANNOT | CANNOT | CANNOT | 83 | 16.1 min |
| p002 | rule | 428 and 460 | **428 and 460** | AM | | **0.9 s** |
| p095 | trend | −45.04 and −354.19 (± 53.77) | −64 and −363 | the net | 1000 | 13.9 min |
| p099 | noise | CANNOT | CANNOT | CANNOT | 0 | 10.2 min |
| p105 | rule | 567,009 and 620,944 | **567,009 and 620,944** | AM | | 5.8 min |
| p193 | rule | 238 and 228 | **238 and 228** | AM | | **2.7 s** |
| p199 | trend | 277.26 and 109.58 (± 20.2) | 276 and 106 | the net | 833 | 16.1 min |
| p213 | noise | CANNOT | CANNOT | CANNOT | 333 | 16.3 min |

- **By:** AM, with an exact rule it found in the examples; the net, with an estimate that passed its self-check; or
  CANNOT.
- **Self-check:** the net hides each example in turn, learns from the others and guesses the hidden one. The score is
  the share it guessed to within a tenth of the examples' spread, out of 1,000. Below 500, the answer is CANNOT.
- **Time:** an exact rule that AM finds early takes seconds; one deeper in its search took 5.8 minutes. A problem with
  no exact rule takes 10 to 16 minutes, because AM searches everything first and then the net learns. With no
  floating-point hardware, every number the net computes is worked out in software, 8 bits at a time. In all,
  5,526 s (92.1 minutes).
- **Power:** the partner's USB meter showed 0.25 to 0.5 W for the whole board. Most of that is the board's USB chip,
  regulator and LEDs, not the ATmega328P.

## The memory, measured on the chip

Before the first problem, the program fills all the free RAM with a pattern. After each problem it counts the bytes
that still hold it: **147, every time**. So at its peak the program used **1,901 of the 2,048 bytes**. That covers
everything the program uses:
- the brain (782 bytes: the problem in hand and the net);
- AM's search;
- the rest of the program and the Arduino core.

The net takes its memory only after AM's search has given its own back, so the two never need room at the same time.

## What the Uno edition is

| | The brain in `brain/` | The Uno edition |
|---|---|---|
| Problems | rules x → y, sequences, and an online learner for streams | rules x → y only (noisy trends and noise included) |
| Examples per problem | up to 16 | up to 12 (the challenge's problems have at most 12) |
| The net | 72 units (289 numbers) | **8 units (33 numbers)** |
| The brain's state | 5,216 bytes, plus at most 3 KB of stack | **782 bytes**, plus the stack |
| Arithmetic | single and double precision | single precision only |
| Version | 1.2 | made from 1.0 |

**AM and its splitter are the same code, with smaller buffers.** The splitter's 22 pieces are all that 12 examples can
need, so their answers don't change.

**Made from version 1.0.** AM's proof (version 1.1) alone takes 2,274 bytes of flash, and the Uno edition leaves 320,
so the edition is made from version 1.0. On these 9 problems the full brain gives the very same answers in 1.0, 1.1
and 1.2. The Uno edition matches it on all 9:
- the same 3 exact answers;
- the same 3 CANNOTs;
- 3 right estimates, within 8 units of the full brain's.

**On a computer, with the same code,** the Uno edition gets **216 of the 242 x → y problems** in the 300-problem
challenge right, against **219** for the full brain of the same version. **All 71 of its exact answers are the same as
the full brain's.** The 3 it misses are noisy trends, where its net is smaller.

## Files

| File | What it holds |
|---|---|
| `real-uno-run.txt` | the real Uno's log, as the partner's computer saved it (the date kept, the time of day and time zone removed) |
| `expected.txt` | the reference: the Uno edition's answers to the 9 problems on a computer, with the same code |

Apart from spacing and its `ms=` and `cycles=` fields, each problem's line in the log is the same as its line in the
reference.
- `ms=` is the board's own clock.
- `cycles=none` means there is no cycle counter on the ATmega328P.
- The board printed its first three lines twice, because an Uno restarts when its serial port is opened.
