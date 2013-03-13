#!/usr/bin/env python

import glob
from distutils.core import setup

setup(
	name = 'download-gemist',
	version = '1.4',
	author = 'Martin Tournoij',
	author_email = 'martin@arp242.net',
	url = 'http://code.arp242.net/download-gemist',
	packages = ['dgemist'],
	scripts = glob.glob('download-*'),
	data_files = [
		('share/doc/download-gemist', ['README.md']),
	],

)
