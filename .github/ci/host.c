/* The check on a computer: lines to standard output, and each solve run on a thread of its own, on a stack of ours.
   Just before the call the thread fills everything below its stack pointer with a pattern (its start-up code may have
   used that memory already), and as soon as the call returns it finds the deepest byte that changed: the distance from
   the stack pointer at the call is the stack the call used.
       cc -std=c11 -O2 -ffp-contract=off -I../../brain/include check.c host.c ../../brain/lib/<target>/libaa.a -lpthread */
#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stddef.h>
#include <stdio.h>
#include "check.h"

void ci_out(const char *line) { fputs(line, stdout); fflush(stdout); }

#define STACK_SIZE (256 * 1024)
#define MARGIN 256                       /* left alone just below the stack pointer: a red zone is at most 128 bytes */
static _Alignas(16384) unsigned char stack_area[STACK_SIZE];
static int32_t (*job)(void);
static int32_t job_result;
static uintptr_t job_used;

static uintptr_t stack_pointer(void)
{
    uintptr_t sp;
#if defined(__x86_64__)
    __asm__ volatile ("mov %%rsp, %0" : "=r"(sp));
#elif defined(__aarch64__)
    __asm__ volatile ("mov %0, sp" : "=r"(sp));
#else
    sp = (uintptr_t)__builtin_frame_address(0);
#endif
    return sp;
}

static void *thread_main(void *arg)
{
    const uintptr_t sp = stack_pointer();
    volatile unsigned char *p;
    size_t i = 0;
    (void)arg;
    for (p = stack_area; (uintptr_t)p < sp - MARGIN; p++) *p = 0xA5;    /* volatile: a plain loop, never a call */
    job_result = job();
    while (i < sizeof stack_area && stack_area[i] == 0xA5) i++;          /* the stack grows down */
    job_used = sp > (uintptr_t)(stack_area + i) ? sp - (uintptr_t)(stack_area + i) : 0;
    return NULL;
}

int32_t ci_measure(int32_t (*fn)(void), uint32_t *stack_used)
{
    pthread_attr_t attr;
    pthread_t thread;
    job = fn;
    job_used = 0;
    if (pthread_attr_init(&attr) != 0 || pthread_attr_setstack(&attr, stack_area, sizeof stack_area) != 0 ||
        pthread_create(&thread, &attr, thread_main, NULL) != 0) {
        fputs("could not start a thread on our own stack\n", stdout);
        *stack_used = 0;
        return fn();
    }
    pthread_join(thread, NULL);
    pthread_attr_destroy(&attr);
    *stack_used = (uint32_t)job_used;
    return job_result;
}

int main(void) { return ci_run(); }
