/* The check on a computer: lines to standard output, and each solve run on a thread whose stack is filled with a
   pattern first, so that afterwards the deepest byte it changed shows the stack it used.  The library's share is that
   depth less the depth of an empty call through the same path.
       cc -std=c11 -O2 -ffp-contract=off -I../../brain/include check.c host.c ../../brain/lib/<target>/libaa.a -lpthread */
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdio.h>
#include <string.h>
#include "check.h"

void ci_out(const char *line) { fputs(line, stdout); fflush(stdout); }

#define STACK_SIZE (256 * 1024)
static _Alignas(16384) unsigned char stack_area[STACK_SIZE];
static int32_t (*job)(void);
static int32_t job_result;

static void *thread_main(void *arg)
{
    (void)arg;
    job_result = job ? job() : 0;
    return NULL;
}

/* the bytes of stack_area the thread changed, counted from its top (the stack grows down) */
static uint32_t run_on_painted_stack(int32_t (*fn)(void))
{
    pthread_attr_t attr;
    pthread_t thread;
    size_t i = 0;
    memset(stack_area, 0xA5, sizeof stack_area);
    job = fn;
    if (pthread_attr_init(&attr) != 0 || pthread_attr_setstack(&attr, stack_area, sizeof stack_area) != 0 ||
        pthread_create(&thread, &attr, thread_main, NULL) != 0) {
        fputs("could not start a thread on the painted stack\n", stdout);
        job_result = fn ? fn() : 0;
        return 0;
    }
    pthread_join(thread, NULL);
    pthread_attr_destroy(&attr);
    while (i < sizeof stack_area && stack_area[i] == 0xA5) i++;
    return (uint32_t)(sizeof stack_area - i);
}

int32_t ci_measure(int32_t (*fn)(void), uint32_t *stack_used)
{
    static uint32_t empty_call;
    static int measured_empty;
    uint32_t used;
    if (!measured_empty) { empty_call = run_on_painted_stack(NULL); measured_empty = 1; }
    used = run_on_painted_stack(fn);
    *stack_used = used > empty_call ? used - empty_call : 0;
    return job_result;
}

int main(void) { return ci_run(); }
