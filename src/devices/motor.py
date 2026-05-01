"""Simulated motor devices for embedded experiments."""


class DCMotor:
    """DC motor simulation with PWM speed control and inertia modeling."""

    def __init__(self, name: str = "MOTOR", max_rpm: float = 3000.0):
        self.name = name
        self._max_rpm = max_rpm
        self._speed: float = 0.0
        self._current_rpm: float = 0.0
        self._direction: int = 1
        self._inertia: float = 0.95
        self._enabled: bool = False

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False
        self._speed = 0.0

    def set_speed(self, speed: float):
        self._speed = max(-1.0, min(1.0, speed))
        self._direction = 1 if self._speed >= 0 else -1

    def update(self):
        if not self._enabled:
            self._current_rpm *= self._inertia
            if abs(self._current_rpm) < 1.0:
                self._current_rpm = 0.0
            return
        target_rpm = self._max_rpm * self._speed * self._direction
        self._current_rpm += (target_rpm - self._current_rpm) * (1.0 - self._inertia)

    @property
    def rpm(self) -> float:
        return self._current_rpm

    @property
    def speed_percent(self) -> float:
        return abs(self._current_rpm) / self._max_rpm * 100.0

    def summary(self) -> str:
        return (f"[{self.name}] {self._current_rpm:.0f} RPM "
                f"({'FWD' if self._direction > 0 else 'REV'})")


class StepperMotor:
    """Stepper motor simulation with position tracking."""

    def __init__(self, name: str = "STEPPER", steps_per_rev: int = 200, max_rpm: float = 500.0):
        self.name = name
        self._steps_per_rev = steps_per_rev
        self._max_rpm = max_rpm
        self._position: int = 0
        self._target_position: int = 0
        self._speed: float = 200.0
        self._enabled: bool = False

    def enable(self):
        self._enabled = True

    def disable(self):
        self._enabled = False

    def step(self, steps: int):
        self._position += steps
        self._target_position = self._position

    def move_to(self, position: int):
        self._target_position = position

    def set_speed(self, rpm: float):
        self._speed = max(1.0, min(self._max_rpm, rpm))

    def update(self):
        if not self._enabled or self._position == self._target_position:
            return
        direction = 1 if self._target_position > self._position else -1
        step_increment = max(1, int(self._speed * self._steps_per_rev / 60.0 * 0.001))
        self._position += direction * step_increment
        if (direction > 0 and self._position > self._target_position) or \
           (direction < 0 and self._position < self._target_position):
            self._position = self._target_position

    @property
    def position(self) -> int:
        return self._position

    @property
    def angle(self) -> float:
        return (self._position % self._steps_per_rev) / self._steps_per_rev * 360.0

    def summary(self) -> str:
        return f"[{self.name}] Pos: {self._position} steps, Angle: {self.angle:.1f} deg"
