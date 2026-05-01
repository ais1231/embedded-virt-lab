"""Experiment 1: GPIO LED Blink - Hello World of embedded systems.

Simulates an LED connected to PA0 with a blinking pattern.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.gpio import GPIO, GPIOMode, GPIOConfig
from src.devices.led import LED


def main():
    print("=" * 60)
    print("  Experiment 1: GPIO LED Blink")
    print("=" * 60)

    # Initialize MCU and peripherals
    mcu = MCUSimulator("STM32F103C8")
    gpioa = GPIO('A')
    mcu.attach_peripheral("GPIOA", gpioa)

    # Configure PA0 as push-pull output at 50MHz
    gpioa.configure_pin(0, GPIOMode.OUTPUT_50MHZ, GPIOConfig.PUSH_PULL)

    # Attach an LED to PA0
    led = LED("LED1", "red")
    gpioa[0].on_change(lambda val: led.on() if val else led.off())

    print("[INFO] System Clock: {:.1f} MHz".format(mcu.system_clock_hz / 1e6))
    print("[INFO] PA0 configured as push-pull output")
    print("[INFO] LED1 attached to PA0")
    print()

    # Blink pattern: 5 cycles of on/off
    for i in range(5):
        gpioa[0].write(1)
        print(f"  Cycle {i+1}: LED ON  {led}")
        mcu.delay_ms(500)

        gpioa[0].write(0)
        print(f"  Cycle {i+1}: LED OFF {led}")
        mcu.delay_ms(500)

    print()
    print("[DONE] Experiment complete. LED blinked {} times.".format(led._blink_count))
    print(gpioa.summary())


if __name__ == "__main__":
    main()
