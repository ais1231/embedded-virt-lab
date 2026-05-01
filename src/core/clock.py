"""Clock tree simulation for STM32F1xx series MCU."""

from enum import Enum


class ClockSource(Enum):
    HSI = 8_000_000      # Internal 8MHz RC
    HSE = 8_000_000      # External 8MHz (default)
    PLL = 72_000_000     # PLL output


class AHBPrescaler(Enum):
    DIV1 = 1
    DIV2 = 2
    DIV4 = 4
    DIV8 = 8
    DIV16 = 16
    DIV64 = 64
    DIV128 = 128
    DIV256 = 256
    DIV512 = 512


class APBPrescaler(Enum):
    DIV1 = 1
    DIV2 = 2
    DIV4 = 4
    DIV8 = 8
    DIV16 = 16


class ClockTree:
    """STM32F103 clock tree simulation.

    Default configuration: HSE 8MHz -> PLL x9 = 72MHz SYSCLK
    AHB = 72MHz, APB1 = 36MHz, APB2 = 72MHz
    """

    def __init__(self):
        self._hse_freq = 8_000_000
        self._hsi_freq = 8_000_000
        self._pll_mul = 9
        self._pll_src = ClockSource.HSE
        self._sysclk_src = ClockSource.PLL
        self._ahb_prescaler = AHBPrescaler.DIV1
        self._apb1_prescaler = APBPrescaler.DIV2
        self._apb2_prescaler = APBPrescaler.DIV1
        self._pll_enabled = True

    def configure_hse(self, freq_hz: int):
        self._hse_freq = freq_hz

    def configure_pll(self, mul: int, source: ClockSource = ClockSource.HSE):
        self._pll_mul = mul
        self._pll_src = source

    def set_sysclk_source(self, source: ClockSource):
        self._sysclk_src = source

    def set_ahb_prescaler(self, prescaler: AHBPrescaler):
        self._ahb_prescaler = prescaler

    def set_apb1_prescaler(self, prescaler: APBPrescaler):
        self._apb1_prescaler = prescaler

    def set_apb2_prescaler(self, prescaler: APBPrescaler):
        self._apb2_prescaler = prescaler

    def enable_pll(self, enabled: bool = True):
        self._pll_enabled = enabled

    @property
    def pll_clock(self) -> int:
        if not self._pll_enabled:
            return 0
        src_freq = self._hse_freq if self._pll_src == ClockSource.HSE else self._hsi_freq
        return src_freq * self._pll_mul

    @property
    def system_clock(self) -> int:
        if self._sysclk_src == ClockSource.HSI:
            return self._hsi_freq
        elif self._sysclk_src == ClockSource.HSE:
            return self._hse_freq
        elif self._sysclk_src == ClockSource.PLL:
            return self.pll_clock
        return 0

    @property
    def ahb_clock(self) -> int:
        return self.system_clock // self._ahb_prescaler.value

    @property
    def apb1_clock(self) -> int:
        return self.ahb_clock // self._apb1_prescaler.value

    @property
    def apb2_clock(self) -> int:
        return self.ahb_clock // self._apb2_prescaler.value

    def summary(self) -> str:
        return (
            f"Clock Configuration:\n"
            f"  HSE:       {self._hse_freq / 1e6:.1f} MHz\n"
            f"  HSI:       {self._hsi_freq / 1e6:.1f} MHz\n"
            f"  PLL:       {self.pll_clock / 1e6:.1f} MHz (src={self._pll_src.name}, mul={self._pll_mul})\n"
            f"  SYSCLK:    {self.system_clock / 1e6:.1f} MHz\n"
            f"  HCLK(AHB): {self.ahb_clock / 1e6:.1f} MHz (/{self._ahb_prescaler.value})\n"
            f"  PCLK1:     {self.apb1_clock / 1e6:.1f} MHz (/{self._apb1_prescaler.value})\n"
            f"  PCLK2:     {self.apb2_clock / 1e6:.1f} MHz (/{self._apb2_prescaler.value})"
        )
