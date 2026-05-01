"""Experiment 5: PWM Motor Speed Control.

Simulates DC motor speed control using PWM with soft-start ramp.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.pwm import PWM
from src.devices.motor import DCMotor


def main():
    print("=" * 60)
    print("  Experiment 5: PWM DC Motor Speed Control")
    print("=" * 60)

    mcu = MCUSimulator("STM32F103C8")
    pwm = PWM("PWM1")
    mcu.attach_peripheral("PWM1", pwm)

    motor = DCMotor("M1", max_rpm=3000.0)
    motor.enable()

    pwm.configure_channel(1, duty_percent=0.0)
    pwm.enable()

    # Connect PWM output to motor speed
    pwm[1].on_change(lambda val: motor.set_speed(val))

    print("[INFO] PWM1_CH1 -> DC Motor M1")
    print("[INFO] Base PWM frequency: {:.1f} Hz".format(pwm.get_base_frequency()))
    print("[INFO] Starting soft-start ramp...")
    print()

    # Soft-start: ramp from 0% to 80% in 10% steps
    for duty in [10, 20, 30, 40, 50, 60, 70, 80]:
        pwm.configure_channel(1, duty_percent=duty)

        for _ in range(1000):
            mcu.tick()
            motor.update()

        print(f"  Duty: {duty:3d}%  |  Motor RPM: {motor.rpm:6.0f}  "
              f"({motor.speed_percent:.1f}%)  {'#' * (duty // 2)}")

    print()
    print("[RESULT] Motor final speed: {:.0f} RPM".format(motor.rpm))
    print(pwm.summary())


if __name__ == "__main__":
    main()
