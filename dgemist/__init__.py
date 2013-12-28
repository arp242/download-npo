# encoding:utf-8
#
# Download videos from the Dutch `Uitzending gemist' site.
#
# http://code.arp242.net/download-gemist
#
# Copyright © 2012-2013 Martin Tournoij <martin@arp242.net>
# See below for full copyright


from __future__ import print_function
import os, re, sys

import dgemist.sites

if sys.version_info[0] < 3:
	import urllib2
else:
	import urllib.request as urllib2

__all__ = ['GetVersion', 'CheckUpdate', 'HumanSize', 'HumanTime',]

_verbose = False


class DgemistError(Exception): pass


def Verbose():
	return _verbose


def GetVersion():
	""" Get (version, release date), both as string """
	return ('1.6', '2013-12-28')


def CheckUpdate():
	""" Check if there's a newer version
	returns None or new version string
	
	>>> CheckUpdate() is None
	True
	"""
	
	try:
		page = urllib2.urlopen('http://code.arp242.net/download-gemist/downloads').read().decode('utf-8')
		versions = re.findall('<td class="name">version-([0-9.]*?)</td>', page)
		versions.sort()
		latest = versions.pop()

		return (latest if latest != GetVersion()[0] else None)
	# Never fail
	except:
		return None


def HumanSize(bytesize, p=1):
	""" Return human-readable string of n bytes
	Use p to set the precision

	>>> HumanSize(42424242)
	'40,5 MiB'

	>>> HumanSize(42424242, 0)
	'40 MiB'

	>>> HumanSize(1024**3, 2)
	'1024,00 MiB'
	"""

	i = 0
	while bytesize > 1024:
		bytesize /= 1024.0
		i += 1

	bytesize = (('%.' + str(p) + 'f') % bytesize).replace('.', ',')
	return '%s %s' % (bytesize, ('b', 'KiB', 'MiB', 'GiB')[i])


def HumanTime(s):
	""" Return human-readable string of n seconds
	
	>>> HumanTime(42)
	'42s'

	>>> HumanTime(32490)
	'9h01m30s'
	"""

	if s > 3600:
		return '%ih%02im%02is' % (s / 3600, s / 60 % 60, s % 60)
	if s > 60:
		return '%im%02is' % (s / 60, s % 60)
	return '%02is' % s


def MakeFilename(outdir, title, playerId, safe=True, nospace=True, overwrite=False):
	""" Make a filename from the page title
	
	TODO: doctest
	"""

	if title == '-':
		return '-'

	filename = '%s-%s.mp4' % (title, playerId)
	if safe:
		unsafe = r'"/\\*?<>|:'
		filename = ''.join([ f for f in filename if f not in unsafe ])
	if nospace:
		filename = filename.replace(' ', '_')

	outfile = '%s/%s' % (outdir, filename)
	if os.path.exists(outfile) and not overwrite:
			raise DgemistError('Bestand overgeslagen omdat het al bestaat, '
				+ 'Gebruik -w voor overschrijven)')

	return outfile


def MatchSite(url):
	""" Return a Site object based from url """

	url = url.replace('http://', '').replace('https://', '')

	sites = dgemist.sites.sites
	for s in dgemist.sites.sites:
		clss = getattr(dgemist.sites, s)
		if re.match(clss.match, url):
			if _verbose: print('Using site class %s' % clss)
			return clss()

	raise DgemistError("Kan geen site vinden voor de URL `%s'" % url)



# The MIT License (MIT)
#
# Copyright © 2012-2013 Martin Tournoij
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# The software is provided "as is", without warranty of any kind, express or
# implied, including but not limited to the warranties of merchantability,
# fitness for a particular purpose and noninfringement. In no event shall the
# authors or copyright holders be liable for any claim, damages or other
# liability, whether in an action of contract, tort or otherwise, arising
# from, out of or in connection with the software or the use or other dealings
# in the software.
