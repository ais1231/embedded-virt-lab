"""ADC peripheral simulation for STM32F1xx (12-bit SAR ADC)."""

from enum import Enum
from typing import Optional, Callable, List
import random


class ADCChannel(Enum):
    CH0 = 0
    CH1 = 1
    CH2 = 2
    CH3 = 3
    CH4 = 4
    CH5 = 5
    CH6 = 6
    CH7 = 7
    CH8 = 8
    CH9 = 9
    CH10 = 10
    CH11 = 11
    CH12 = 12
    CH13 = 13
    CH14 = 14
    CH15 = 15
    CH16 = 16
    CH17 = 17
    TEMP = 16
    VREFINT = 17


class ADCAlign(Enum):
    RIGHT = 0
    LEFT = 1


class ADC:
    """12-bit SAR ADC simulation with injected and regular channels.

    Supports scan mode, continuous conversion, and external trigger.
    Resolution: 12-bit (0-4095), Reference: 3.3V
    """

    VREF = 3.3
    RESOLUTION = 12
    MAX_VALUE = (1 << RESOLUTION) - 1  # 4095

    def __init__(self, name: str = "ADC1", base_addr: int = 0x40012400):
        self.name = name
        self.base_addr = base_addr
        self._channels: List[ADCChannel] = [ADCChannel.CH0]
        self._current_channel = ADCChannel.CH0
        self._data_register: int = 0
        self._align = ADCAlign.RIGHT
        self._continuous = False
        self._scan_mode = False
        self._enabled = False
        self._eoc_callback: Optional[Callable] = None
        self._channel_values: dict = {}
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def set_channel(self, channel: ADCChannel):
        self._current_channel = channel
        if channel not in self._channels:
            self._channels = [channel]

    def set_channels(self, channels: List[ADCChannel]):
        self._channels = channels

    def set_scan_mode(self, enabled: bool):
        self._scan_mode = enabled

    def set_continuous(self, enabled: bool):
        self._continuous = enabled

    def inject_value(self, channel: ADCChannel, voltage: float):
        if 0 <= voltage <= self.VREF:
            self._channel_values[channel] = voltage

    def start_conversion(self):
        if not self._enabled:
            return

        for ch in self._channels:
            voltage = self._channel_values.get(ch, 0.0)
            # Add Gaussian noise to simulate real ADC behavior
            noise = random.gauss(0, 0.002)  # ~2mV RMS noise
            voltage = max(0.0, min(self.VREF, voltage + noise))
            self._data_register = self._voltage_to_code(voltage, self._align)
            self._current_channel = ch
            if self._eoc_callback:
                self._eoc_callback(ch, self._data_register)

    def read(self) -> int:
        return self._data_register

    def read_voltage(self) -> float:
        return self._code_to_voltage(self._data_register, self._align)

    def on_eoc(self, callback: Callable):
        self._eoc_callback = callback

    def _voltage_to_code(self, voltage: float, align: ADCAlign) -> int:
        code = int((voltage / self.VREF) * self.MAX_VALUE)
        code = max(0, min(self.MAX_VALUE, code))
        if align == ADCAlign.LEFT:
            code <<= (16 - self.RESOLUTION)
        return code

    def _code_to_voltage(self, code: int, align: ADCAlign) -> float:
        if align == ADCAlign.LEFT:
            code >>= (16 - self.RESOLUTION)
        return (code / self.MAX_VALUE) * self.VREF

    def reset(self):
        self._data_register = 0
        self._channels = [ADCChannel.CH0]
        self._current_channel = ADCChannel.CH0
        self._enabled = False
        self._continuous = False
        self._scan_mode = False
        self._channel_values.clear()

    def summary(self) -> str:
        return (
            f"{self.name} (0x{self.base_addr:08X}):\n"
            f"  Enabled: {self._enabled}\n"
            f"  Channel: {self._current_channel.name}\n"
            f"  Data:    0x{self._data_register:04X} ({self.read_voltage():.3f}V)\n"
            f"  Scan:    {self._scan_mode}\n"
            f"  Cont:    {self._continuous}\n"
            f"  VREF:    {self.VREF}V"
        )
