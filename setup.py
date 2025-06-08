from setuptools import setup, find_packages

setup(
    name="timecard-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "nfcpy>=1.0.4",
        "gspread>=5.10.0",
        "oauth2client>=4.1.3",
        "pyyaml>=6.0.1",
        "pygame>=2.5.1",
    ],
    author="Yossan-c4s",
    description="NFC-based Timecard System with Google Spreadsheet integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Yossan-c4s/timecard-system",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.7",
)