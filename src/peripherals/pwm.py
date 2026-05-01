"""PWM output simulation based on STM32 timer channels."""

from enum import Enum
from typing import Optional, Callable
import math


class PWMMode(Enum):
    """PWM output compare modes."""
    PWM1 = 0   # Active when CNT < CCR, else inactive
    PWM2 = 1   # Active when CNT > CCR, else inactive


class PWMPolarity(Enum):
    ACTIVE_HIGH = 0
    ACTIVE_LOW = 1


class PWMChannel:
    """Single PWM output channel."""

    def __init__(self, channel: int):
        self.channel = channel
        self._duty_cycle: float = 0.0   # 0.0 to 100.0
        self._frequency: float = 1000.0  # Hz
        self._mode = PWMMode.PWM1
        self._polarity = PWMPolarity.ACTIVE_HIGH
        self._enabled = False
        self._output: int = 0
        self._on_change: Optional[Callable] = None

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False
        self._output = 0

    def set_duty_cycle(self, percent: float):
        self._duty_cycle = max(0.0, min(100.0, percent))

    def set_frequency(self, freq_hz: float):
        self._frequency = max(1.0, freq_hz)

    def get_output(self) -> int:
        return self._output

    def on_change(self, callback: Callable):
        self._on_change = callback

    @property
    def duty_cycle(self) -> float:
        return self._duty_cycle

    @property
    def frequency(self) -> float:
        return self._frequency

    def summary(self) -> str:
        return (
            f"  CH{self.channel}: {'ON' if self._enabled else 'OFF'} "
            f"{self._duty_cycle:.1f}% @ {self._frequency:.1f}Hz → Out={self._output}"
        )


class PWM:
    """PWM generator using timer-based output compare.

    Supports up to 4 channels per timer, configurable frequency and duty cycle.
    """

    def __init__(self, name: str = "PWM1", base_addr: int = 0x40012C00):
        self.name = name
        self.base_addr = base_addr
        self._channels = {i: PWMChannel(i) for i in range(1, 5)}
        self._timer_period: int = 999
        self._timer_prescaler: int = 71
        self._timer_clock: int = 72_000_000
        self._enabled = False
        self._counter: int = 0
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu
        if mcu:
            self._timer_clock = mcu.apb1_clock_hz if name != 'PWM1' else mcu.apb2_clock_hz

    def __getitem__(self, channel: int) -> PWMChannel:
        if channel not in self._channels:
            raise IndexError(f"PWM channel {channel} not found (1-4)")
        return self._channels[channel]

    def enable(self):
        self._enabled = True
        for ch in self._channels.values():
            if ch._enabled:
                ch._output = 1

    def disable(self):
        self._enabled = False
        for ch in self._channels.values():
            ch._output = 0

    def set_period(self, period: int):
        self._timer_period = period

    def set_prescaler(self, prescaler: int):
        self._timer_prescaler = prescaler

    def get_base_frequency(self) -> float:
        return self._timer_clock / ((self._timer_prescaler + 1) * (self._timer_period + 1))

    def configure_channel(self, channel: int, duty_percent: float, frequency: Optional[float] = None):
        ch = self._channels[channel]
        ch.set_duty_cycle(duty_percent)
        if frequency is not None:
            ch.set_frequency(frequency)
        ch.enable()

    def _on_tick(self):
        if not self._enabled:
            return

        self._counter = (self._counter + 1) % (self._timer_period + 1)

        for ch in self._channels.values():
            if not ch._enabled:
                continue
            threshold = int(self._timer_period * ch._duty_cycle / 100.0)
            new_output = 1 if self._counter < threshold else 0
            if ch._polarity == PWMPolarity.ACTIVE_LOW:
                new_output = 1 - new_output
            if new_output != ch._output:
                ch._output = new_output
                if ch._on_change:
                    ch._on_change(new_output)

    def reset(self):
        self._counter = 0
        self._enabled = False
        for ch in self._channels.values():
            ch.disable()

    def summary(self) -> str:
        base_freq = self.get_base_frequency()
        lines = [
            f"{self.name} (0x{self.base_addr:08X}):",
            f"  Timer: PSC={self._timer_prescaler} ARR={self._timer_period}",
            f"  Base Freq: {base_freq:.1f} Hz",
            f"  Counter: {self._counter}",
        ]
        for ch in self._channels.values():
            lines.append(ch.summary())
        return '\n'.join(lines)
