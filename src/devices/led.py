"""Simulated LED device."""


class LED:
    """Simulated LED with brightness control and blink counting."""

    def __init__(self, name: str = "LED", color: str = "red"):
        self.name = name
        self.color = color
        self._state: bool = False
        self._brightness: float = 1.0
        self._blink_count: int = 0

    def on(self):
        self._state = True

    def off(self):
        self._state = False

    def toggle(self):
        self._state = not self._state
        if self._state:
            self._blink_count += 1

    def set_brightness(self, level: float):
        self._brightness = max(0.0, min(1.0, level))

    @property
    def is_on(self) -> bool:
        return self._state

    @property
    def brightness(self) -> float:
        return self._brightness if self._state else 0.0

    def __repr__(self):
        status = 'ON ' if self._state else 'OFF'
        return f"[{self.name}] {status} ({self.brightness:.0%})"
