# AGENTS.md

## Project: Embedded Virtual Lab

ARM Cortex-M embedded peripheral simulation framework for NJUST embedded systems education.

## AI Assistance Summary

This project was built with AI assistance (MiMo 10B Token Program). The AI helped with:

1. **Architecture Design**: Analyzing STM32 reference manuals to model MCU clock tree, NVIC, memory map, and peripheral register mappings
2. **Code Generation**: ~3000 lines of Python implementing 7 peripherals (GPIO/ADC/UART/Timer/PWM/I2C/SPI), 6 virtual devices, 2 visualization modes
3. **Test Suite**: 9 unit tests covering core simulation accuracy
4. **Documentation**: Bilingual README with architecture diagrams, API examples, and simulation fidelity comparison

## Usage

```bash
# Run experiments
python experiments/exp01_gpio_led.py

# Run tests
python tests/test_peripherals.py
```

## Git Workflow (for team members)

```bash
git clone https://github.com/ais1231/embedded-virt-lab.git
cd embedded-virt-lab
# make changes...
git add .
git commit -m "descriptive message"
git push
```
