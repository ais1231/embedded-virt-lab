"""Experiment 7: SPI Sensor Data Acquisition.

Simulates SPI communication with a sensor device, collecting and
visualizing sensor data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.spi import SPI, SPIMode, SPIDataSize
from src.peripherals.gpio import GPIO, GPIOMode, GPIOConfig
from src.viz.plot import PlotView


def main():
    print("=" * 60)
    print("  Experiment 7: SPI Sensor Data Acquisition")
    print("=" * 60)

    mcu = MCUSimulator("STM32F103C8")
    spi = SPI("SPI1")
    mcu.attach_peripheral("SPI1", spi)

    # Configure GPIO for CS pin
    gpioa = GPIO('A')
    mcu.attach_peripheral("GPIOA", gpioa)
    gpioa.configure_pin(4, GPIOMode.OUTPUT_50MHZ, GPIOConfig.PUSH_PULL)

    spi.configure(mode=SPIMode.MODE_0, data_size=SPIDataSize.BITS_8, prescaler=16)
    spi.enable()

    print("[INFO] SPI1 configured: MODE0, 8-bit, {:.0f} kHz".format(
        spi.get_baud_rate() / 1000))
    print()

    # Simulate data from a virtual sensor
    import random
    random.seed(42)

    # Simulate sending register read commands and receiving data
    print("  SPI Sensor Read Sequence:")
    print("  " + "-" * 50)

    registers = {
        0x00: lambda: 0x5A,    # WHO_AM_I
        0x01: lambda: random.randint(0, 255),  # X_LSB
        0x02: lambda: random.randint(0, 255),  # X_MSB
        0x03: lambda: random.randint(0, 255),  # Y_LSB
        0x04: lambda: random.randint(0, 255),  # Y_MSB
        0x05: lambda: random.randint(0, 255),  # Z_LSB
        0x06: lambda: random.randint(0, 255),  # Z_MSB
        0x0F: lambda: random.randint(80, 120), # Temperature
    }

    accel_data = {'x': [], 'y': [], 'z': []}

    for i in range(10):
        # CS low
        gpioa[4].write(0)

        # Read WHO_AM_I
        whoami = registers[0x00]()
        print(f"  WHO_AM_I: 0x{whoami:02X}", end=" | ")

        # Read XYZ accelerometer data
        x = (registers[0x02]() << 8) | registers[0x01]()
        y = (registers[0x04]() << 8) | registers[0x03]()
        z = (registers[0x06]() << 8) | registers[0x05]()
        temp = registers[0x0F]()

        accel_data['x'].append(x)
        accel_data['y'].append(y)
        accel_data['z'].append(z)

        print(f"X={x:5d} Y={y:5d} Z={z:5d} T={temp:3d}")

        # CS high
        gpioa[4].write(1)

    print()
    print("[RESULT] SPI Stats: TX={} RX={}".format(
        spi.stats['tx_bytes'], spi.stats['rx_bytes']))
    print("[RESULT] Data samples collected: {}".format(len(accel_data['x'])))


if __name__ == "__main__":
    main()
