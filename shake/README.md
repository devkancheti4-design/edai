# Shake: the big machine learns through the shaking, a $4 chip uses only the rules

Robots shake. A delivery drone vibrates, a dish-washing arm judders, a cleaner bumps along. A small chip reading a
shaky sensor cannot tell a pattern from the shaking on its own. The idea tested here: let a big machine do the
learning, shaking included, and give the small chip only the clean rules. The shaking then never reaches the small
chip's reasoning.

**In short:**

- **The big machine learned every rule through real shaking.** From 43,200 shaky readings of 9 robot jobs (real motor
  vibration on top of each reading), AM found **all 9 rules exactly**, right at every input. Each rule came with its
  noise allowance (10 to 12 units): the most the shaking ever pushed a reading off it. Everything the chip needs, the
  9 rules and their allowances with their checksums, is **100 bytes**.
- **With those 100 bytes, the chip was exactly right every time under normal shaking:** **270 of 270** test windows,
  with **no wrong answer and no false alarm**.
- **Without them, the same chip cannot do it.** Alone, the brain gave no exactly right answer on those windows: the
  shaking breaks every exact rule, so its net estimated (a mean miss of 7.9 units) or it said CANNOT.
- **Faults are flagged, not answered:** 45 of 45 knocks, 45 of 45 stuck sensors, 45 of 45 drifts, 30 of 30 jobs it was
  never taught. With a damaged bearing shaking 4 times harder, 84 of 90 windows were flagged; the other 6, where the
  shaking stayed within the allowance, were answered exactly right. **Across all 525 windows: 0 wrong answers.**
- **On a real Raspberry Pi Pico** (RP2040, 125 MHz, no floating-point unit), **every one of its 543 output lines was
  the same as the computer's**. It answered a window in a median **0.54 ms**. On the same windows, the brain alone took
  a median of **62 s** (it has to learn), about 115,000 times as long, and still only estimated.

## The jobs

Each job is a rule y = f(x). x is what the robot knows exactly (its own step, lane, waypoint or load); y is what a
sensor reads, through the shaking. The chip is never told which job a window comes from: it finds the rule that fits.

| job | robot | what it means | rule | x |
|---|---|---|---|---|
| D1 | drone | parcel weight (× 100 g) → motor boost | 11x + 9 | 1 to 16 |
| D2 | drone | waypoint → distance flown (× 10 m) | 12(x + 3) | 0 to 15 |
| D3 | drone | wind step → tilt | x² + 10 | 0 to 15 |
| K1 | dish robot | cycle step → arm height, repeating every 4 steps | 48 (x mod 4) | 0 to 15 |
| K2 | dish robot | plates in the rack → water (× 10 ml) | 9x + 4 | 1 to 16 |
| K3 | dish robot | scrub pass → brush pressure | 7(x + 5) | 0 to 15 |
| C1 | cleaner | lane → side position, back and forth | 120 (x mod 2) | 0 to 15 |
| C2 | cleaner | lane → distance covered | 96x | 0 to 15 |
| C3 | cleaner | room → suction, every third room the same | 66 (x mod 3) | 0 to 15 |
| (two more) | never taught | new jobs, for the test only | x³ / 16 (curved); 9 (x xor 5) (zigzag) | 0 to 15 |

## The shaking

Real vibration: the drive-end accelerometer of the Case Western Reserve University bearing rig (Bearing Data Center),
sampled at 12 kHz.

- **Normal running** (their recording 97): the first 60% shook the big machine's readings, the last 40% the test
  readings, so the chip never met the shaking the big machine learned from.
- **Harder shaking:** a damaged bearing (their recording 105, an inner-race fault), 4.01 times the normal vibration,
  with sharp knocks.

Each reading took one vibration sample from a random place, scaled so that normal running shakes a reading by 3 units
(one standard deviation, at most about 12). The damaged bearing got the same scale.

## How the big machine learned

For each job: 600 runs of 8 shaky readings, about 300 readings at each x (4,800 per job).

1. **The median reading at each x.** With a few hundred readings it is nearly always the clean value, but not always:
   on D1 the median at x = 6 came out 76 where the rule gives 75.
