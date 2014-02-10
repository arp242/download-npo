import glob, os, shutil, sys
from cx_Freeze import setup, Executable


setup(
	name = 'download-gemist',
	version = '1.6.2',
	author = 'Martin Tournoij',
	author_email = 'martin@arp242.net',
	url = 'http://code.arp242.net/download-gemist',
	description = '',
	options = {
		'build_exe': {
			'excludes': ['_ssl', '_hashlib', '_ctypes', 'bz2', 'email', 'unittest', 'doctest',
				'locale', 'optparse',],
		}
	},
	executables = [
		Executable(
			script = 'download-gemist',
			compress = True,
			#icon = './data/icons/icon.ico',
		),
		Executable(
			script = 'download-gemist-gui',
			base = 'Win32GUI',
			compress = True,
			#icon = './data/icons/icon.ico',
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
