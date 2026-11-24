# edai: a brain that learns and reasons in 8 KB

edai is a brain for the smallest devices. It learns and reasons with **about 8 KB of memory**: **5,216 bytes** of
state and at most **3 KB** of stack. It needs no stored model, no training run, no cloud, no operating system and no
heap.

- **AM reasons.** From a handful of examples it finds the exact rule, made of short chains of integer steps, and proves
  it before answering. An exact answer never contradicts an example.
- **A small net learns.** When there is no rule, it learns the examples on the spot and checks itself on examples it
  hid from itself before it estimates. It also shows AM where to search.
- **Otherwise it says CANNOT.** It does not guess.

It runs on a **$4 Raspberry Pi Pico** (no floating-point unit), on phones and in browsers, on servers, and, in a
[2 KB edition](uno/README.md), on an 8-bit **Arduino Uno with 2 KB of RAM**. It gives **the same answer, bit for bit,
on every one of them**. It is supplied here compiled (`brain/`).

**Version 1.2** (23 November 2026): AM proves its answers (1.1), and the net is AM's light (1.2).

## Its strength: memory

| | edai | for comparison |
|---|---|---|
| The whole brain's state | **5,216 bytes**, the same object for every problem | the NASA benchmark's LSTMs (below): about **29 MB** of weights, one model per channel |
| Stack | at most **3,072 bytes** on any target; 2,888 measured on a real Pico (version 1.1) | |
| Code | about 31 KB of program space for a whole program on an Arm microcontroller | |
| Stored model or training data | **none**: it learns each problem from its own examples | trained per task, kept in memory |
| Heap, globals, operating system | **none** | |

What the 5,216 bytes hold:

| | Bytes |
|---|---|
| the problem in hand: up to 16 examples and 2 questions | 288 |
| the net's 289 learned numbers | 1,156 |
| what learning needs: two running averages and the current slope for each number | 3,468 |
| the net's 72 units and two counters | 296 |
| a check word | 8 |
| **total** | **5,216** |

It needs so little because:

1. **It keeps no model.** It learns each problem from that problem's own few examples, from scratch, and keeps nothing
   afterwards. The same 5,216 bytes serve every problem.
2. **The net is small:** 289 numbers in 32-bit floating point.
3. **AM keeps no tables.** It tries each short chain of steps in turn and keeps only the best answer for each part of
   the problem, so its whole search fits on the stack.
4. **No heap and no globals.** All state is in the one object you own: put it in static memory, on a task's stack or in
   a pool.
5. **The stack is bounded and measured.** The deepest any call goes is worked out from the compiler's frame sizes, and
   checked on real chips.
6. **Its maths is its own.** `exp`, `tanh` and square roots are the library's own code, which is also why every chip
   gives the same answers.

**And in 2 KB.** A cut-down edition keeps the same design (AM, its splitter and a net of 8 units) in **782 bytes** of
state. On a real 8-bit Arduino Uno, the whole program peaked at **1,901 of the chip's 2,048 bytes** of RAM, and it got
9 of 9 right ([`uno/`](uno/README.md)).

The trade is time: because it learns on every question, it spends time where others spend memory. That is about
20 ms a problem on a laptop. On the $4 Pico, an exact rule takes seconds, and a problem the net must learn about a
minute.

## Three tests

### [Space: NASA spacecraft telemetry](space/README.md)

The brain watched NASA JPL's public telemetry from the **SMAP satellite** and the **Curiosity rover**, the benchmark of
Hundman et al. (KDD 2018): 82 channels and 105 labelled anomalies. Every window asks: here are 12 readings, what are
the next two?

- **AM answered 39.5%** of the 508,502 test windows with a rule of its own, and was **exactly right on 95.7%** of those.
- **Spikes:** the detector, fixed before scoring, caught **55 of the 62 sudden-spike anomalies, as many as the paper's
  LSTM**. In all it found 77 of the 105 anomalies.
- **With the paper's own thresholding**, the brain's forecasts reached **82.9% precision** (94.7% on the rover).
- **Memory:** the paper's LSTMs hold about 29 MB of weights (81 models, from its own published settings) and also see
  the commands sent to the spacecraft. edai is **one 5,216-byte brain for every channel**, with no training: about
  **4,900 times less memory**.
