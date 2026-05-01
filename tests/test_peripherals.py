"""Tests for Embedded Virtual Lab peripherals."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_mcu_initialization():
    """Test basic MCU initialization and clock tree."""
    from src.core.mcu_sim import MCUSimulator
    mcu = MCUSimulator("STM32F103C8")
    assert mcu.system_clock_hz == 72_000_000
    assert mcu.ahb_clock_hz == 72_000_000
    assert mcu.apb1_clock_hz == 36_000_000
    assert mcu.apb2_clock_hz == 72_000_000
    assert mcu.clock.system_clock == 72_000_000


def test_gpio_output():
    """Test GPIO output mode and pin toggling."""
    from src.peripherals.gpio import GPIO, GPIOMode, GPIOConfig, PinState
    gpio = GPIO('A')
    gpio.configure_pin(0, GPIOMode.OUTPUT_50MHZ, GPIOConfig.PUSH_PULL)

    gpio[0].write(1)
    assert gpio[0].read() == 1
    assert gpio[0].state == PinState.HIGH

    gpio[0].write(0)
    assert gpio[0].read() == 0

    gpio[0].toggle()
    assert gpio[0].read() == 1

    # Port-level operations
    gpio.write_port(0xFFFF)
    assert gpio.read_port() == 0xFFFF

    gpio.set_bits(0x000F)
    assert (gpio.read_port() & 0x000F) == 0x000F

    gpio.reset_bits(0x0003)
    assert (gpio.read_port() & 0x0003) == 0


def test_adc_conversion():
    """Test ADC voltage to code conversion."""
    from src.peripherals.adc import ADC, ADCChannel, ADCAlign
    adc = ADC("ADC1")
    adc.enable()
    adc.set_channel(ADCChannel.CH0)

    # 3.3V should give max code
    adc.inject_value(ADCChannel.CH0, 3.3)
    adc.start_conversion()
    assert adc.read() == 4095
    assert abs(adc.read_voltage() - 3.3) < 0.01

    # 0V should give 0
    adc.inject_value(ADCChannel.CH0, 0.0)
    adc.start_conversion()
    assert adc.read() == 0

    # 1.65V should be ~2047
    adc.inject_value(ADCChannel.CH0, 1.65)
    adc.start_conversion()
    assert abs(adc.read() - 2048) <= 10  # allow noise


def test_uart_link():
    """Test UART send/receive between linked devices."""
    from src.core.mcu_sim import MCUSimulator
    from src.peripherals.uart import UART, UARTBaudRate

    mcu_a = MCUSimulator("A")
    mcu_b = MCUSimulator("B")
    uart_a = UART("USART1")
    uart_b = UART("USART2")
    mcu_a.attach_peripheral("USART1", uart_a)
    mcu_b.attach_peripheral("USART2", uart_b)

    uart_a.link_to(uart_b)
    uart_a.enable()
    uart_b.enable()

    uart_a.send_byte(0x55)
    assert uart_b.available() == 1
    assert uart_b.read_byte() == 0x55

    uart_b.send_string("OK")
    assert uart_a.read_all() == b"OK"


def test_timer_frequency():
    """Test timer frequency calculation."""
    from src.core.mcu_sim import MCUSimulator
    from src.peripherals.timer import Timer, TimerMode

    mcu = MCUSimulator()
    tim = Timer("TIM2")
    mcu.attach_peripheral("TIM2", tim)

    # 72MHz / 7200 / 10000 = 1 Hz
    tim.set_prescaler(7199)
    tim.set_auto_reload(9999)
    assert abs(tim.get_frequency() - 1.0) < 0.01
    assert abs(tim.get_period_us() - 1_000_000) < 100


def test_pwm_duty_cycle():
    """Test PWM channel configuration."""
    from src.core.mcu_sim import MCUSimulator
    from src.peripherals.pwm import PWM

    mcu = MCUSimulator()
    pwm = PWM("PWM1")
    mcu.attach_peripheral("PWM1", pwm)

    pwm.configure_channel(1, duty_percent=50.0)
    assert pwm[1].duty_cycle == 50.0

    pwm.configure_channel(2, duty_percent=75.0)
    assert pwm[2].duty_cycle == 75.0


def test_i2c_register_rw():
    """Test I2C register read/write operations."""
    from src.peripherals.i2c import I2C

    i2c = I2C("I2C1")
    i2c.register_device(0x48, "TMP102", {0x00: 0x00})
    i2c.enable()

    i2c.write_register(0x48, 0x01, 0x60)
    assert i2c.read_register(0x48, 0x01) == 0x60

    # NACK on missing device
    try:
        i2c.read_register(0x50, 0x00)
        assert False, "Should raise IOError"
    except IOError:
        pass


def test_memory_rw():
    """Test memory read/write operations."""
    from src.core.memory import SRAM, Flash

    sram = SRAM(1024)
    sram.write_u32(0x20000000, 0xDEADBEEF)
    assert sram.read_u32(0x20000000) == 0xDEADBEEF

    sram.write_u16(0x20000004, 0x1234)
    assert sram.read_u16(0x20000004) == 0x1234

    sram.write_u8(0x20000010, 0xAB)
    assert sram.read_u8(0x20000010) == 0xAB

    flash = Flash(64 * 1024)
    flash.unlock()
    flash.write_u32(0x08000000, 0xCAFEBABE)
    assert flash.read_u32(0x08000000) == 0xCAFEBABE


def test_clock_tree():
    """Test clock tree configuration."""
    from src.core.clock import ClockTree, ClockSource, AHBPrescaler, APBPrescaler

    clk = ClockTree()
    # Default: 8MHz HSE, PLL x9 = 72MHz
    assert clk.system_clock == 72_000_000
    assert clk.ahb_clock == 72_000_000
    assert clk.apb1_clock == 36_000_000

    # Change to HSI
    clk.set_sysclk_source(ClockSource.HSI)
    assert clk.system_clock == 8_000_000

    # Change back and set prescaler
    clk.set_sysclk_source(ClockSource.PLL)
    clk.set_ahb_prescaler(AHBPrescaler.DIV2)
    assert clk.ahb_clock == 36_000_000


if __name__ == "__main__":
    tests = [
        test_mcu_initialization,
        test_gpio_output,
        test_adc_conversion,
        test_uart_link,
        test_timer_frequency,
        test_pwm_duty_cycle,
        test_i2c_register_rw,
        test_memory_rw,
        test_clock_tree,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            print(f"  [PASS] {test.__name__}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {test.__name__}: {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    sys.exit(0 if failed == 0 else 1)
