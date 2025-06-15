# coding:utf8
from setuptools import setup


setup(
    name="easytrader",
    version="0.23.7",
    description="A utility for China Stock Trade",
    long_description="",
    long_description_content_type="text/markdown",
    author="shidenggui",
    author_email="longlyshidenggui@gmail.com",
    license="BSD",
    url="https://github.com/shidenggui/easytrader",
    keywords="China stock trade",
    install_requires=[
        "requests",
        "six",
        "easyutils",
        "flask",
        "pywinauto==0.6.6",
        "pillow",
        "pandas",
    ],
    extras_require={
        "miniqmt": ["xtquant"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: BSD License",
    ],
    packages=["easytrader", "easytrader.config", "easytrader.utils", "easytrader.miniqmt"],
    package_data={
        "": ["*.jar", "*.json"],
        "config": ["config/*.json"],
        "thirdlibrary": ["thirdlibrary/*.jar"],
    },
)
