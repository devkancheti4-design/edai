ENTRY(Reset_Handler)
MEMORY { FLASH (rx) : ORIGIN = 0x00000000, LENGTH = 4M
         RAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 4M }
SECTIONS {
  .text : { KEEP(*(.vectors)) *(.text .text.*) *(.rodata .rodata.*) . = ALIGN(4); } > FLASH
  .ARM.exidx : { *(.ARM.exidx*) } > FLASH
  .data : ALIGN(4) { __data_start = .; *(.data .data.*) . = ALIGN(4); __data_end = .; } > RAM AT > FLASH
  __data_load = LOADADDR(.data);
  .bss (NOLOAD) : ALIGN(4) { __bss_start = .; *(.bss .bss.* COMMON) . = ALIGN(4); __bss_end = .; } > RAM
  __stack_top = ORIGIN(RAM) + LENGTH(RAM);
}
