from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flatbat",
    version="1.0.0",
    author="tomasmckenna",
    author_email="tomas@mckenna.im",  # Replace with your email
    description="Minimalist tkinter system monitor overlay (CPU, RAM, GPU, battery, and clock)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tomasmckenna/flatbat",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.6",
    install_requires=[
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "flatbat=flatbat:run_flatbat",
        ],
    },
)
