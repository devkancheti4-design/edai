/* The CI's check of the compiled brain, through its public header only (brain/include/aa.h).

   The same program runs on Linux (host.c) and on emulated Cortex-M chips (bare.c), and every target must print the
   lines in expected.txt:
   - the README's example;
   - 14 problems of the earlier 300-problem challenge that between them get every kind of answer: AM, its splitter, the
     net, AM's estimate and CANNOT, on rules and on sequences;
   - the online learner, 600 steps;
   - the documented error codes.
   Floating-point results are printed as their bits, so "the same line" means the same answer bit for bit.  Lines that
   differ by target by design start with TARGET or STACK and are not compared. */
#include <stdint.h>
#include "aa.h"
#include "check.h"

typedef struct {
    const char *id;
    int seq;                    /* 0: a rule y = f(x), from x, y and the questions q; 1: a sequence, its terms in y */
    int n;
    int64_t x[12], y[12], q[2];
} ci_problem;

static const ci_problem PROBLEMS[] = {
    { "readme", 0, 8, {55, 68, 19, 29, 95, 4, 92, 13}, {440, 544, 152, 232, 760, 32, 736, 104}, {111, 118} },
    { "p000", 0, 12, {6, 34, -20, 71, 67, 29, -12, 58, 73, 16, 41, 35}, {222, 166, 289, 53, 68, 159, 278, 98, 62, 197, 132, 146}, {12, 14} },
    { "p001", 0, 12, {98, 16, -3, -5, 24, 114, 101, 119, 7, 62, 70, 2}, {322, 420, -305, -2, 137, 75, 376, 159, -218, -311, 285, -269}, {-15, -7} },
    { "p002", 0, 8, {56, 2, 41, 24, 55, 9, 79, 68}, {224, 20, 164, 96, 220, 36, 316, 272}, {107, 115} },
    { "p095", 0, 8, {35, 85, 67, 6, 118, 115, 95, 38}, {-98, -263, -196, 6, -374, -359, -268, -118}, {24, 116} },
    { "p099", 0, 8, {-17, 46, 31, 54, 13, 23, 0, -15}, {-263, 2, -1, 496, 77, -372, 463, 346}, {70, 119} },
    { "p105", 0, 8, {15, -12, 12, 75, -29, 64, 80, -13}, {9025, 8836, 5476, 265225, 45369, 191844, 302500, 10201}, {109, 114} },
    { "p193", 0, 12, {89, 39, 73, 81, 0, 104, -15, 44, 23, 25, -18, 3}, {178, 78, 146, 162, 8, 208, 8, 88, 46, 50, 8, 8}, {119, 114} },
    { "p199", 0, 12, {60, 0, 32, 111, 66, 88, 5, 89, 95, -29, 52, 42}, {189, 296, 260, 88, 177, 113, 302, 108, 88, 296, 212, 237}, {25, 91} },
    { "p213", 0, 12, {7, -40, 71, 119, 16, -39, 40, 41, 5, 51, -20, -31}, {5, -453, 21, -205, 284, -407, -274, 303, 151, -42, -82, -449}, {104, 60} },
    { "p005", 0, 12, {-1, 111, 2, 27, 11, 16, -4, 6, 34, 94, -14, 45}, {-2, 108, 20, 24, 8, 160, -40, 60, 340, 940, -140, 42}, {18, 68} },
    { "p166", 0, 8, {-19, -9, 62, 40, 41, 11, 71, 72}, {25, 17, 0, 0, 0, 9, 17, 0}, {77, 113} },
    { "p021", 1, 8, {0}, {1, 3, 0, 0, -3, -9, -12, -36}, {0, 0} },
    { "p111", 1, 8, {0}, {-10, -21, -44, -85, -150, -245, -376, -549}, {0, 0} },
    { "p004", 1, 8, {0}, {168, -95, 81, 63, -298, 116, 30, 237}, {0, 0} },
};
#define N_PROBLEMS ((int)(sizeof PROBLEMS / sizeof PROBLEMS[0]))

/* the brain and the online learner are used one after the other, so they share their memory (both fit a Cortex-M0's
   16 KB with the stack) */
static union { aa_brain brain; aa_stream stream; } mem;

