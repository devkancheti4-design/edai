# Many small brains, and a queen

The brain is small (about 5 KB of state), so many of them fit where one big model would. Two tests: do many beat one, and what does a big device that **remembers** add on top?

**In short:**

- **Many beat one.** A swarm of 129 unchanged brains, each with its own view of the problem, against one brain alone, on **3,000 problems never seen**: **+53 gained, 0 lost** (2,749 against 2,696).
- **They know when they agree.** Answers given by a clear majority of the swarm were right **93.0%** of the time, as often as the single brain's own exact answers (91.5%). Wrong swarm answers fell from 11 to 4
  with the stricter vote.
- **A queen that remembers beats both.** On 1,000 meetings with 200 machines, **the swarm with the queen got 879 right, the swarm alone 801, one brain 793**. Its exact answers were right 93.9% of the time,
  against 84.0%.
- **Most known machines never need the queen:** 435 of the 1,000 meetings were answered at the edge by the small brain alone, 425 of them right, in a median of 46 µs.

## Many against one

Every brain in the swarm is the same compiled brain, unchanged. The brain is deterministic, so copies that see the same thing would all say the same thing. Here each one looks at the problem in its own
way. If the first brain has an exact answer, it stands. Otherwise, if at least two-thirds of the brains that found a rule agree (and at least 2 do), theirs is the swarm's answer.

| | Right | Swarm answers | Wrong |
|---|---|---|---|
| **First test** (1,800 problems never seen): one brain | 1,658 | | |
| swarm, first rule (a plain majority) | 1,693 (+35, 0 lost) | 45 | 10 |
| **Second test** (3,000 new problems): one brain | 2,696 | | |
| swarm, first rule | 2,751 | 67 | 11 |
| **swarm, two-thirds rule** | **2,749** (+53, 0 lost) | 57 | **4** |

- The swarm beat the single brain on every one of the 16 sets. The stricter rule was chosen on other problems (3,000 of them) and frozen before the test sets were made.
- **Noise stays noise:** in the first test's 360 noise problems, not one of the 129 brains found a rule.
- **Time:** with one chip per brain, 1.32 times the single brain's time; one chip running them all in turn, 101 times.
- The 4 wrong answers of the second test are all rules in pieces, where the question falls on a side with only one or two examples: no vote can catch that.

## The queen

A world of 200 machines, each with one hidden rule, met 5 times. The queen keeps every example every machine has given, checks every answer against all of them, and teaches each machine's small brain its
rule in 14 to 25 bytes. The swarm does the searching.

| Test world (made after the design was frozen, run once) | One brain | Swarm | **Swarm and queen** |
|---|---|---|---|
| **right, of 1,000 meetings** | 793 | 801 | **879** |
| later meetings, of 800 | 637 | 640 | **718** |
| exact answers right | 84.5% | 84.0% | **93.9%** |
| noise machines, of 200 (CANNOT is right) | 192 | 192 | 192 |

- **It is not just repeated points:** on the 612 later meetings where no question repeats a point she has seen, 545 against the swarm's 489 (p = 1 × 10⁻¹⁰).
- **By meeting:** the swarm stays near 80%; with the queen it goes 80.5, 87.5, 90.5, 90.0, 91.0%.
- **Memory:** 143 KB of examples on the big device at the end; 4,455 bytes sent down to all the machines together.
- **Not faster in total:** what goes up to the queen is the hard part. What is fast is the edge.

## Honest limits

- The worlds are made of the brain's own kind of rule (short chains, rules in pieces, branches), without measurement noise. They are not a real fleet's data.
- The queen is told which machine a meeting belongs to.
- The brains were program runs on one computer, not 129 chips, and no message was lost.
- Two changes were made after looking at earlier worlds; the test world was made afterwards. One test world, drawn once.
- Its code is not published.