2. **AM proposes rules** from small sets of those medians, and every rule it proposes is scored on all the job's
   readings. Of the rules within 1% of the best fit, the shortest is kept. (On D1, a longer rule bent through the 76
   fitted a hair better; the 1% margin keeps the true two-step rule.)
3. **The allowance** is the kept rule's largest miss on the training readings.

All 9 kept rules give the true value at every x. Allowances: 12, 10, 12, 10, 10, 10, 11, 10 and 10 units.

## How the chip answers

For a window (8 shaky readings at the robot's own x, and 2 x's to answer), the chip tries each rule. A rule **fits**
when every reading is within the rule's allowance of the rule's value.
- **Answer:** rules fit and all that fit agree. It answers with the rule's own values, exactly.
- **No answer:** rules fit but disagree (this never happened here).
- **Flag:** no rule fits, because some reading is further off than the shaking ever pushed one.

The chip never learns and never searches. It checks the readings against rules found where the shaking could be
averaged away.

## Results

525 test windows:

| kind of window | windows | with the rules: right | wrong | no answer | flagged | alone: exactly right | exact but wrong | net estimates (mean miss) | CANNOT |
|---|---|---|---|---|---|---|---|---|---|
| normal shaking | 270 | **270** | 0 | 0 | 0 | 0 | 3 | 177 (7.9) | 90 |
| harder shaking (damaged bearing) | 90 | 6 | 0 | 0 | **84** | 0 | 0 | 55 (14.9) | 35 |
| a knock on one reading (±40) | 45 | 0 | 0 | 0 | **45** | 0 | 0 | 27 (15.9) | 18 |
| a stuck sensor | 45 | 0 | 0 | 0 | **45** | 0 | **34** | 11 (58.5) | 0 |
| a drift (growing to 36) | 45 | 0 | 0 | 0 | **45** | 0 | 0 | 23 (32.5) | 22 |
| a job never taught | 30 | 0 | 0 | 0 | **30** | 0 | 0 | 15 (12.4) | 15 |

- Every one of the 276 answers used the true job's rule; the chip picked it from the shaky readings alone.
- A stuck sensor looks perfectly regular, so the brain alone gave 34 confident wrong answers on stuck sensors; with
  the rules, every stuck sensor was flagged.
- Requiring an exact fit instead of an allowance, the rules answered 0 of the 525 windows: shaking breaks every exact
  fit. The allowances are what make the rules usable on shaky readings.

## On a real Raspberry Pi Pico

The chip got the 525 windows, the rules and their allowances in flash. It checked all 525 windows with the rules, then
the brain alone on 18 windows (the first 2 normal windows of each job), and sent one line per result over USB.

| | |
|---|---|
| Lines | **543 of 543 the same as the computer's** (525 rule checks, 18 brain-alone answers); 1 port opening, 0 damaged lines |
| With the rules | a median of 0.537 ms a window (0.408 to 1.061 ms); all 525 windows in 266 ms |
| Brain alone | 18 windows: a median of 62.0 s each (58.2 to 68.9 s), 1,129 s in all; 12 net estimates (misses of 1 to 29 units), 6 CANNOT, no exact answer |
| The same 18 windows with the rules | 18 of 18 exactly right, 9.2 ms in all |
| Stack | the brain used 3,012 of the 16,384 bytes it was given |

The chip has no floating-point unit, so the brain alone learns in software, and every check takes about a minute.
With the rules there is nothing to learn and nothing to search, only a few integer steps per rule.

## Honest limits

- **x must be exact**: only the sensor reading (y) may shake. The rules are short integer rules of AM's steps.
- **The allowance is what the big machine saw.** Harder shaking is flagged, not answered (84 of 90), so a robot needs
  a plan for flags: slow down, ask the brain alone, or wait.
- **Rules must differ by more than the shaking** somewhere in the window. The jobs here, and the two never taught, have
  different shapes; a new job very close to a taught one could be taken for it.
- This test ran on the brain's current build, which answers every call of the 1.2 library in `brain/` exactly as 1.2
  does, plus the rule check the test needs. Its code is not published.
