# Code that heals itself

Coding is rules. So let the big model write the code once, and let small brains keep it right afterwards: they catch what breaks, put the right answer
back, and take updates, at no further cost and with no tokens.

**In short:**

- **Learned from the program's own calls.** From the call log of a delivery-drone dispatch service (16 functions, 2,000 calls each), the brain found
  the exact rule of **12 of the 16** in under 6 seconds on a laptop, with no model asked anything. The 12 rules take **48 bytes**. The other 4 (a price table, a text
  label, an exponential, a hash) were reported as not guarded instead of guarded badly.
- **Every planted bug caught and healed:** **167 of 167**. Without the guard the callers would have received **71,557 wrong answers**; with it, **0**.
- **No false alarms:** 0 in **240,000** calls of the correct code.
- **On a real $4 chip:** **323,500 of 323,500 decisions** the same as the computer's, **4.4 µs** a check, in **3,648 bytes of flash and 168 bytes of RAM**.
- **Live, inside a running program:** in 20 minutes of traffic with 223 bugs deployed, customers got **16,082 wrong answers from the bare service and
  842 from the guarded one**, of 915,876 each.

## The service and what was learned

| Function | What it does | The rule the brain found |
|---|---|---|
| `pages_needed` | pages of 10 orders | (x + 9) // 10 |
| `page_offset` | first row of a page of 12 | (x − 1) × 12 |
| `next_pad` | the next of 8 landing pads | (x + 1) mod 8 |
| `padded_size` | packets padded to 4-byte words | ((x − 1) or 3) + 1 |
| `loader_trips` | trips of 8 parcels | (x + 7) // 8 |
| `delivery_fee` | 7 credits up to 5 kg, then 3 a kg | max(3x − 8, 7) |
| `battery_reserve` | 12 Wh a km plus 9 to land | 12x + 9 |
| `safe_speed` | held between 2 and 36 m/s | min(max(x, 2), 36) |
| `check_digit` | mod-11 label digit | x mod 11 |
| `led_level` | LED gamma 2 | (x × x) >> 4 |
| `weekday` | day of the week | (x + 3) mod 7 |
| `grid_cell` | 12-metre map cell | x // 12 |
| a price table, a text label, an exponential, a hash | | none: reported as not guarded |

A rule was kept only if it gave the logged answer on **every** logged call. Each of the 12 functions, written back from its rule, is right on every input of
its range.

## The planted bugs

Every single change of every guarded function, as mutation testing makes them, each run on 500 fresh calls:

| What changes | Caught and healed |
|---|---|
| a number off by one either way, or doubled | 48 of 48 |
| a setting off by one either way | 16 of 16 |
| an operator (+ and −, × and //, shifts, and, or) | 30 of 30 |
| an operation dropped | 44 of 44 |
| min and max swapped | 3 of 3 |
| a minus sign lost | 2 of 2 |
| the function crashes | 12 of 12 |
| the answer comes back 10 times too big | 12 of 12 |
| **all** | **167 of 167** |

The first wrong call was flagged at once (median: the very first). A check costs about 0.5 µs in Python on a laptop.

## On a real $4 Raspberry Pi Pico

The chip got every call's input and answer over USB and decided; it never knew which code was healthy.

| | |
|---|---|
| Decisions the same as the computer's | **323,500 of 323,500** (83,500 calls of the 167 bugs, 240,000 of the healthy code) |
| Bugs caught and healed by the chip | **167 of 167**; wrong answers reaching the caller: 71,557 without, **0** with |
| False alarms | **0** of 240,000 |
| Time of a check | **4.4 µs** in a tight loop; median 8.8 µs with calls coming one at a time |
| Memory | **3,648 bytes of flash, 168 bytes of RAM**, 180 bytes of stack; no brain object is needed for a check |
| Damaged rules at start | 384 of 384 one-bit flips and 48 of 48 shortened copies refused |
| Random calls over the whole 64-bit range, and damaged lines | 40,000 of 40,000 decisions the same; 4,015 damaged lines, none decided on |
| **An update of 18 bytes** (a change that was meant) | taken in **149 µs**; the new code flagged on 0 of 200 calls (200 of 200 before); all 323,500 decisions the same as the computer's again |

The update's test found a gap: its last 2 bytes, which say which function changed, had no check of their own, and 4 of their 16 one-bit errors were taken. With a
check byte in the same 18 bytes, all 144 one-bit errors were refused on the chip.

## Live, in any running Python program

The guard goes into a running program without changing its files. It learns each function from the program's own calls, **proves** the rule on every whole number in the
range it met, and heals only when new code has come and only on inputs it is sure of. A person approves a change that is meant.

| What | Result |
|---|---|
| **A live service** (20 minutes, 40 orders and 40 gradings a second, 223 bugs deployed one after another) | wrong answers the customers got: **16,082** from the bare service, **842** from the guarded one, of 915,876 each (144 of the bugs changed answers; 135 of those gave the customers none at all) |
| **Code not written for this:** 65 test modules of Python's own library, 16,267 tests | **no result different**; 40.2 million calls, 16.1 million checked, **0 answers replaced** |
| **A grading program of 63 functions**, as it was (not public) | 62 guarded after 10 seconds; all 49,152 possible gradings right; bugs in its inner functions: **2,453 of 8,250 gradings wrong without, 0 with** |
| **Caught as the code loads**, before any call | 217 of 217 and 59 of 59; 293 of 299 in Python's own library |
| **Cost** | 97 ns a guarded call |

Where it does not heal: 740 of the 842 were one hash function, 102 were three functions with no rule and more inputs than it remembers. All of these were caught as the code
loaded. In Python's own library only 1 of the 32 tested functions had a rule: mostly decimals and very large numbers that never repeat. There it raises the alarm and does
not heal (178,672 wrong answers became 106,816).

## Against tampering

Thirteen access checks (admin level, lock-out, transfer limit, ports and so on) were learned from their live calls, then changed by an attacker one at a time: 113 attacks, run once,
with nothing tuned for it.

| | Attacks | Wrong decisions without / with | Caught as the code loaded |
|---|---|---|---|
| **the 10 checks learned by rule** (55 bytes) | 67 | **20,309 / 0** | 57 (all 67 seen) |
| of those, hidden back doors on one input | 10 | 334 / 0 | **10 of 10** |
| 1 check remembered whole | 6 | 2,188 / 0 | 5 (all 6 seen) |
| 2 checks with large ranges and no rule | 14 | 4,938 / 3,662 | 10 |
| back doors on a number far outside anything met | 13 | 260 / 260 | 0 (7 seen) |
| code that sends its input away and answers right | 13 | 0 / 0 | 0 |

It is an alarm and a seat belt against tampered code, **not a lock**: someone who can change the running program can also reach the guard inside it, and its rules are not signed.

## Honest limits

- It keeps the behaviour it learned. If the code was already wrong, the wrong answer is the trusted one until a person approves a fix.
- It guards functions of whole numbers (live: also decimals and true/false) whose answers are numbers or short texts. Rules cover code that is laws on whole numbers: fees, paging, padding,
  time slots, units, masks, decisions. They cover little of ordinary library code.
- On the chip, the functions themselves ran on the computer and the Pico watched them. (In the [flight test](../flight/README.md) the laws ran on the chip too.)
- The customers in the live run were programs, not people.
- Its code is not published.
