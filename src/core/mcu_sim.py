"""Core MCU simulator - emulates ARM Cortex-M3 behavior at peripheral level."""

import time
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field
from .clock import ClockTree
from .memory import Memory, Flash, SRAM


@dataclass
class InterruptRequest:
    """NVIC interrupt request representation."""
    irq_number: int
    priority: int = 0
    pending: bool = False
    active: bool = False
    handler: Optional[Callable] = None


class NVIC:
    """Nested Vectored Interrupt Controller simulation."""

    MAX_IRQ = 240

    def __init__(self):
        self._irqs: Dict[int, InterruptRequest] = {}
        self._vector_table: Dict[int, Callable] = {}
        self._basepri = 0
        self._primask = False

    def enable_irq(self, irq_number: int, priority: int = 0):
        if irq_number < 0 or irq_number > self.MAX_IRQ:
            raise ValueError(f"IRQ number {irq_number} out of range (0-{self.MAX_IRQ})")
        self._irqs[irq_number] = InterruptRequest(irq_number=irq_number, priority=priority)

    def set_handler(self, irq_number: int, handler: Callable):
        if irq_number in self._irqs:
            self._irqs[irq_number].handler = handler

    def trigger_irq(self, irq_number: int):
        if irq_number in self._irqs:
            self._irqs[irq_number].pending = True

    def clear_irq(self, irq_number: int):
        if irq_number in self._irqs:
            irq = self._irqs[irq_number]
            irq.pending = False
            irq.active = False

    def get_pending_irqs(self) -> List[InterruptRequest]:
        return [irq for irq in self._irqs.values() if irq.pending and not self._primask]

    def service_pending(self) -> Optional[Callable]:
        pending = self.get_pending_irqs()
        if not pending:
            return None
        highest = min(pending, key=lambda x: x.priority)
        highest.pending = False
        highest.active = True
        return highest.handler

    def disable_global_interrupts(self):
        self._primask = True

    def enable_global_interrupts(self):
        self._primask = False


class MCUSimulator:
    """ARM Cortex-M3/4 class simulator for peripheral-level experimentation."""

    def __init__(self, name: str = "STM32F103C8", flash_size_kb: int = 64, sram_size_kb: int = 20):
        self.name = name
        self.clock = ClockTree()
        self.flash = Flash(flash_size_kb * 1024)
        self.sram = SRAM(sram_size_kb * 1024)
        self.nvic = NVIC()
        self.peripherals: Dict[str, object] = {}
        self._is_running = False
        self._cycle_count: int = 0
        self._breakpoints: set = set()
        self._watchpoints: Dict[int, int] = {}
        self._tick_callbacks: List[Callable] = []

    @property
    def system_clock_hz(self) -> int:
        return self.clock.system_clock

    @property
    def ahb_clock_hz(self) -> int:
        return self.clock.ahb_clock

    @property
    def apb1_clock_hz(self) -> int:
        return self.clock.apb1_clock

    @property
    def apb2_clock_hz(self) -> int:
        return self.clock.apb2_clock

    def attach_peripheral(self, name: str, peripheral: object):
        self.peripherals[name] = peripheral
        if hasattr(peripheral, 'attach_mcu'):
            peripheral.attach_mcu(self)

    def get_peripheral(self, name: str) -> object:
        if name not in self.peripherals:
            raise KeyError(f"Peripheral '{name}' not found")
        return self.peripherals[name]

    def add_tick_callback(self, callback: Callable):
        self._tick_callbacks.append(callback)

    def tick(self):
        self._cycle_count += 1

        for cb in self._tick_callbacks:
            cb()

        handler = self.nvic.service_pending()
        if handler:
            handler()

        for p in self.peripherals.values():
            if hasattr(p, '_on_tick'):
                p._on_tick()

    def run(self, cycles: Optional[int] = None):
        self._is_running = True
        try:
            if cycles is not None:
                for _ in range(cycles):
                    if not self._is_running:
                        break
                    self.tick()
            else:
                while self._is_running:
                    self.tick()
        except KeyboardInterrupt:
            pass
        finally:
            self._is_running = False

    def stop(self):
        self._is_running = False

    def reset(self):
        self._cycle_count = 0
        self._is_running = False
        for p in self.peripherals.values():
            if hasattr(p, 'reset'):
                p.reset()
        self.nvic = NVIC()

    @property
    def cycle_count(self) -> int:
        return self._cycle_count

    def delay_ms(self, ms: int):
        ticks_per_ms = self.system_clock_hz // 1000
        self.run(ticks_per_ms * ms)

    def delay_us(self, us: int):
        ticks_per_us = self.system_clock_hz // 1_000_000
        self.run(ticks_per_us * us)
