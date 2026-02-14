"""Setup configuration for Kafka Robot Fleet."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="kafka-robot-fleet",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Production-grade robot fleet management system using Apache Kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/kafka-robot-fleet",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "kafka-robot-fleet=kafka_robot_fleet.main:main",
        ],
    },
)
