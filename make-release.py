#!/usr/bin/env python

import sys, subprocess, os
import dgemist
version = dgemist.GetVersion()[0]

# I keep forgetting to increment the version number before release :-/
if dgemist.CheckUpdate() is None:
	print("Je hebt het versienummer niet opgehoogd sukkel")
	sys.exit(1)

if sys.platform != 'win32':
	subprocess.call(
		r"sed -E -i.orig 's/download-gemist(-setup)?-[0-9.]{3,5}\.(exe|tar\.gz)/download-gemist\1-%s.\2/' README.md" % version,
		shell=True)
	os.unlink('README.md.orig')
