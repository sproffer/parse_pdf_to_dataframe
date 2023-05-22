"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['pdf-to-dataframe.py']
DATA_FILES = ['sample1.pdf','sample2.pdf']
OPTIONS = {}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
