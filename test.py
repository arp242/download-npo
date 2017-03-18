#!/usr/bin/env python3

import doctest
import unittest
import download_npo

#import coverage
#cov = coverage.Coverage()
#cov.start()

doctest.testmod(download_npo)

loader = unittest.TestLoader()
test = loader.discover('.', pattern='*_test.py')
runner = unittest.runner.TextTestRunner()
runner.run(test)

#cov.stop()
#cov.save()
#cov.report(omit=['*_test.py'])
