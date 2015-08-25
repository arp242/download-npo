#!/usr/bin/env python

import sys, subprocess, os
import download_npo
version = download_npo.GetVersion()[0]

# I keep forgetting to increment the version number before release :-/
if download_npo.CheckUpdate() is None:
	print("Je hebt het versienummer niet opgehoogd sukkel")
	sys.exit(1)

if sys.platform != 'win32':
	subprocess.call(
		r"sed -E -i.orig 's/download-npo(-setup)?-[0-9.]{3,5}\.(exe|tar\.gz)/download-npo\1-%s.\2/' README.markdown" % version,
		shell=True)
	os.unlink('README.markdown.orig')


#if '#define MyAppVersion "%s"\r\n' % version not in open('setup.iss').readlines():
#	print('Ook versie in setup.iss ophogen')
#	sys.exit(1)

