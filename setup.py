#!/usr/bin/env python

import glob, sys, subprocess, os, re
from distutils.core import setup

import dgemist
version = dgemist.GetVersion()[0]

# Windows
if sys.platform == 'win32':
	if '#define MyAppVersion "%s"\r\n' % version not in open('setup.iss').readlines():
		print('Ook versie in setup.iss ophogen')
		sys.exit(1)

	from cx_Freeze import setup, Executable

	setup(
		name = 'download-gemist',
		version = version,
		author = 'Martin Tournoij',
		author_email = 'martin@arp242.net',
		url = 'http://code.arp242.net/download-gemist',
		description = '',
		options = {
			'build_exe': {
				#'excludes': ['_ssl', '_hashlib', '_ctypes', 'bz2', 'email', 'unittest', 'doctest',
				'excludes': ['_ssl', '_hashlib', '_ctypes', 'bz2', 'unittest', 'doctest',
					'locale', 'optparse',],
			}
		},
		executables = [
			Executable(
				script = 'download-gemist',
				compress = True,
				icon = './icon.ico',
			),
			Executable(
				script = 'download-gemist-gui',
				base = 'Win32GUI',
				compress = True,
				icon = './icon.ico',
			),
		]
	)

	filelist = [
		('', ['README.md']),
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
		name = 'download-gemist',
		version = version,
		author = 'Martin Tournoij',
		author_email = 'martin@arp242.net',
		url = 'http://code.arp242.net/download-gemist',
		packages = ['dgemist'],
		scripts = glob.glob('download-*'),
		data_files = [
			('share/doc/download-gemist', ['README.markdown']),
		],
	)
