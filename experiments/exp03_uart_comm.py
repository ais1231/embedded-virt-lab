"""Experiment 3: UART Serial Communication.

Simulates full-duplex UART communication between two virtual devices.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.mcu_sim import MCUSimulator
from src.peripherals.uart import UART, UARTBaudRate


def main():
    print("=" * 60)
    print("  Experiment 3: UART Serial Communication")
    print("=" * 60)

    # Create two MCUs for device-to-device communication
    mcu_a = MCUSimulator("Device-A")
    mcu_b = MCUSimulator("Device-B")

    uart_a = UART("USART1")
    uart_b = UART("USART2")
    mcu_a.attach_peripheral("USART1", uart_a)
    mcu_b.attach_peripheral("USART2", uart_b)

    # Link the two UARTs
    uart_a.link_to(uart_b)
    uart_a.enable()
    uart_b.enable()
    uart_a.configure(baud_rate=UARTBaudRate.B115200)

    print("[INFO] USART1 <---> USART2 linked at 115200 baud")
    print()

    # Test: Send messages between devices
    messages = [
        "Hello from Device-A!",
        "ACK: Message received.",
        "Sensor data: T=25.3C, H=68%",
        "Command: START_ACQUISITION",
        "Response: ACQUIRING..."
    ]

    for i, msg in enumerate(messages):
        if i % 2 == 0:
            uart_a.send_string(msg + "\n")
            print(f"  A -> B: {msg}")
        else:
            uart_b.send_string(msg + "\n")
            print(f"  B -> A: {msg}")

    print()
    print("[STATS] UART_A: TX={} RX={}".format(
        uart_a.stats['tx_bytes'], uart_a.stats['rx_bytes']))
    print("[STATS] UART_B: TX={} RX={}".format(
        uart_b.stats['tx_bytes'], uart_b.stats['rx_bytes']))


if __name__ == "__main__":
    main()
