"""Memory subsystem simulation for embedded MCUs."""

from typing import Dict, List, Optional, Tuple


class Memory:
    """Base memory region with read/write access control."""

    def __init__(self, size: int, base_addr: int = 0, name: str = "MEM"):
        self.size = size
        self.base_addr = base_addr
        self.name = name
        self._data = bytearray(size)

    def read_u8(self, addr: int) -> int:
        offset = addr - self.base_addr
        self._check_bounds(offset, 1)
        return self._data[offset]

    def read_u16(self, addr: int) -> int:
        offset = addr - self.base_addr
        self._check_bounds(offset, 2)
        return int.from_bytes(self._data[offset:offset + 2], 'little')

    def read_u32(self, addr: int) -> int:
        offset = addr - self.base_addr
        self._check_bounds(offset, 4)
        return int.from_bytes(self._data[offset:offset + 4], 'little')

    def write_u8(self, addr: int, value: int):
        offset = addr - self.base_addr
        self._check_bounds(offset, 1)
        self._data[offset] = value & 0xFF

    def write_u16(self, addr: int, value: int):
        offset = addr - self.base_addr
        self._check_bounds(offset, 2)
        self._data[offset:offset + 2] = (value & 0xFFFF).to_bytes(2, 'little')

    def write_u32(self, addr: int, value: int):
        offset = addr - self.base_addr
        self._check_bounds(offset, 4)
        self._data[offset:offset + 4] = (value & 0xFFFFFFFF).to_bytes(4, 'little')

    def _check_bounds(self, offset: int, size: int):
        if offset < 0 or offset + size > self.size:
            raise MemoryError(
                f"{self.name}: access at offset 0x{offset:08X} size {size} "
                f"exceeds region size 0x{self.size:08X}"
            )

    def hexdump(self, start: int = 0, length: int = 256) -> str:
        start = max(0, start)
        end = min(start + length, self.size)
        lines = []
        for i in range(start, end, 16):
            chunk = self._data[i:i + 16]
            hex_part = ' '.join(f'{b:02X}' for b in chunk)
            ascii_part = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append(f'  {self.base_addr + i:08X}: {hex_part:<48s} {ascii_part}')
        return '\n'.join(lines)

    def __len__(self) -> int:
        return self.size


class Flash(Memory):
    """Flash memory with write-protection semantics."""

    def __init__(self, size: int, base_addr: int = 0x08000000):
        super().__init__(size, base_addr, "FLASH")
        self._unlocked = False

    def unlock(self):
        self._unlocked = True

    def lock(self):
        self._unlocked = False

    def erase_page(self, page_addr: int, page_size: int = 1024):
        if not self._unlocked:
            raise PermissionError("FLASH: must unlock before erase")
        offset = page_addr - self.base_addr
        self._data[offset:offset + page_size] = b'\xFF' * page_size

    def write_u8(self, addr: int, value: int):
        if not self._unlocked:
            raise PermissionError("FLASH: must unlock before write")
        super().write_u8(addr, value)

    def write_u16(self, addr: int, value: int):
        if not self._unlocked:
            raise PermissionError("FLASH: must unlock before write")
        super().write_u16(addr, value)

    def write_u32(self, addr: int, value: int):
        if not self._unlocked:
            raise PermissionError("FLASH: must unlock before write")
        super().write_u32(addr, value)


class SRAM(Memory):
    """SRAM region with fast read/write."""

    def __init__(self, size: int, base_addr: int = 0x20000000):
        super().__init__(size, base_addr, "SRAM")
