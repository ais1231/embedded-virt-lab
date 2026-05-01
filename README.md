# 🔬 Embedded Virtual Lab

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

**ARM Cortex-M 嵌入式外设仿真实验平台**

> 面向嵌入式系统教学的高保真外设仿真框架，支持 STM32F103 系列 MCU 外设的软件模拟与虚拟实验。无需硬件开发板即可进行 GPIO、ADC、UART、I2C、SPI、定时器、PWM 等外设编程实验。

## 📋 项目背景 / Background

本平台面向南京理工大学（NJUST）嵌入式系统课程教学，旨在解决硬件实验设备不足、学生课外练习困难等问题。通过纯 Python 实现的外设仿真框架，学生可以在任何计算机上完成嵌入式编程实验。

### 🎯 核心特性 / Features

- **⚡ 周期精确仿真**: 模拟 Cortex-M3 内核时钟树、NVIC 中断控制器、存储器映射
- **🔌 完整外设支持**: GPIO / ADC / UART / I2C / SPI / Timer / PWM / SysTick
- **📟 虚拟设备库**: LED、温度传感器、光敏传感器、直流电机、步进电机、OLED 显示屏
- **📊 可视化输出**: 终端实时监控界面 + Matplotlib 数据绘图
- **🧪 实验案例**: 7 个配套实验，从 LED 闪烁到 SPI 传感器数据采集
- **🐍 纯 Python**: 无需 Keil / IAR / 硬件调试器，开箱即用

## 🏗️ 系统架构 / Architecture

```
embedded-virt-lab/
├── src/
│   ├── core/           # MCU 内核仿真
│   │   ├── mcu_sim.py  # MCU 仿真器主控 (Cortex-M3 NVIC)
│   │   ├── memory.py   # 存储器模型 (Flash / SRAM / 内存映射)
│   │   └── clock.py    # 时钟树仿真 (HSI/HSE/PLL/总线分频)
│   ├── peripherals/    # 外设仿真模块
│   │   ├── gpio.py     # GPIO 端口/引脚 (推挽/开漏, CRL/CRH/BSRR 寄存器)
│   │   ├── adc.py      # 12-bit SAR ADC (扫描/连续模式, 注入通道)
│   │   ├── uart.py     # USART (全双工, 可配置波特率/帧格式)
│   │   ├── timer.py    # 通用定时器 + SysTick (向上/向下/中央对齐计数)
│   │   ├── pwm.py      # PWM 输出 (4通道, 占空比/频率可调)
│   │   ├── i2c.py      # I2C 总线 (主模式, 标准/快速模式, 多设备)
│   │   └── spi.py      # SPI 总线 (全双工, 4种模式, 主从架构)
│   ├── devices/        # 虚拟硬件设备
│   │   ├── led.py      # LED (亮度控制, 闪烁计数)
│   │   ├── sensor.py   # 温度/光照传感器 (高斯噪声, 可校准)
│   │   ├── motor.py    # DC 电机 / 步进电机 (惯性模型, 位置跟踪)
│   │   └── display.py  # OLED 显示屏 (128x64, SSD1306 兼容, 5x7 字模)
│   └── viz/            # 可视化
│       ├── terminal.py # 终端实时监控 (颜色/进度条/仪表盘)
│       └── plot.py     # Matplotlib 曲线图 (多通道, 实时刷新)
├── experiments/        # 实验案例
│   ├── exp01_gpio_led.py        # 实验1: GPIO LED 闪烁
│   ├── exp02_adc_sensor.py      # 实验2: ADC 温度传感器采集
│   ├── exp03_uart_comm.py       # 实验3: UART 串口通信
│   ├── exp04_timer_interrupt.py # 实验4: 定时器中断
│   ├── exp05_pwm_motor.py       # 实验5: PWM 电机调速
│   ├── exp06_i2c_display.py     # 实验6: I2C 传感器网络
│   └── exp07_spi_sensor.py      # 实验7: SPI 数据采集
├── tests/              # 单元测试
├── setup.py
└── requirements.txt
```

## 🚀 快速开始 / Quick Start

### 环境要求 / Requirements

- Python 3.8+
- numpy (可选，用于 ADC 噪声仿真)
- matplotlib (可选，用于数据绘图)

### 安装 / Installation

```bash
git clone https://github.com/njust-emb/embedded-virt-lab.git
cd embedded-virt-lab
pip install -r requirements.txt
```

### 运行实验 / Run Experiments

```bash
# 实验1: GPIO LED 闪烁
python experiments/exp01_gpio_led.py

# 实验2: ADC 温度传感器采集
python experiments/exp02_adc_sensor.py

# 实验3: UART 串口通信
python experiments/exp03_uart_comm.py

# 实验4: 定时器中断
python experiments/exp04_timer_interrupt.py

# 实验5: PWM 电机调速
python experiments/exp05_pwm_motor.py

# 实验6: I2C 传感器网络
python experiments/exp06_i2c_display.py

# 实验7: SPI 传感器数据采集
python experiments/exp07_spi_sensor.py
```

### 运行测试 / Run Tests

```bash
python tests/test_peripherals.py
```

