"""Terminal-based visualization for embedded simulation state."""

import os
import sys
import time
from typing import Dict, Optional


class TerminalView:
    """Displays MCU peripheral states in terminal with color output."""

    COLORS = {
        'reset': '\033[0m',
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'bold': '\033[1m',
        'dim': '\033[2m',
    }

    def __init__(self, use_color: bool = True, refresh_rate: float = 10.0):
        self._use_color = use_color
        self._refresh_rate = refresh_rate
        self._lines: list = []
        self._callbacks: Dict[str, callable] = {}
        self._running = False
        self._frame_count = 0

    def add_section(self, name: str, callback: callable):
        """Register a section that returns a string when called."""
        self._callbacks[name] = callback

    def start(self, duration_seconds: Optional[float] = None):
        self._running = True
        start_time = time.time()
        try:
            while self._running:
                self._render()
                self._frame_count += 1
                if duration_seconds and (time.time() - start_time) > duration_seconds:
                    break
                time.sleep(1.0 / self._refresh_rate)
        except KeyboardInterrupt:
            pass
        finally:
            self._running = False

    def stop(self):
        self._running = False

    def _render(self):
        os.system('cls' if sys.platform == 'win32' else 'clear')
        width = os.get_terminal_size().columns
        border = '=' * min(width, 80)

        header = self._c('bold') + self._c('cyan') + \
            " Embedded Virtual Lab - Simulation Monitor " + self._c('reset')
        print(header.center(width))
        print(self._c('dim') + f" Frame: {self._frame_count}".center(width) + self._c('reset'))
        print(border)

        for name, callback in self._callbacks.items():
            section_title = f" {name} "
            print(self._c('yellow') + section_title + self._c('reset'))
            try:
                output = callback()
                for line in output.strip().split('\n'):
                    print(f"  {line}")
            except Exception as e:
                print(f"  {self._c('red')}Error: {e}{self._c('reset')}")
            print()

        print(border)
        print(self._c('dim') + " Q=Quit | R=Reset | P=Pause ".center(width) + self._c('reset'))

    def _c(self, color: str) -> str:
        return self.COLORS.get(color, '') if self._use_color else ''


class PinStateDisplay:
    """ASCII bar visualization for analog values (0-4095 ADC, 0-100% PWM, etc.)."""

    WIDTH = 40

    @staticmethod
    def bar(value: float, max_value: float, label: str = "", filled: str = "#",
            empty: str = ".", show_value: bool = True) -> str:
        ratio = max(0.0, min(1.0, value / max_value))
        filled_count = int(ratio * PinStateDisplay.WIDTH)
        bar_str = filled * filled_count + empty * (PinStateDisplay.WIDTH - filled_count)
        if show_value:
            return f"{label:12s} [{bar_str}] {value:.1f}"
        return f"{label:12s} [{bar_str}]"

    @staticmethod
    def multi_bar(values: list, labels: list, max_value: float, title: str = "") -> str:
        lines = []
        if title:
            lines.append(f"  {title}")
        for val, lbl in zip(values, labels):
            lines.append("  " + PinStateDisplay.bar(val, max_value, lbl))
        return '\n'.join(lines)
