#!/usr/bin/env python3

import doctest
import unittest
import download_npo
import download_npo.sites

doctest.testmod(download_npo)
doctest.testmod(download_npo.sites)

loader = unittest.TestLoader()
test = loader.discover('.', pattern='*_test.py')
runner = unittest.runner.TextTestRunner()
runner.run(test)
