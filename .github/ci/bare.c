/* The check on an emulated Cortex-M under QEMU: lines through Arm semihosting (bkpt 0xAB), and the stack each solve
   uses measured by filling the free stack below the caller with a pattern first and finding afterwards the deepest
   byte that changed.  Built with startup_cortex_m.c and the board's linker script; QEMU exits when the check ends. */
#include <stdint.h>
#include "check.h"

static int semihost(int op, const void *arg)
{
    register int r0 __asm__("r0") = op;
    register const void *r1 __asm__("r1") = arg;
    __asm__ volatile ("bkpt 0xAB" : "+r"(r0) : "r"(r1) : "memory");
    return r0;
}

void ci_out(const char *line) { semihost(0x04, line); }      /* SYS_WRITE0 */

extern uint8_t __bss_end[];
#define PAINT 6144u                                           /* about twice the most any call may use */

int32_t ci_measure(int32_t (*fn)(void), uint32_t *stack_used)
{
    uint8_t *sp;
    volatile uint8_t *lo, *top, *p;
    int32_t result;
    __asm__ volatile ("mov %0, sp" : "=r"(sp));
    top = (volatile uint8_t *)(sp - 64);
    lo = (volatile uint8_t *)(sp - PAINT);
    if (lo < (volatile uint8_t *)(__bss_end + 16)) lo = (volatile uint8_t *)(__bss_end + 16);
    for (p = lo; p < top; p++) *p = 0xA5;                     /* volatile: a plain loop, never a call to memset */
    result = fn();
    for (p = lo; p < top && *p == 0xA5; p++) {}
    *stack_used = (uint32_t)(sp - (uint8_t *)(uintptr_t)p);
    return result;
}

int main(void)
{
    static const uint32_t exit_block[2] = { 0x20026, 0 };      /* ADP_Stopped_ApplicationExit, status 0 */
    (void)ci_run();
    semihost(0x18, (const void *)0x20026);                     /* SYS_EXIT */
    semihost(0x20, exit_block);                                /* SYS_EXIT_EXTENDED, where SYS_EXIT needs a block */
    for (;;) {}
}
