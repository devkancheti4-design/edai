/* The CI's check of the compiled brain (check.c), and what each platform gives it: host.c on a computer, bare.c on an
   emulated microcontroller. */
#ifndef CI_CHECK_H
#define CI_CHECK_H
#include <stdint.h>

/* prints one line of text (it ends with a newline) */
void ci_out(const char *line);
/* runs fn and gives back its result, with the bytes of stack it used in *stack_used */
int32_t ci_measure(int32_t (*fn)(void), uint32_t *stack_used);
/* the whole check: prints every line, and returns 0 if every answer and code is the one expected */
int ci_run(void);

#endif
