"""Experiment 6: I2C Sensor Network.

Simulates multiple I2C devices on a shared bus with register read/write.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.i2c import I2C, I2CSpeed


def main():
    print("=" * 60)
    print("  Experiment 6: I2C Sensor Network")
    print("=" * 60)

    mcu = MCUSimulator("STM32F103C8")
    i2c = I2C("I2C1")
    mcu.attach_peripheral("I2C1", i2c)
    i2c.set_speed(I2CSpeed.FAST)
    i2c.enable()

    # Register virtual I2C devices
    i2c.register_device(0x48, "TMP102", {0x00: 0x7D, 0x01: 0x80})  # 25.0C
    i2c.register_device(0x77, "BMP280", {0xF7: 0x6F, 0xF8: 0xFC, 0xF9: 0x8C})
    i2c.register_device(0x68, "MPU6050", {0x3B: 0x00, 0x3C: 0x05, 0x43: 0x01})
    i2c.register_device(0x3C, "SSD1306", {0x00: 0xAE, 0x81: 0x7F})

    print("[INFO] I2C bus initialized at 400 kHz")
    print()

    # Scan bus
    devices = i2c.scan()
    print("  I2C Bus Scan Results:")
    for addr in devices:
        print(f"    Found device at 0x{addr:02X}")
    print()

    # Read sensor data
    print("  Reading sensor registers:")
    sensors = [(0x48, 0x00, "TMP102 Temp MSB"),
               (0x77, 0xF7, "BMP280 Press MSB"),
               (0x68, 0x3B, "MPU6050 Accel X High"),
               (0x3C, 0x00, "SSD1306 Display Status")]

    for addr, reg, name in sensors:
        try:
            value = i2c.read_register(addr, reg)
            print(f"    {name:24s} [0x{addr:02X}, 0x{reg:02X}] = 0x{value:02X}")
        except IOError:
            print(f"    {name:24s} [0x{addr:02X}, 0x{reg:02X}] = ERROR")

    # Write configuration
    print()
    print("  Writing configuration:")
    i2c.write_register(0x3C, 0x81, 0xCF)  # Set contrast
    value = i2c.read_register(0x3C, 0x81)
    print(f"    SSD1306 Contrast set to 0x{value:02X}")

    print()
    print(i2c.summary())


if __name__ == "__main__":
    main()
