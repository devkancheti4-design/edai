# Taught once, known by every chip

Finding a rule takes time; using one does not. So let one brain (the teacher) find the rules once, hand them to every other chip as a few bytes, and let each chip answer from them at once when one fits. If none
fits, the chip searches as always.

**In short:**

- **729 times faster on the real $4 Pico.** The 93 problems it could answer from the rules took **0.96 s instead of 699.5 s** of searching, every one exactly the teacher's answer (median 0.68 ms each).
- **94 rules in 449 bytes**, all that the teacher proved on the 300 problems of the test stream.
- **The chip can be the teacher:** the rules the Pico found by itself were byte for byte the computer's.
- **An update is 20 bytes**, taken by the chip in **1.5 ms**. Sent twice, or with a byte changed, it was refused.
- **Damage is refused:** 3,592 of 3,592 one-bit flips and 449 of 449 shortened copies, on the chip.
- **The brain itself is unchanged:** on the Pico all 300 problem lines were the same as the computer's, down to the rule behind each answer.

## On the real Raspberry Pi Pico (RP2040, 125 MHz, no floating-point unit)

| | |
|---|---|
| The 300 problems, searching | 274 of 300, every line the same as the computer's; 16,768 s |
| Asked again, the rules first | 106 of them have a rule the chip was given: **93 answered from the rules**, each the teacher's answer; the other 13 were searched and gave the same answers to the bit |
| Those 93 | **0.96 s** from the rules (0.36 ms fastest, 0.68 ms median, 24.6 ms longest), **699.5 s** by search |
| The rules made on the chip / on the computer | the same 449 bytes |

A USB stall dropped 51 of the 300 lines on their way to the computer; they come from a second run of the same problems, and every line matched.

## On a computer, more problems

| | |
|---|---|
| 1,800 problems taught | 514 rules in 2,516 bytes; 557 of the problems answered from them, **every one the brain's own exact answer** |
| Problems the teacher had not seen (five sets taught, the sixth asked, six times) | 167 answered from the rules: 166 the same as the brain's own, and the one that differs is right where the brain was wrong |
| 1,500 newly made problems | 141 answered from the rules, 141 the same |
| Work on unseen problems | 379 million steps of search became 95 thousand |
| Wrong rules on purpose | 640,367 changed rules and 34,963 trick problems: **no answer that contradicts an example** |
| Damaged rules | 0 of 22,644 accepted |

## Honest limits

- **On problems never seen it helps mostly with shapes that come back:** 277 of the 308 such answers were number sequences. The test's x → y rules are random and seldom repeat (31 of 308). A device that keeps meeting the same
  rules would gain much more.
- A wrong rule that fits every example cannot be told from the right one by the examples. The promise is "never contradicts an example", not "always right".
- For the very simplest rules, searching is as fast.
- Its code and the form of the bytes are not published.
