/* The edai brain (the library in ../brain, unchanged) on windows of NASA spacecraft telemetry.

   Standard input, one window per line (whole numbers):
       <id> R <n> x1 .. xn y1 .. yn <nq> q1 [q2]      a rule y = f(x): n examples, nq questions
       <id> S <n> t1 .. tn                             a sequence: n terms, asks the next two
   Standard output, one line per window:
       <id> by=<AM|SPLITTER|NET|AMEST|CANNOT> ans=<a,b|CANNOT> [check=<thousandths> est=<e1,e2>] ns=<nanoseconds>
     by     who answered: AM (an exact rule, proved), SPLITTER (an exact rule in pieces), NET (the net's estimate, passed
            its self-check), AMEST (a rule of AM's that fits all but the one or two examples the net doubted), CANNOT
            (no rule, and the net's self-check failed)
     check  when the net ran: the share of its hidden examples it guessed, in thousandths
     est    when the net ran: its two estimates, even when it then said CANNOT
     ns     the time of the solve call

   make        (or: cc -std=c11 -O2 -I../brain/include nasa_run.c ../brain/lib/macos-arm64/libaa.a -o nasa_run) */
#define _DARWIN_C_SOURCE 1
#define _POSIX_C_SOURCE 200809L
#include <inttypes.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "aa.h"

static aa_brain brain;

static uint64_t now_ns(void)
{
    struct timespec t;
#ifdef CLOCK_MONOTONIC_RAW
    clock_gettime(CLOCK_MONOTONIC_RAW, &t);     /* nanoseconds on macOS (CLOCK_MONOTONIC counts whole microseconds) */
#else
    clock_gettime(CLOCK_MONOTONIC, &t);
#endif
    return (uint64_t)t.tv_sec * 1000000000u + (uint64_t)t.tv_nsec;
}

int main(void)
{
    static const char *BY[5] = { "CANNOT", "AM", "SPLITTER", "NET", "AMEST" };
    if (aa_brain_init(&brain) != AA_OK) { fprintf(stderr, "the brain did not start\n"); return 1; }
    char id[64], kind[4]; int n;
    while (scanf("%63s %3s %d", id, kind, &n) == 3) {
        int64_t x[AA_MAX_EXAMPLES], y[AA_MAX_EXAMPLES], q[AA_MAX_QUESTIONS] = { 0, 0 };
        int nq = 0, ok = n >= 1 && n <= AA_MAX_EXAMPLES, seq = kind[0] == 'S';
        for (int i = 0; ok && i < n; i++) ok = scanf("%" SCNd64, &x[i]) == 1;
        if (!seq) {
            for (int i = 0; ok && i < n; i++) ok = scanf("%" SCNd64, &y[i]) == 1;
            ok = ok && scanf("%d", &nq) == 1 && nq >= 1 && nq <= AA_MAX_QUESTIONS;
            for (int j = 0; ok && j < nq; j++) ok = scanf("%" SCNd64, &q[j]) == 1;
        }
        if (!ok) { printf("%s error=input\n", id); fflush(stdout); return 2; }
        aa_answer a;
        uint64_t t0 = now_ns();
        int32_t rc = seq ? aa_solve_sequence(&brain, x, n, &a) : aa_solve_rule(&brain, x, y, n, q, nq, &a);
        uint64_t t1 = now_ns();
        if (rc != AA_OK) { printf("%s error=%d\n", id, (int)rc); fflush(stdout); continue; }
        printf("%s by=%s", id, (a.by >= 0 && a.by <= 4) ? BY[a.by] : "?");
        if (a.by == AA_CANNOT) printf(" ans=CANNOT");
        else printf(" ans=%" PRId64 ",%" PRId64, a.value[0], a.value[1]);
        if (a.learned) printf(" check=%d est=%" PRId64 ",%" PRId64, (int)(a.self_check * 1000.0f + 0.5f), a.estimate[0], a.estimate[1]);
        printf(" ns=%" PRIu64 "\n", t1 - t0);
        fflush(stdout);
    }
    return 0;
}
