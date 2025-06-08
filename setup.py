from setuptools import setup, find_packages

setup(
    name="timecard-system",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "nfcpy",
        "gspread",
        "oauth2client",
        "pyyaml",
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