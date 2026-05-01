"""I2C peripheral simulation based on STM32F1xx."""

from enum import Enum
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass, field


class I2CMode(Enum):
    MASTER = 0
    SLAVE = 1


class I2CSpeed(Enum):
    STANDARD = 100_000
    FAST = 400_000


@dataclass
class I2CDevice:
    address: int
    name: str
    registers: Dict[int, int] = field(default_factory=dict)
    on_read: Optional[Callable] = None
    on_write: Optional[Callable] = None


class I2C:
    """I2C bus simulation - Standard (100kHz) and Fast (400kHz) modes."""

    def __init__(self, name: str = "I2C1", base_addr: int = 0x40005400):
        self.name = name
        self.base_addr = base_addr
        self._mode = I2CMode.MASTER
        self._speed = I2CSpeed.STANDARD
        self._enabled = False
        self._devices: Dict[int, I2CDevice] = {}
        self._stats = {'reads': 0, 'writes': 0, 'nacks': 0}
        self._on_transfer: Optional[Callable] = None
        self.mcu = None

    def attach_mcu(self, mcu):
        self.mcu = mcu

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def set_speed(self, speed: I2CSpeed):
        self._speed = speed

    def register_device(self, address: int, name: str, registers: Dict[int, int] = None):
        if address in self._devices:
            raise ValueError(f"I2C address 0x{address:02X} already in use")
        self._devices[address] = I2CDevice(
            address=address, name=name, registers=registers or {})

    def scan(self) -> List[int]:
        return sorted(self._devices.keys())

    def write_register(self, dev_addr: int, reg_addr: int, data: int):
        if dev_addr not in self._devices:
            self._stats['nacks'] += 1
            raise IOError(f"I2C: NACK from device 0x{dev_addr:02X}")
        dev = self._devices[dev_addr]
        dev.registers[reg_addr] = data & 0xFF
        self._stats['writes'] += 1
        if dev.on_write:
            dev.on_write(reg_addr, data & 0xFF)
        if self._on_transfer:
            self._on_transfer('write', dev_addr, reg_addr, data & 0xFF)

    def read_register(self, dev_addr: int, reg_addr: int) -> int:
        if dev_addr not in self._devices:
            self._stats['nacks'] += 1
            raise IOError(f"I2C: NACK from device 0x{dev_addr:02X}")
        dev = self._devices[dev_addr]
        self._stats['reads'] += 1
        value = dev.registers.get(reg_addr, 0)
        if dev.on_read:
            value = dev.on_read(reg_addr)
            dev.registers[reg_addr] = value
        return value

    def write_bytes(self, dev_addr: int, reg_addr: int, data: bytes):
        for i, b in enumerate(data):
            self.write_register(dev_addr, reg_addr + i, b)

    def read_bytes(self, dev_addr: int, reg_addr: int, length: int) -> bytes:
        return bytes(self.read_register(dev_addr, reg_addr + i) for i in range(length))

    def on_transfer(self, callback: Callable):
        self._on_transfer = callback

    def reset(self):
        self._devices.clear()
        self._stats = {'reads': 0, 'writes': 0, 'nacks': 0}
        self._enabled = False

    @property
    def stats(self) -> dict:
        return dict(self._stats)

    def summary(self) -> str:
        dev_list = [f"0x{a:02X}: {d.name}" for a, d in self._devices.items()]
        return (
            f"{self.name} (0x{self.base_addr:08X}):\n"
            f"  Speed: {self._speed.value/1000:.0f} kHz\n"
            f"  Mode:  {self._mode.name}\n"
            f"  Stats: R={self._stats['reads']} W={self._stats['writes']} NACK={self._stats['nacks']}\n"
            f"  Devices: [{', '.join(dev_list) if dev_list else 'none'}]"
        )