/* ---- text, without the C library (some small C libraries cannot print 64-bit numbers) ---- */
static char *put(char *p, const char *s) { while (*s) *p++ = *s++; *p = 0; return p; }
static char *put_i64(char *p, int64_t v)
{
    char tmp[24]; int n = 0;
    uint64_t u = v < 0 ? (uint64_t)0 - (uint64_t)v : (uint64_t)v;
    do { tmp[n++] = (char)('0' + (int)(u % 10)); u /= 10; } while (u);
    if (v < 0) *p++ = '-';
    while (n) *p++ = tmp[--n];
    *p = 0;
    return p;
}
static char *put_hex(char *p, uint32_t v)
{
    for (int k = 28; k >= 0; k -= 4) *p++ = "0123456789abcdef"[(v >> k) & 15u];
    *p = 0;
    return p;
}
static uint32_t bits(float f) { union { float f; uint32_t u; } c; c.f = f; return c.u; }

/* ---- one solve, measured ---- */
static const ci_problem *cur;
static aa_answer ans;
static int32_t solve_cur(void)
{
    if (cur->seq) return aa_solve_sequence(&mem.brain, cur->y, cur->n, &ans);
    return aa_solve_rule(&mem.brain, cur->x, cur->y, cur->n, cur->q, 2, &ans);
}