- Every number was made with the library in `brain/`, and `space/run_all.sh` makes them all again.

### [Shake: learning through vibration](shake/README.md)

Robots shake, and a small chip can't tell a pattern from the shaking on its own. So a big machine learned 9 robot
rules (drone, dish robot, cleaner) through real motor vibration, and gave a $4 Pico only the rules and their noise
allowances: **100 bytes**.

- **Exactly right on 270 of 270** shaky windows, with **no wrong answer and no false alarm**.
- **Every fault flagged:** knocks, stuck sensors, drifts, jobs it was never taught. **0 wrong answers in 525** windows.
- **On the real Pico, every one of its 543 output lines was the same as the computer's.** A window took **0.54 ms**,
  against about 62 s for the brain learning alone.

### [Uno: the 2 KB edition on a real Arduino Uno](uno/README.md)

The Arduino Uno's ATmega328P is an 8-bit chip with 2 KB of RAM and no floating-point hardware. A cut-down edition of
the brain, made from version 1.0, ran on a real board: AM, its splitter and a net of 8 units, in 782 bytes of state.

- **9 of 9 right** (3 exact rules, 3 noisy trends, 3 of pure noise), and **all 9 lines the same as the computer's**.
- **Memory, measured on the chip:** the whole program peaked at **1,901 of the 2,048 bytes**. It fills 31,936 of the
  32,256 bytes of flash an Uno program can use.
- **92 minutes** for the 9: exact rules in seconds to minutes, problems with no rule in 10 to 16 minutes. The whole
  board drew 0.25 to 0.5 W.

## Use it

```c
#include "aa.h"

static aa_brain brain;                       /* 5,216 bytes: put it anywhere */

int main(void)
{
    aa_answer a;
    aa_brain_init(&brain);
    const int64_t x[] = {55, 68, 19, 29, 95, 4, 92, 13}, y[] = {440, 544, 152, 232, 760, 32, 736, 104}, q[] = {111, 118};
    aa_solve_rule(&brain, x, y, 8, q, 2, &a);   /* a.by == AA_AM (an exact, proved rule), a.value == {888, 944} */
    return 0;
}
```

```bash
cc -std=c11 -I brain/include your.c brain/lib/macos-arm64/libaa.a -o your_program
```

- **The header:** `brain/include/aa.h` describes every call: rules (`aa_solve_rule`), sequences (`aa_solve_sequence`),
  and an online learner for sensor streams (`aa_observe`, `aa_predict`).
- **The libraries:** `brain/lib/<target>/libaa.a` for 9 targets:
  - Cortex-M0+, M4F, M33 and M7;
  - RISC-V (imc and imafc);
  - macOS on Apple silicon;
  - Linux on x86-64 and AArch64.

  Their SHA-256 sums are in `SHA256SUMS.txt`.
- **What a program needs:** on microcontrollers, only the compiler's helpers and `memset`/`memcpy`.

## The same answer on every chip

The brain gives the same answer bit for bit on every target. That has been checked:
- on a real Raspberry Pi Pico (all 300 problems of the earlier challenge, every line the same as the computer's);
- on emulated Cortex-M4F, M7, M33 and M0 cores;
- on a real Arduino Uno (the 2 KB edition: all 9 lines the same as the computer's, [`uno/`](uno/README.md));
- on phones and in browsers;
- in the shake test above (543 of 543 lines on the Pico).

Earlier versions of this repository held those runs: the 300-problem challenge, its fresh problem sets, the device
runners, the exactness and light tests, an outside challenger and the real-sensor tests. They are all in its history,
up to commit `b3c00e9`.

## What is here

| Path | What it holds |
|---|---|
| `brain/include/aa.h`, `brain/lib/<target>/libaa.a` | the compiled brain for 9 targets, and its header |
| `space/` | the NASA telemetry test: the program, the scripts, the protocol fixed before scoring, and the results |
| `shake/` | the shake test: what was done and every result |
| `uno/` | the 2 KB edition on a real Arduino Uno: the board's log, the computer's reference and the results |
| `SHA256SUMS.txt` | the libraries' SHA-256 sums |
