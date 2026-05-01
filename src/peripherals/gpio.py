"""GPIO port and pin simulation for STM32F1xx."""

from enum import Enum
from typing import Optional, Callable, Dict


class GPIOMode(Enum):
    INPUT = 0
    OUTPUT_10MHZ = 1
    OUTPUT_2MHZ = 2
    OUTPUT_50MHZ = 3


class GPIOConfig(Enum):
    """CRL/CRH configuration modes for STM32."""
    ANALOG = 0
    FLOATING_INPUT = 1
    PULL_UP_DOWN = 2
    RESERVED = 3
    PUSH_PULL = 0
    OPEN_DRAIN = 4
    AF_PUSH_PULL = 8
    AF_OPEN_DRAIN = 12


class PinState(Enum):
    LOW = 0
    HIGH = 1


class GPIOPin:
    """Single GPIO pin with configurable modes."""

    def __init__(self, port: str, pin: int):
        self.port = port
        self.pin = pin
        self.name = f"P{port}{pin}"
        self._state = PinState.LOW
        self._mode = GPIOMode.INPUT
        self._config = GPIOConfig.FLOATING_INPUT
        self._output_value = 0
        self._input_value = 0
        self._on_change: Optional[Callable] = None

    @property
    def state(self) -> PinState:
        return PinState.HIGH if self.read() else PinState.LOW

    def set_mode(self, mode: GPIOMode, config: GPIOConfig):
        self._mode = mode
        self._config = config

    def read(self) -> int:
        return self._input_value

    def write(self, value: int):
        if self._mode in (GPIOMode.OUTPUT_10MHZ, GPIOMode.OUTPUT_2MHZ, GPIOMode.OUTPUT_50MHZ):
            self._output_value = 1 if value else 0
            self._input_value = self._output_value
            if self._on_change:
                self._on_change(self._output_value)

    def toggle(self):
        if self._mode in (GPIOMode.OUTPUT_10MHZ, GPIOMode.OUTPUT_2MHZ, GPIOMode.OUTPUT_50MHZ):
            self.write(1 - self._output_value)

    def set_input_value(self, value: int):
        if self._mode == GPIOMode.INPUT:
            self._input_value = 1 if value else 0

    def on_change(self, callback: Callable):
        self._on_change = callback

    def __repr__(self):
        return f"Pin({self.name}, mode={self._mode.name}, state={self.state.name})"


class GPIO:
    """16-pin GPIO port with STM32 GPIO register semantics.

    Simulates: CRL, CRH, IDR, ODR, BSRR, BRR registers.
    """

    def __init__(self, port: str = 'A', base_addr: int = 0x40010800):
        self.port = port
        self.base_addr = base_addr
        self.pins: Dict[int, GPIOPin] = {i: GPIOPin(port, i) for i in range(16)}
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def __getitem__(self, pin: int) -> GPIOPin:
        if pin < 0 or pin > 15:
            raise IndexError(f"Pin {pin} out of range (0-15)")
        return self.pins[pin]

    def configure_pin(self, pin: int, mode: GPIOMode, config: GPIOConfig):
        self.pins[pin].set_mode(mode, config)

    def read_port(self) -> int:
        value = 0
        for i in range(16):
            value |= (self.pins[i].read() << i)
        return value

    def write_port(self, value: int):
        for i in range(16):
            if self.pins[i]._mode != GPIOMode.INPUT:
                self.pins[i].write((value >> i) & 1)

    def set_bits(self, bits: int):
        for i in range(16):
            if bits & (1 << i):
                self.pins[i].write(1)

    def reset_bits(self, bits: int):
        for i in range(16):
            if bits & (1 << i):
                self.pins[i].write(0)

    def reset(self):
        for pin in self.pins.values():
            pin.write(0)
            pin.set_mode(GPIOMode.INPUT, GPIOConfig.FLOATING_INPUT)

    def summary(self) -> str:
        lines = [f"GPIO{self.port} (0x{self.base_addr:08X}):"]
        for i in range(16):
            pin = self.pins[i]
            val = 'H' if pin.read() else 'L'
            mode = 'IN' if pin._mode == GPIOMode.INPUT else 'OUT'
            lines.append(f"  Pin{i:2d}: [{val}] {mode}")
        return '\n'.join(lines)
