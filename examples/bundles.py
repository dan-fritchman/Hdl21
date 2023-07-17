"""
# Bundles Example 

Uses a typical embedded system as an example to demonstrate the use of hdl21 `Bundle`s.
"""

import hdl21 as h
from sys import stdout
from enum import Enum, auto


@h.roleset
class HostDevice(Enum):
    # A pair of roles `Host` and `Device`, as commonly used by USB, JTAG, and similar buses.
    HOST = auto()
    DEVICE = auto()


@h.bundle
class Jtag:
    # Jtag Bundle
    roles = HostDevice
    tck, tdi, tms = h.Signals(3, src=roles.HOST, dest=roles.DEVICE)
    tdo = h.Signal(src=roles.DEVICE, dest=roles.HOST)


@h.bundle
class Uart:
    # Uart Bundle
    # Note the UART bundle is not role-based;
    # If it is used as a port, `tx` is always an output, and `rx` is always an input.
    tx = h.Output()
    rx = h.Input()


@h.bundle
class Spi:
    # Spi Bundle
    roles = HostDevice
    sck, cs = h.Signals(2, src=roles.HOST, dest=roles.DEVICE)
    dq = h.Signal(src=roles.DEVICE, dest=roles.HOST, width=4)


@h.module
class Chip:
    # Chip, with SPI, JTAG, and UART ports
    spi = Spi(role=HostDevice.HOST, port=True)
    jtag = Jtag(role=HostDevice.DEVICE, port=True)
    uart = Uart(port=True)
    ...  # Actual internal content, which likely connects these down *many* levels of hierarchy


@h.module
class SpiFlash:
    # A typical flash memory with a SPI port
    spi = Spi(role=HostDevice.DEVICE, port=True)


@h.module
class Board:
    # A typical embedded board, featuring a custom chip, SPI-connected flash, and JTAG port
    jtag = Jtag(role=HostDevice.DEVICE, port=True)
    uart = Uart(port=True)

    chip = Chip(jtag=jtag, uart=uart)
    flash = SpiFlash(spi=chip.spi)


@h.module
class Tester:
    # A typical test-widget with a JTAG port
    jtag = Jtag(role=HostDevice.HOST, port=True)
    uart = Uart(port=True)


@h.module
class TestSystem:
    # A system in which `Tester` can test `Board`
    jtag = Jtag()
    board_uart = Uart()

    # Connect a `Board` and `Tester`, swapping UART `rx` and `tx` between them
    board = Board(jtag=jtag, uart=board_uart)
    tester = Tester(jtag=jtag, uart=h.bundlize(tx=board_uart.rx, rx=board_uart.tx))


def main():
    # Main entrypoint. Print a Verilog netlist, which includes all the resolved port-directions, to stdout.
    h.netlist(TestSystem, stdout, fmt="verilog")


if __name__ == "__main__":
    main()
