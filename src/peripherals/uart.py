"""UART/USART peripheral simulation based on STM32F1xx."""

from enum import Enum
from typing import Optional, Callable, List
from collections import deque


class UARTBaudRate(Enum):
    B9600 = 9600
    B19200 = 19200
    B38400 = 38400
    B57600 = 57600
    B115200 = 115200
    B230400 = 230400


class UARTWordLength(Enum):
    BITS_8 = 8
    BITS_9 = 9


class UARTStopBits(Enum):
    STOP_1 = 1
    STOP_0_5 = 0.5
    STOP_2 = 2
    STOP_1_5 = 1.5


class UARTParity(Enum):
    NONE = 'N'
    EVEN = 'E'
    ODD = 'O'


class UART:
    """UART/USART peripheral simulation.

    Simulates TX/RX buffers, baud rate, frame format, and interrupts
    (RXNE, TXE, TC, IDLE).
    """

    def __init__(self, name: str = "USART1", base_addr: int = 0x40013800):
        self.name = name
        self.base_addr = base_addr
        self._baud_rate = UARTBaudRate.B115200
        self._word_length = UARTWordLength.BITS_8
        self._stop_bits = UARTStopBits.STOP_1
        self._parity = UARTParity.NONE
        self._enabled = False
        self._tx_buffer: deque = deque(maxlen=256)
        self._rx_buffer: deque = deque(maxlen=256)
        self._tx_complete = True
        self._last_rx: Optional[int] = None
        self._on_rx: Optional[Callable] = None
        self._on_tx_complete: Optional[Callable] = None
        self._tx_counter = 0
        self._link: Optional['UART'] = None
        self._stats = {'tx_bytes': 0, 'rx_bytes': 0, 'errors': 0}
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def configure(self, baud_rate: UARTBaudRate = None, word_length: UARTWordLength = None,
                  stop_bits: UARTStopBits = None, parity: UARTParity = None):
        if baud_rate:
            self._baud_rate = baud_rate
        if word_length:
            self._word_length = word_length
        if stop_bits:
            self._stop_bits = stop_bits
        if parity:
            self._parity = parity

    def send_byte(self, data: int):
        if not self._enabled:
            return
        self._tx_buffer.append(data & 0xFF)
        self._tx_complete = False
        self._stats['tx_bytes'] += 1

        if self._link and self._link._enabled:
            self._link._push_rx(data & 0xFF)
            self._link._stats['rx_bytes'] += 1

    def send_string(self, text: str):
        for ch in text:
            self.send_byte(ord(ch))

    def send_bytes(self, data: bytes):
        if not self._enabled:
            return
        for b in data:
            self._tx_buffer.append(b & 0xFF)
            self._stats['tx_bytes'] += 1
            if self._link and self._link._enabled:
                self._link._push_rx(b & 0xFF)
                self._link._stats['rx_bytes'] += 1

    def _push_rx(self, data: int):
        self._rx_buffer.append(data & 0xFF)
        if self._on_rx:
            self._on_rx(data & 0xFF)

    def read_byte(self) -> Optional[int]:
        if self._rx_buffer:
            return self._rx_buffer.popleft()
        return None

    def read_all(self) -> bytes:
        data = bytes(self._rx_buffer)
        self._rx_buffer.clear()
        return data

    def available(self) -> int:
        return len(self._rx_buffer)

    def link_to(self, other: 'UART'):
        self._link = other
        other._link = self

    def on_receive(self, callback: Callable):
        self._on_rx = callback

    def flush(self):
        self._tx_buffer.clear()
        self._tx_complete = True

    def reset(self):
        self._tx_buffer.clear()
        self._rx_buffer.clear()
        self._tx_complete = True
        self._last_rx = None
        self._enabled = False
        self._stats = {'tx_bytes': 0, 'rx_bytes': 0, 'errors': 0}

    def _on_tick(self):
        if self._tx_buffer:
            self._tx_counter += 1
            bit_time = self.mcu.system_clock_hz // self._baud_rate.value if self.mcu else 100
            if self._tx_counter >= bit_time:
                self._tx_buffer.popleft()
                self._tx_counter = 0
                if not self._tx_buffer:
                    self._tx_complete = True
                    if self._on_tx_complete:
                        self._on_tx_complete()

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def summary(self) -> str:
        return (
            f"{self.name} (0x{self.base_addr:08X}):\n"
            f"  Baud:   {self._baud_rate.value}\n"
            f"  Format: {self._word_length.value}{self._parity.value}{int(self._stop_bits.value)}\n"
            f"  Enabled: {self._enabled}\n"
            f"  TX buf: {len(self._tx_buffer)} bytes\n"
            f"  RX buf: {len(self._rx_buffer)} bytes\n"
            f"  Stats:  TX={self._stats['tx_bytes']} RX={self._stats['rx_bytes']} ERR={self._stats['errors']}\n"
            f"  Linked: {self._link.name if self._link else 'N/A'}"
        )
