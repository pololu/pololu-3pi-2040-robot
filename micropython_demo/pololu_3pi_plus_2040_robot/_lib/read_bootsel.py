@micropython.asm_thumb
def read_bootsel():
    # disable interrupts
    cpsid(0x0)
    
    # set r2 = addr of GPIO_QSI_SS registers, at 0x40018000
    # GPIO_QSPI_SS_CTRL is at +0x0c
    # GPIO_QSPI_SS_STATUS is at +0x08
    align(4)
    data(2, 0x4a00) # ldr r2, [pc, #0]
    b(skip_data)
    data(4, 0x40018000)
    label(skip_data)
    
    # set bit 13 (OEOVER[1]) to disable output
    mov(r1, 1)
    lsl(r1, r1, 13)
    str(r1, [r2, 0x0c])
    
    # delay about 3us
    # seems to work on the Pico - tune for your system
    mov(r0, 0x16)
    label(DELAY)
    sub(r0, 1)
    bpl(DELAY)
    
    # check GPIO_QSPI_SS_STATUS bit 17 - input value
    ldr(r0, [r2, 0x08])
    lsr(r0, r0, 17)
    mov(r1, 1)
    and_(r0, r1)
    
    # clear bit 13 to re-enable, or it crashes
    mov(r1, 0)
    str(r1, [r2, 0x0c])
    
    # re-enable interrupts
    cpsie(0x0)
