### Flight A: a circle at 20 m; a flipped roll gain arrives at 14.0 s

| | Unprotected | Guarded |
|---|---|---|
| The update | installed at 14.5 s | installed at 14.2 s, **caught at 14.2 s**: roll_torque: 24000 of 24001 wrong |
| Control | lost (past 80 degrees) at 15.0 s | never lost: at most 15 degrees of tilt |
| End | hit the ground at 17.1 s, at 16 m/s | flew on; 3,958 wrong outputs replaced; the ground pressed Revert at 30.0 s |

How steady the guarded drone was, as its distance from the moving point it was told to follow:

- before the update (8 to 14 s): 1.25 m on average, 1.50 m at worst
- with the broken update on board, held (14.3 to 30 s): 1.24 m on average, 1.71 m at worst
- after Revert (30.1 to 45 s): 1.52 m on average, 2.31 m at worst

### Flight B: out to 420 m on a battery of 100 seconds; a flipped battery-reserve sign arrives at 4.0 s

| | Unprotected | Guarded |
|---|---|---|
| The update | installed at 4.4 s | installed at 4.3 s, **caught at 4.3 s**: reserve_pct: 200 of 201 wrong |
| Going home | never: the flipped law asks for -32% at 420 m | at 26.3 s: Battery 63%, reserve law 64%: going home |
| End | PX4's own failsafe began to land at 89.6 s, 420 m from home; battery 0% at 90.4 s, 19 m up; **hit the ground at 93.8 s, at 14 m/s** | landed **0.5 m from home with 14% left** (1.1 m/s at touch-down, motors off at 77.2 s) |

### 26 different broken updates, each flown by both drones

- Unprotected: **20 crashed**, 3 went out of control or off course (past 80 degrees or 12 m off, still in the air when the flight ended), 3 flew on.
- Guarded: **26 of 26 flew on or came home**; 26 of 26 caught as the update loaded.
- The guarded drones on the circle were at worst 1.9 m from their moving point (with a harmless update, either drone: at worst 1.9 m); those on the battery flight landed with 14% to 15% left.
- The unprotected drones that crashed hit the ground at 6 to 16 m/s.
- 3 updates rewritten with the same answers: 3 of 3 recognised, no alert, nothing replaced.

| Law | The bug | Unprotected | Guarded |
|---|---|---|---|
| `gyro_mrad` | shift the wrong way: 16 times too big: `raw * 3 << 2` | off course (77.7 m, tilt 14°) | flew on (1.8 m) |
| `gyro_mrad` | sign flipped: `raw * -3 >> 2` | crashed, 16 m/s | flew on (1.8 m) |
| `gyro_mrad` | twice too big: `raw * 3 >> 1` | flew on (10.4 m) | flew on (1.9 m) |
| `gyro_mrad` | ten times too big: `raw * 30 >> 2` | off course (83.9 m, tilt 10°) | flew on (1.8 m) |
| `gyro_mrad` | a factor dropped: a third: `raw >> 2` | crashed, 9 m/s | flew on (1.9 m) |
| `gyro_mrad` | a quarter: `raw * 3 >> 4` | crashed, 13 m/s | flew on (1.8 m) |
| `gyro_mrad` | cut to 8 bits: `raw * 3 >> 2 & 255` | crashed, 16 m/s | flew on (1.9 m) |
| `roll_torque` | sign flipped: `err * -12 * 12` | crashed, 16 m/s | flew on (1.8 m) |
| `roll_torque` | ten times too big: `err * 12 * 12 * 10` | flew on (1.4 m) | flew on (1.7 m) |
| `roll_torque` | a factor dropped: a twelfth: `err * 12` | crashed, 11 m/s | flew on (1.9 m) |
| `roll_torque` | * became +: `err * 12 + 12` | crashed, 9 m/s | flew on (1.7 m) |
| `roll_torque` | always nothing: `0` | crashed, 16 m/s | flew on (1.9 m) |
| `roll_torque` | * became /: `err * 12 / 12` | crashed, 13 m/s | flew on (1.8 m) |
| `pitch_torque` | sign flipped: `err * -12 * 12` | crashed, 16 m/s | flew on (1.9 m) |
| `pitch_torque` | ten times too big: `err * 12 * 12 * 10` | flew on (1.9 m) | flew on (1.8 m) |
| `pitch_torque` | a factor dropped: a twelfth: `err * 12` | crashed, 6 m/s | flew on (1.7 m) |
| `pitch_torque` | * became +: `err * 12 + 12` | off course (35.4 m, tilt 146°) | flew on (1.7 m) |
| `pitch_torque` | always nothing: `0` | crashed, 11 m/s | flew on (1.7 m) |
| `pitch_torque` | * became /: `err * 12 / 12` | crashed, 15 m/s | flew on (1.8 m) |
| `reserve_pct` | sign flipped: `(8 - dist) * 4` | crashed, 14 m/s | home with 14% |
| `reserve_pct` | * became /: `(dist + 8) / 4` | crashed, 15 m/s | home with 15% |
| `reserve_pct` | a factor dropped: `dist + 8` | crashed, 14 m/s | home with 14% |
| `reserve_pct` | + became -: `(dist - 8) * 4` | crashed, 14 m/s | home with 14% |
| `reserve_pct` | always nothing: `0` | crashed, 14 m/s | home with 14% |
| `reserve_pct` | the fixed part dropped: `dist * 4` | crashed, 13 m/s | home with 15% |
| `reserve_pct` | the whole sign flipped: `-((dist + 8) * 4)` | crashed, 14 m/s | home with 15% |
