"""Experiment 2: ADC Temperature Sensor Reading.

Simulates reading a temperature sensor via ADC, implementing
oversampling and moving average filtering.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.adc import ADC, ADCChannel
from src.devices.sensor import TemperatureSensor


def main():
    print("=" * 60)
    print("  Experiment 2: ADC Temperature Sensor Reading")
    print("=" * 60)

    mcu = MCUSimulator("STM32F103C8")
    adc = ADC("ADC1")
    mcu.attach_peripheral("ADC1", adc)

    sensor = TemperatureSensor("LM35", ambient=25.0, noise=0.05)
    adc.enable()
    adc.set_channel(ADCChannel.CH0)

    print("[INFO] LM35 temperature sensor on ADC1_CH0")
    print("[INFO] Reference voltage: {:.2f}V, Resolution: 12-bit".format(ADC.VREF))
    print()

    samples = []
    for i in range(20):
        temp = sensor.read()
        # LM35: 10mV per degree C -> Vout = temp * 0.01
        voltage = temp * 0.01 + 0.5  # offset for 0C at 0.5V
        adc.inject_value(ADCChannel.CH0, voltage)
        adc.start_conversion()
        raw = adc.read()
        measured_v = adc.read_voltage()
        measured_temp = (measured_v - 0.5) / 0.01
        samples.append(measured_temp)
        print(f"  Sample {i+1:2d}: Raw=0x{raw:03X}  Voltage={measured_v:.3f}V  "
              f"Temp={measured_temp:.2f}C")

    avg = sum(samples) / len(samples)
    print()
    print("[RESULT] Average temperature: {:.2f} C".format(avg))
    print("[RESULT] Sensor average: {:.2f} C".format(sensor.average()))


if __name__ == "__main__":
    main()
