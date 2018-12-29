#!/usr/bin/env python3

import doctest
import unittest
import download_npo
import download_npo.sites
import download_npo.cli
import download_npo.gui

doctest.testmod(download_npo)
for m in ('sites', 'cli', 'gui'):
    doctest.testmod(getattr(download_npo, m))

loader = unittest.TestLoader()
test = loader.discover('.', pattern='*_test.py')
runner = unittest.runner.TextTestRunner()
runner.run(test)
