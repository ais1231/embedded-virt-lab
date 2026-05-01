from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="embedded-virt-lab",
    version="1.0.0",
    author="NJUST Embedded Systems Lab",
    description="ARM Cortex-M Embedded Peripheral Simulation Framework for Education",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/njust-emb/embedded-virt-lab",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "Topic :: Education",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
    ],
    extras_require={
        "dev": ["pytest", "pytest-cov", "black", "flake8"],
    },
)
