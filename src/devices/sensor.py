"""Simulated sensor devices."""

import random


class TemperatureSensor:
    """Simulated temperature sensor (e.g., LM35, DS18B20)."""

    def __init__(self, name: str = "TEMP", ambient: float = 25.0, noise: float = 0.1):
        self.name = name
        self._ambient = ambient
        self._noise = noise
        self._offset: float = 0.0
        self._samples: list = []

    def read(self) -> float:
        temp = self._ambient + random.gauss(0, self._noise) + self._offset
        self._samples.append(temp)
        if len(self._samples) > 100:
            self._samples.pop(0)
        return temp

    def set_ambient(self, temp: float):
        self._ambient = temp

    def calibrate(self, offset: float):
        self._offset = offset

    def average(self) -> float:
        if not self._samples:
            return self._ambient
        return sum(self._samples) / len(self._samples)

    def range(self) -> tuple:
        if not self._samples:
            return (self._ambient, self._ambient)
        return (min(self._samples), max(self._samples))

    def __repr__(self):
        return f"[{self.name}] {self.read():.2f} C"


class LightSensor:
    """Simulated light intensity sensor (LDR / photodiode)."""

    def __init__(self, name: str = "LIGHT", ambient: float = 500.0):
        self.name = name
        self._ambient = ambient
        self._samples: list = []

    def read(self) -> float:
        value = self._ambient * (1.0 + random.gauss(0, 0.02))
        self._samples.append(value)
        if len(self._samples) > 100:
            self._samples.pop(0)
        return value

    def set_ambient(self, lux: float):
        self._ambient = lux

    def average(self) -> float:
        if not self._samples:
            return self._ambient
        return sum(self._samples) / len(self._samples)

    def __repr__(self):
        return f"[{self.name}] {self.read():.1f} lux"
