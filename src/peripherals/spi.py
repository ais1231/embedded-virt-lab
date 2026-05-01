"""SPI peripheral simulation based on STM32F1xx."""

from enum import Enum
from typing import Optional, Callable, List
from collections import deque


class SPIMode(Enum):
    MODE_0 = 0  # CPOL=0, CPHA=0
    MODE_1 = 1  # CPOL=0, CPHA=1
    MODE_2 = 2  # CPOL=1, CPHA=0
    MODE_3 = 3  # CPOL=1, CPHA=1


class SPIRole(Enum):
    MASTER = 0
    SLAVE = 1


class SPIDataSize(Enum):
    BITS_8 = 8
    BITS_16 = 16


class SPI:
    """SPI bus simulation - full-duplex, configurable mode and data size."""

    def __init__(self, name: str = "SPI1", base_addr: int = 0x40013000):
        self.name = name
        self.base_addr = base_addr
        self._role = SPIRole.MASTER
        self._mode = SPIMode.MODE_0
        self._data_size = SPIDataSize.BITS_8
        self._baud_rate_prescaler = 2
        self._enabled = False
        self._tx_buffer: deque = deque()
        self._rx_buffer: deque = deque()
        self._stats = {'tx_bytes': 0, 'rx_bytes': 0, 'errors': 0}
        self._on_rx: Optional[Callable] = None
        self._slave: Optional['SPI'] = None
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def configure(self, mode: SPIMode = None, role: SPIRole = None,
                  data_size: SPIDataSize = None, prescaler: int = None):
        if mode is not None:
            self._mode = mode
        if role is not None:
            self._role = role
        if data_size is not None:
            self._data_size = data_size
        if prescaler is not None:
            self._baud_rate_prescaler = prescaler

    def get_baud_rate(self) -> int:
        if not self.mcu:
            return 0
        return self.mcu.apb2_clock_hz // self._baud_rate_prescaler

    def connect_slave(self, slave: 'SPI'):
        self._slave = slave
        slave._role = SPIRole.SLAVE

    def transfer(self, data: int) -> int:
        if not self._enabled:
            return 0
        self._stats['tx_bytes'] += 1
        if self._slave and self._slave._enabled:
            received = self._slave._handle_transfer(data)
            self._rx_buffer.append(received)
            self._stats['rx_bytes'] += 1
            if self._on_rx:
                self._on_rx(received)
            return received
        return 0

    def transfer_bytes(self, data: bytes) -> bytes:
        return bytes(self.transfer(b) for b in data)

    def _handle_transfer(self, data: int) -> int:
        self._stats['rx_bytes'] += 1
        if self._on_rx:
            self._on_rx(data)
        return 0xFF  # default slave response

    def write_byte(self, data: int):
        self.transfer(data)

    def read_byte(self) -> Optional[int]:
        return self._rx_buffer.popleft() if self._rx_buffer else None

    def available(self) -> int:
        return len(self._rx_buffer)

    def on_receive(self, callback: Callable):
        self._on_rx = callback

    def reset(self):
        self._tx_buffer.clear()
        self._rx_buffer.clear()
        self._enabled = False
        self._stats = {'tx_bytes': 0, 'rx_bytes': 0, 'errors': 0}

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def summary(self) -> str:
        return (
            f"{self.name} (0x{self.base_addr:08X}):\n"
            f"  Mode:   {self._mode.name}\n"
            f"  Role:   {self._role.name}\n"
            f"  Data:   {self._data_size.value}-bit\n"
            f"  Baud:   {self.get_baud_rate()/1000:.0f} kHz\n"
            f"  Stats:  TX={self._stats['tx_bytes']} RX={self._stats['rx_bytes']}\n"
            f"  Status: {'Enabled' if self._enabled else 'Disabled'}"
        )