## 📖 使用示例 / Usage Examples

### 创建仿真 MCU 并配置 GPIO

```python
from src.core.mcu_sim import MCUSimulator
from src.peripherals.gpio import GPIO, GPIOMode, GPIOConfig

mcu = MCUSimulator("STM32F103C8")
gpioa = GPIO('A')
mcu.attach_peripheral("GPIOA", gpioa)

# 配置 PA0 为推挽输出，最高 50MHz
gpioa.configure_pin(0, GPIOMode.OUTPUT_50MHZ, GPIOConfig.PUSH_PULL)

# 输出高电平
gpioa[0].write(1)
print(f"PA0 state: {gpioa[0].state.name}")  # HIGH
```

### 模拟 ADC 采集

```python
from src.peripherals.adc import ADC, ADCChannel

adc = ADC("ADC1")
adc.enable()
adc.set_channel(ADCChannel.CH0)

# 注入模拟电压 2.5V
adc.inject_value(ADCChannel.CH0, 2.5)
adc.start_conversion()

print(f"ADC raw: 0x{adc.read():03X}")          # ~0xC1D
print(f"ADC voltage: {adc.read_voltage():.3f}V")  # ~2.500V
```

### UART 设备间通信

```python
from src.peripherals.uart import UART, UARTBaudRate

uart_a = UART("USART1")
uart_b = UART("USART2")
uart_a.link_to(uart_b)
uart_a.enable()
uart_b.enable()

uart_a.send_string("Hello Embedded World!\n")
data = uart_b.read_all()
print(data.decode())  # "Hello Embedded World!\n"
```

### 定时器中断

```python
from src.peripherals.timer import Timer, TimerMode

tim2 = Timer("TIM2")
count = [0]

def on_update(timer):
    count[0] += 1

tim2.on_update(on_update)
tim2.set_prescaler(7199)    # 72MHz / 7200
tim2.set_auto_reload(9999)  # 1 Hz
tim2.enable()

mcu.run(72_000_000)  # 运行 1 秒
print(f"Interrupts: {count[0]}")  # 1
```

### I2C 总线操作

```python
from src.peripherals.i2c import I2C

i2c = I2C("I2C1")
i2c.enable()

# 注册设备
i2c.register_device(0x48, "TMP102", {0x00: 0x7D, 0x01: 0x80})

# 读写寄存器
temp_msb = i2c.read_register(0x48, 0x00)
i2c.write_register(0x48, 0x01, 0x60)

# 扫描总线
print([f"0x{a:02X}" for a in i2c.scan()])  # ['0x48']
```

### PWM 电机控制

```python
from src.peripherals.pwm import PWM
from src.devices.motor import DCMotor

pwm = PWM("PWM1")
motor = DCMotor("M1", max_rpm=3000.0)

pwm.configure_channel(1, duty_percent=75.0)
motor.enable()
motor.set_speed(0.75)

for _ in range(1000):
    mcu.tick()
    motor.update()

print(f"Motor speed: {motor.rpm:.0f} RPM")  # ~2250 RPM
```

## 🎓 实验列表 / Experiments

| # | 实验名称 | 外设 | 知识点 |
|---|---------|------|--------|
| 1 | GPIO LED 闪烁 | GPIO | 端口配置、输出控制、延时 |
| 2 | ADC 温度采集 | ADC | 模数转换、过采样、传感器校准 |
| 3 | UART 串口通信 | UART | 全双工通信、帧格式、异步收发 |
| 4 | 定时器中断 | Timer | 预分频器、自动重载、中断回调 |
| 5 | PWM 电机调速 | PWM | 占空比控制、电机惯性模型 |
| 6 | I2C 传感器网络 | I2C | 总线仲裁、寄存器读写、多设备 |
| 7 | SPI 数据采集 | SPI | 全双工传输、CS 片选、时序 |

## 🧠 仿真精度 / Simulation Fidelity

| 特性 | 仿真级别 |
|------|---------|
| 时钟树 (HSI/HSE/PLL/分频) | 寄存器级 |
| GPIO (CRL/CRH/IDR/ODR/BSRR) | 寄存器级 |
| ADC (12-bit SAR + 高斯噪声) | 行为级 + 物理噪声 |
| UART (帧格式/波特率) | 功能级 + 时序 |
| Timer (向上/向下/中央对齐) | 周期精确 |
| PWM (占空比/频率/极性) | 周期精确 |
| I2C (主模式 7-bit 寻址) | 协议级 |
| SPI (4种模式 全双工) | 协议级 |
| NVIC 中断控制器 | 架构级 |

## 🌐 技术栈 / Tech Stack

- **语言**: Python 3.8+
- **数值计算**: numpy (可选，ADC 噪声模型)
- **可视化**: matplotlib (可选，数据曲线)
- **测试**: unittest / pytest
- **目标器件**: STM32F103C8T6 (ARM Cortex-M3, 72MHz)

## 🤝 贡献 / Contributing

欢迎提交 Issue 和 Pull Request。

## 📄 许可 / License

MIT License - 详见 [LICENSE](LICENSE) 文件。

---
*Nanjing University of Science and Technology · School of Electronic and Optical Engineering*
