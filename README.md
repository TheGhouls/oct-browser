# oct-browser
Script browser based on the oct browser module for simple and intuitive web browsing using script

[![doc](https://readthedocs.org/projects/octbrowser/badge/?version=latest)](http://oct.readthedocs.org/en/latest/)
[![Supported Python versions](https://img.shields.io/badge/python-2.7--3.4-blue.svg)](https://pypi.python.org/pypi/octbrowser/)
[![pypi](https://img.shields.io/pypi/v/octbrowser.svg?style=flat)](https://pypi.python.org/pypi/octbrowser/)

[Documentation](http://octbrowser.readthedocs.org/en/latest/)

[OCTBrowser on pypi](https://pypi.python.org/pypi/octbrowser)

Python Version | Tested |
-------------- | -------|
Python >= 2.7.x|Tested|
Python >= 3.4|Tested|

Installation
------------

You can install OCTBrowser with pip :

`pip install octbrowser`

Or using setuptools :

`python setup.py install`

Changelogs
----------

0.4.1 to 0.4.2
==============

* Headers manipulation methods now update the session headers and make it avaible for all requests (thanks to Mark Owen)
* The ``submit_form`` method now send correcty the headers (thanks to Mark Owen)
* Now using SocketServer for unit testing (thanks to Mark Owen)
* Global unit tests improvements (thanks to Mark Owen)
