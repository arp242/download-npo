#!/usr/bin/env python

import glob, sys, subprocess, os, re
from distutils.core import setup

import download_npo
version = download_npo.GetVersion()[0]

# Windows
if sys.platform == 'win32':
	from cx_Freeze import setup, Executable

	setup(
		name = 'download-npo',
		version = version,
		author = 'Martin Tournoij',
		author_email = 'martin@arp242.net',
		url = 'http://code.arp242.net/download-npo',
		description = '',
		options = {
			'build_exe': {
				'excludes': ['_ssl', '_hashlib', '_ctypes', 'bz2', 'unittest', 'doctest',
					'locale', 'optparse'],
			}
		},
		executables = [
			Executable(
				script = 'download-npo',
				compress = True,
				icon = './icon.ico',
			),
			Executable(
				script = 'download-npo-gui',
				base = 'Win32GUI',
				compress = True,
				icon = './icon.ico',
			),
		]
	)

	filelist = [
		('', ['README.markdown']),
	]

	for (destdir, files) in filelist:
		destdir = 'dist_win32/' + destdir
		if not os.path.exists(destdir):
			os.makedirs(destdir)
		
		for f in files:
			shutil.copy2(f, destdir)

	remove = [
		'tcl/encoding',
		'tcl/tzdata',
		'tcl/msgs',
		'tk/demos',
		'tk/images',
		'tk/msgs',
	]
	for f in remove: shutil.rmtree('dist_win32/%s' % f)
# Everything else
else:
	setup(
		name = 'download-npo',
		version = version,
		author = 'Martin Tournoij',
		author_email = 'martin@arp242.net',
		url = 'http://code.arp242.net/download-npo',
		packages = ['download_npo'],
		scripts = ['download-npo', 'download-npo-gui', 'play-npo'],
		data_files = [
			('share/doc/download-npo', ['README.markdown']),
		],
	)