int ci_run(void)
{
    static const char *BY[5] = { "CANNOT", "AM", "SPLITTER", "NET", "AM_EST" };
    char line[256], *p;
    int failed = 0;
    uint32_t worst = 0;
    aa_info_t info;

    aa_info(&info);
    p = put(line, "TARGET "); p = put(p, info.target); p = put(p, ", the library's own stack bound ");
    p = put_i64(p, info.stack_bytes); put(p, " bytes\n"); ci_out(line);
    {
        uint32_t v = aa_version();
        p = put(line, "version "); p = put_i64(p, v >> 16); p = put(p, "."); p = put_i64(p, (v >> 8) & 255u);
        p = put(p, "."); p = put_i64(p, v & 255u); p = put(p, " brain="); p = put_i64(p, info.brain_bytes);
        p = put(p, " stream="); p = put_i64(p, info.stream_bytes); p = put(p, " header="); p = put_i64(p, AA_VERSION);
        put(p, "\n"); ci_out(line);
        if (v != (uint32_t)AA_VERSION || info.brain_bytes != AA_BRAIN_BYTES || info.stream_bytes != AA_STREAM_BYTES) failed = 1;
    }

    /* the problems */
    if (aa_brain_init(&mem.brain) != AA_OK) { ci_out("the brain did not start\n"); return 1; }
    for (int i = 0; i < N_PROBLEMS; i++) {
        uint32_t used = 0;
        int32_t rc;
        unsigned char *a = (unsigned char *)&ans;
        for (unsigned k = 0; k < sizeof ans; k++) a[k] = 0;
        cur = &PROBLEMS[i];
        rc = ci_measure(solve_cur, &used);
        if (used > worst) worst = used;
        p = put(line, cur->id); p = put(p, cur->seq ? " seq " : " rule");
        if (rc != AA_OK) { p = put(p, " error="); p = put_i64(p, rc); failed = 1; }
        else {
            p = put(p, " by="); p = put(p, (ans.by >= 0 && ans.by <= 4) ? BY[ans.by] : "?");
            p = put(p, " ans=");
            if (ans.by == AA_CANNOT) p = put(p, "CANNOT");
            else { p = put_i64(p, ans.value[0]); p = put(p, ","); p = put_i64(p, ans.value[1]); }
            if (ans.learned) {
                p = put(p, " check="); p = put_i64(p, (int64_t)(ans.self_check * 1000.0f + 0.5f));
                p = put(p, " est="); p = put_i64(p, ans.estimate[0]); p = put(p, ","); p = put_i64(p, ans.estimate[1]);
            }
            p = put(p, " bits="); p = put_hex(p, bits(ans.self_check)); p = put(p, ","); p = put_hex(p, bits(ans.fit));
        }
        put(p, "\n"); ci_out(line);
        if (i == 0 && !(rc == AA_OK && ans.by == AA_AM && ans.value[0] == 888 && ans.value[1] == 944)) failed = 1;
    }

    /* the online learner: y = 0.25 + 0.5 a - 0.25 b on a fixed grid, 600 steps */
    {
        aa_stream_config c;
        uint32_t sum = 2166136261u, count = 0;
        float before = 0, pred[3] = { 0, 0, 0 };
        aa_stream_defaults(&c);
        c.in_lo[0] = 0; c.in_hi[0] = 1; c.in_lo[1] = 0; c.in_hi[1] = 1; c.out_lo = 0; c.out_hi = 1;
        if (aa_stream_init(&mem.stream, &c) != AA_OK) { ci_out("the learner did not start\n"); return 1; }
        for (int i = 0; i < 600; i++) {
            const float in0 = (float)(i % 17) * 0.0625f, in1 = (float)((i * 5) % 13) * 0.0625f;
            const float target = 0.25f + 0.5f * in0 - 0.25f * in1;
            if (aa_observe(&mem.stream, in0, in1, target, &before) != AA_OK) failed = 1;
            sum = (sum ^ bits(before)) * 16777619u;
        }
        aa_predict(&mem.stream, 0.0f, 0.0f, &pred[0]);
        aa_predict(&mem.stream, 0.5f, 0.25f, &pred[1]);
        aa_predict(&mem.stream, 1.0f, 0.75f, &pred[2]);
        aa_stream_count(&mem.stream, &count);
        p = put(line, "stream count="); p = put_i64(p, count); p = put(p, " sum="); p = put_hex(p, sum);
        p = put(p, " predictions="); p = put_hex(p, bits(pred[0])); p = put(p, ","); p = put_hex(p, bits(pred[1]));
        p = put(p, ","); p = put_hex(p, bits(pred[2])); put(p, "\n"); ci_out(line);
    }

    /* the documented error codes */
    {
        static const int64_t X[2] = { 1, 2 }, Q[2] = { 3, 4 };
        aa_answer a;
        int32_t got[8], want[8] = { AA_ERR_NULL, AA_ERR_RANGE, AA_ERR_RANGE, AA_ERR_RANGE, AA_ERR_RANGE, AA_ERR_INIT,
                                    AA_ERR_VERSION, AA_ERR_NULL };
        static const char *NAME[8] = { "null", "n0", "n17", "nq3", "seq2", "uninit", "version", "info" };
        aa_brain_init(&mem.brain);
        got[0] = aa_solve_rule((aa_brain *)0, X, X, 2, Q, 2, &a);
        got[1] = aa_solve_rule(&mem.brain, X, X, 0, Q, 2, &a);
        got[2] = aa_solve_rule(&mem.brain, X, X, 17, Q, 2, &a);
        got[3] = aa_solve_rule(&mem.brain, X, X, 2, Q, 3, &a);
        got[4] = aa_solve_sequence(&mem.brain, X, 2, &a);
        {
            unsigned char *b = (unsigned char *)&mem.brain;
            for (unsigned k = 0; k < sizeof mem.brain; k++) b[k] = 0;
            got[5] = aa_solve_rule(&mem.brain, X, X, 2, Q, 2, &a);
        }
        got[6] = aa_brain_init_(&mem.brain, 0x00090000u, (uint32_t)sizeof mem.brain);
        got[7] = aa_info((aa_info_t *)0);
        p = put(line, "errors");
        for (int k = 0; k < 8; k++) {
            p = put(p, " "); p = put(p, NAME[k]); p = put(p, "="); p = put_i64(p, got[k]);
            if (got[k] != want[k]) failed = 1;
        }
        put(p, "\n"); ci_out(line);
    }

    p = put(line, "STACK most used by one call: "); p = put_i64(p, worst); p = put(p, " bytes, ");
    p = put(p, worst <= AA_STACK_BYTES ? "within" : "OVER"); p = put(p, " the promise of "); p = put_i64(p, AA_STACK_BYTES);
    put(p, " bytes\n"); ci_out(line);
    if (worst > AA_STACK_BYTES) failed = 1;
    ci_out(failed ? "FAILED\n" : "DONE\n");
    return failed;
}
