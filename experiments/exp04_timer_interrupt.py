"""Experiment 4: Timer Interrupt Generation.

Demonstrates using a timer to generate periodic interrupts
and measuring timing accuracy.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.timer import Timer, TimerMode
from src.devices.led import LED


def main():
    print("=" * 60)
    print("  Experiment 4: Timer Interrupt Generation")
    print("=" * 60)

    mcu = MCUSimulator("STM32F103C8")
    tim2 = Timer("TIM2")
    mcu.attach_peripheral("TIM2", tim2)

    led = LED("LED_IRQ", "green")

    interrupt_count = [0]

    def timer_callback(timer):
        interrupt_count[0] += 1
        led.toggle()

    tim2.on_update(timer_callback)

    # Configure TIM2 for 1 Hz interrupt
    # 72MHz / (7200-1 + 1) / (10000-1 + 1) = 1 Hz
    tim2.set_prescaler(7200 - 1)
    tim2.set_auto_reload(10000 - 1)
    tim2.set_mode(TimerMode.UP)
    tim2.enable()

    print("[INFO] System Clock: {:.1f} MHz".format(mcu.system_clock_hz / 1e6))
    print("[INFO] TIM2 configured: PSC=7199, ARR=9999")
    print("[INFO] Theoretical frequency: {:.2f} Hz".format(tim2.get_frequency()))
    print("[INFO] Period: {:.2f} us".format(tim2.get_period_us()))
    print()

    # Run for 5 seconds of interrupts
    print("  Running timer for ~5 seconds...")
    for sec in range(5):
        mcu.delay_ms(1000)
        print(f"  T+{sec+1}s: Interrupts={interrupt_count[0]} "
              f"CNT={tim2.get_counter()} LED={led}")

    print()
    print("[RESULT] Total interrupts: {}".format(interrupt_count[0]))
    print("[RESULT] Expected: ~5 interrupts at 1 Hz")
    print(tim2.summary())


if __name__ == "__main__":
    main()
