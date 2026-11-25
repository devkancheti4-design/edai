# Video shots as exact maths

A photo-realistic shot's maths (where, when, how big, what rhythm) as a few bytes that every chip turns back into **every frame's numbers, identically**. The shots are from
[am-math3d](https://github.com/devkancheti4-design/am-math3d), which locks a shot as numbers before a video model draws it.

**In short:**

- **Four locked shots in 394 bytes:** the chess slide in 166, the mouse's plate leap and pan jump in 104 each, the drummers' beat in 12. Their locked plans are 9 to 23 KB, their guide videos 0.1 to 8.5 MB.
- **Every frame, exactly:** chess 91 of 91 rows, every number the locked plan's; plate leap and pan jump 97 of 97 rows each, every number bit for bit; beat 96 of 96 frames.
- **The verdicts, the same as the records':** four real generated takes, judged by rules locked before they were made: two pass (the chess slide, the drummers' beat), two fail (the orange-cat take, the
  15-second ad).
- **The same on every chip:** all **580 lines** identical on a Mac, in WebAssembly, in a browser, on an **iPhone** and on a **real $4 Raspberry Pi Pico**.
- **Fast and small:** on the Pico every frame of the four shots takes 30 ms in all, and all four verdicts 8.6 ms. On the iPhone the 381 frames take 15 ms.

| Shot | In bytes | Locked plan | Guide video | Checked against | Result |
|---|---|---|---|---|---|
| Chess slide | **166** | 15,023 | 225,625 | every number of the plan's 91 rows | all the same |
| Mouse plate leap | **104** | 22,830 | 223,718 | every number of the plan's 97 rows | bit for bit |
| Mouse pan jump | **104** | 20,340 | 105,176 | the same | bit for bit |
| Drummers' beat | **12** | 9,073 | 8,488,170 | every guide frame's source frames and weights | 96 of 96 |

| Take | Rule, locked before | Verdict |
|---|---|---|
| Chess slide | within 5 px at every frame and at the end | **PASS**: median 1.69, worst 3.43, end 1.49 px |
| Chess, orange-cat prompt | the same | **FAIL**: worst 26.9 px |
| Drummers' beat | repeats best at 13 ± 1 frames | **PASS**: 14 frames |
| 15-second ad | within 8 px at every frame, over the plan's length | **FAIL**: worst 15.92 px, and 4.04 s of 14.97 s |

| Where | Lines the same as the Mac's | Time of the 381 frames |
|---|---|---|
| WebAssembly (node) | 580 of 580 | |
| a browser on the Mac | 580 of 580 | 9.2 ms |
| iPhone (Safari) | 580 of 580 | 15.0 ms |
| Raspberry Pi Pico (125 MHz, no floating-point unit) | 580 of 580 | 29.9 ms |

**What it means, exactly:** the shot's control becomes bytes. The look (fur, light, textures) still comes from the clip or the video model's take. This proves the control part of a photo-realistic shot, not
that its pixels became bytes. Its code is not published.
