/* Minimal start-up for a Cortex-M under QEMU: the vector table, the FPU switched on (where there is one), .data copied
   from flash, .bss cleared, then main().  A fault stops QEMU at once through semihosting.  For a real board, use your
   vendor's start-up code instead (Pico SDK, STM32Cube, nRF SDK): the brain needs nothing from it except the FPU
   switched on before the first call. */
#include <stdint.h>

extern uint32_t __data_load[], __data_start[], __data_end[], __bss_start[], __bss_end[], __stack_top[];
int main(void);
void Reset_Handler(void);

static void Default_Handler(void)
{
    static const char message[] = "FAULT: the chip stopped with a fault\n";
    register int r0 __asm__("r0") = 0x04;                       /* SYS_WRITE0 */
    register const void *r1 __asm__("r1") = message;
    __asm__ volatile ("bkpt 0xAB" : "+r"(r0) : "r"(r1) : "memory");
    r0 = 0x18;                                                  /* SYS_EXIT */
    r1 = (const void *)0x20023;                                 /* ADP_Stopped_RunTimeErrorUnknown */
    __asm__ volatile ("bkpt 0xAB" : "+r"(r0) : "r"(r1) : "memory");
    for (;;) {}
}

__attribute__((section(".vectors"), used)) static const uintptr_t vectors[16] = {
    (uintptr_t)__stack_top, (uintptr_t)Reset_Handler,
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,      /* NMI, HardFault */
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,      /* MemManage, BusFault */
    (uintptr_t)Default_Handler, 0, 0, 0, 0,                      /* UsageFault, reserved */
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler, 0,   /* SVCall, DebugMonitor, reserved */
    (uintptr_t)Default_Handler, (uintptr_t)Default_Handler,      /* PendSV, SysTick */
};

void Reset_Handler(void)
{
#if defined(__ARM_FP)
    *(volatile uint32_t *)0xE000ED88u |= 0xFu << 20;            /* CPACR: full access to CP10 and CP11, the FPU */
    __asm__ volatile ("dsb\n\tisb" ::: "memory");
#endif
    for (uint32_t *s = __data_load, *d = __data_start; d < __data_end;) *d++ = *s++;
    for (uint32_t *d = __bss_start; d < __bss_end;) *d++ = 0;
    main();
    for (;;) {}
}
