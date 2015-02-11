__author__ = 'karec'

import os
from setuptools import setup
from octbrowser import __version__

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='oct',
    version=__version__,
    author='Emmanuel Valette',
    author_email='manu.valette@gmail.com',
    packages=['octbrowser'],
    description="A library based on multi-mechanize for performances testing, using custom browser for writing tests",
    long_description=long_description,
    url='https://github.com/karec/oct-browser',
    download_url='https://github.com/karec/oct-browser/archive/master.zip',
    keywords=['testing', 'mechanize', 'webscrapper', 'browser', 'web', 'lxml', 'html'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4'
    ],
    install_requires=[
        'argparse',
        'requests',
        'lxml',
        'cssselect',
        'tinycss',
        'six'
    ]
)
