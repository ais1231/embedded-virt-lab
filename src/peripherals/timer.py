"""Timer peripheral simulation for STM32F1xx (general-purpose and SysTick)."""

from enum import Enum
from typing import Optional, Callable


class TimerMode(Enum):
    UP = 0
    DOWN = 1
    CENTER_ALIGNED = 2


class TimerSlaveMode(Enum):
    DISABLED = 0
    ENCODER_MODE_1 = 1
    ENCODER_MODE_2 = 2
    ENCODER_MODE_3 = 3
    RESET = 4
    GATED = 5
    TRIGGER = 6
    EXTERNAL_CLOCK = 7


class Timer:
    """16-bit general-purpose timer simulation.

    Supports up-counting, one-pulse mode, input capture and output compare.
    Prescaler (PSC) and Auto-reload (ARR) registers.
    """

    MAX_COUNT = 0xFFFF

    def __init__(self, name: str = "TIM2", base_addr: int = 0x40000000,
                 bits: int = 16):
        self.name = name
        self.base_addr = base_addr
        self.bits = bits
        self._max_count = (1 << bits) - 1
        self._cnt: int = 0
        self._arr: int = self._max_count
        self._psc: int = 0
        self._mode = TimerMode.UP
        self._enabled = False
        self._one_pulse = False
        self._auto_reload = True
        self._update_event: Optional[Callable] = None
        self._capture_compare: Optional[Callable] = None
        self._ccr: int = 0
        self._prescaler_counter: int = 0
        self._direction = 1
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def set_prescaler(self, psc: int):
        self._psc = psc & self._max_count

    def set_auto_reload(self, arr: int):
        self._arr = arr & self._max_count

    def set_mode(self, mode: TimerMode):
        self._mode = mode

    def get_counter(self) -> int:
        return self._cnt

    def set_counter(self, cnt: int):
        self._cnt = cnt & self._max_count

    def on_update(self, callback: Callable):
        self._update_event = callback

    def get_frequency(self) -> float:
        if not self.mcu:
            return 0
        timer_clock = self._get_timer_clock()
        return timer_clock / ((self._psc + 1) * (self._arr + 1))

    def get_period_us(self) -> float:
        freq = self.get_frequency()
        return (1.0 / freq) * 1e6 if freq > 0 else float('inf')

    def _get_timer_clock(self) -> int:
        if self.name in ('TIM1', 'TIM8'):
            return self.mcu.apb2_clock_hz
        return self.mcu.apb1_clock_hz

    def _on_tick(self):
        if not self._enabled or not self.mcu:
            return

        self._prescaler_counter += 1
        if self._prescaler_counter <= self._psc:
            return
        self._prescaler_counter = 0

        if self._mode == TimerMode.UP:
            self._cnt += 1
            if self._cnt >= self._arr:
                self._cnt = 0 if self._auto_reload else self._arr
                if self._update_event:
                    self._update_event(self)
                if self._one_pulse:
                    self._enabled = False
        elif self._mode == TimerMode.DOWN:
            self._cnt -= 1
            if self._cnt <= 0:
                self._cnt = self._arr if self._auto_reload else 0
                if self._update_event:
                    self._update_event(self)
        elif self._mode == TimerMode.CENTER_ALIGNED:
            self._cnt += self._direction
            if self._cnt >= self._arr:
                self._direction = -1
                if self._update_event:
                    self._update_event(self)
            elif self._cnt <= 0:
                self._direction = 1
                if self._update_event:
                    self._update_event(self)

    def reset(self):
        self._cnt = 0
        self._psc = 0
        self._arr = self._max_count
        self._enabled = False
        self._one_pulse = False
        self._prescaler_counter = 0
        self._direction = 1

    def summary(self) -> str:
        return (
            f"{self.name} (0x{self.base_addr:08X}):\n"
            f"  Bits:   {self.bits}-bit\n"
            f"  CNT:    {self._cnt}\n"
            f"  ARR:    {self._arr}\n"
            f"  PSC:    {self._psc}\n"
            f"  Mode:   {self._mode.name}\n"
            f"  Freq:   {self.get_frequency():.2f} Hz\n"
            f"  Period: {self.get_period_us():.2f} us\n"
            f"  Status: {'Running' if self._enabled else 'Stopped'}"
        )


class SystickTimer:
    """Cortex-M SysTick timer simulation.

    24-bit down-counter generating SysTick exception.
    """

    MAX_COUNT = 0x00FFFFFF

    def __init__(self):
        self._load: int = 0
        self._val: int = 0
        self._enabled = False
        self._tickint = False
        self._clksource = 'CPU'
        self._countflag = False
        self._on_tick: Optional[Callable] = None
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def configure(self, reload_value: int, enable_interrupt: bool = True):
        self._load = reload_value & self.MAX_COUNT
        self._val = self._load
        self._tickint = enable_interrupt

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def get_current_value(self) -> int:
        return self._val

    def on_tick_handler(self, callback: Callable):
        self._on_tick = callback

    def _on_tick(self):
        if not self._enabled or not self.mcu:
            return

        if self._val > 0:
            self._val -= 1
        else:
            self._countflag = True
            if self._tickint and self._on_tick:
                self._on_tick()
            self._val = self._load

    def reset(self):
        self._load = 0
        self._val = 0
        self._enabled = False
        self._tickint = False
        self._countflag = False

    def get_interval_us(self) -> float:
        if not self.mcu:
            return 0
        clock = self.mcu.system_clock_hz if self._clksource == 'CPU' else self.mcu.system_clock_hz // 8
        return ((self._load + 1) / clock) * 1e6

    def summary(self) -> str:
        return (
            f"SysTick:\n"
            f"  LOAD:   0x{self._load:06X}\n"
            f"  VAL:    0x{self._val:06X}\n"
            f"  Status: {'Running' if self._enabled else 'Stopped'}\n"
            f"  Int:    {'ON' if self._tickint else 'OFF'}\n"
            f"  Period: {self.get_interval_us():.2f} us"
        )
