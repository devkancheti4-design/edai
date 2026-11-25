- **The brain on the chip** learned the four laws from their own answers and proved them on all 80,971 inputs in **0.93 s**: the same 21 bytes as on the Mac.
- **26 of 26 broken updates caught** as they loaded, 3 of 3 harmless rewrites trusted; the check of all 80,971 inputs takes **0.41 s**, on the second core, while the first one flies on.
- **Every answer the same as the Mac's:** 8,420,984 answers hashed, 454 of 454 result lines equal.
- Updates damaged on the way (one bit flipped): 83 of 83 refused.
- A check takes 5.1 to 5.8 microseconds.

### On the chip: the flipped roll gain (72 bytes of machine code) at 14.0 s

| | Unprotected | Guarded |
|---|---|---|
| The update | installed at 14.1 s | installed at 14.5 s, **caught at 14.5 s**: roll_torque: 24000 of 24001 wrong |
| Control | lost (past 80 degrees) at 14.6 s | never lost: at most 15 degrees of tilt |
| End | hit the ground at 16.7 s, at 16 m/s | flew on; 3,892 wrong outputs replaced; the ground pressed Revert at 30.0 s |

How steady the guarded drone was, as its distance from the moving point it was told to follow:

- before the update (8 to 14 s): 1.25 m on average, 1.45 m at worst
- with the broken update on board, held (14.6 to 30 s): 1.31 m on average, 1.82 m at worst
- after Revert (30.1 to 45 s): 1.56 m on average, 2.27 m at worst

Guarded: the chip answered 79,098 flight calls and replaced 3,892; a call (the law and its check) took 8.7 microseconds on average, 43 at most. Unprotected: the chip answered 46,278 flight calls and replaced 0; a call (the law and its check) took 0.5 microseconds on average, 6 at most.

### On the chip: the flipped battery-reserve sign at 4.0 s

| | Unprotected | Guarded |
|---|---|---|
| The update | installed at 4.1 s | installed at 4.4 s, **caught at 4.5 s**: reserve_pct: 200 of 201 wrong |
| Going home | never: the flipped law asks for -32% at 420 m | at 25.3 s: Battery 59%, reserve law 60%: going home |
| End | PX4's own failsafe began to land at 88.3 s, 420 m from home; battery 0% at 89.7 s, 18 m up; **hit the ground at 93.2 s, at 14 m/s** | landed **0.9 m from home with 10% left** (1.4 m/s at touch-down, motors off at 76.6 s) |

Guarded: the chip answered 130,712 flight calls and replaced 912; a call (the law and its check) took 8.7 microseconds on average, 43 at most. Unprotected: the chip answered 147,010 flight calls and replaced 0; a call (the law and its check) took 0.3 microseconds on average, 5 at most.

### On the chip: the gyro scaling bug (16 times too big) at 14.0 s

| | Unprotected | Guarded |
|---|---|---|
| The update | installed at 14.1 s | installed at 14.4 s, **caught at 14.5 s**: gyro_mrad: 32767 of 32768 wrong |
| Control | at most 14 degrees of tilt | never lost: at most 14 degrees of tilt |
| End | off its path by up to 192.8 m, still in the air when the flight ended | flew on; 11,629 wrong outputs replaced; the ground pressed Revert at 30.0 s |

How steady the guarded drone was, as its distance from the moving point it was told to follow:

- before the update (8 to 14 s): 1.22 m on average, 1.42 m at worst
- with the broken update on board, held (14.6 to 30 s): 1.27 m on average, 1.75 m at worst
- after Revert (30.1 to 45 s): 1.45 m on average, 2.06 m at worst

Guarded: the chip answered 79,913 flight calls and replaced 11,629; a call (the law and its check) took 8.7 microseconds on average, 45 at most. Unprotected: the chip answered 80,914 flight calls and replaced 0; a call (the law and its check) took 0.4 microseconds on average, 4 at most.

