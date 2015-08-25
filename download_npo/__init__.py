# encoding:utf-8
#
# Download videos from the Dutch `Uitzending gemist' site.
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-2015 Martin Tournoij <martin@arp242.net>
# See below for full copyright


from __future__ import print_function
import os, re, sys, unicodedata, locale

import download_npo.sites

if sys.version_info[0] < 3:
	import urllib2
else:
	import urllib.request as urllib2

__all__ = ['GetVersion', 'CheckUpdate', 'HumanSize', 'HumanTime',]

_verbose = 0


class DownloadNpoError(Exception): pass


def Verbose():
	return _verbose


def GetVersion():
	""" Get (version, release date), both as string """
	return ('2.0.1', '2015-07-04')


def CheckUpdate():
	""" Check if there's a newer version
	returns None or new version string
	
	>>> CheckUpdate() is None
	True
	"""

	if GetVersion()[1] == 'beta': return None

	try:
		page = urllib2.urlopen('http://code.arp242.net/download-npo/downloads').read().decode('utf-8')
		versions = re.findall('<td class="name">version-([0-9.]*?)</td>', page)
		versions.sort()
		latest = versions.pop()

		return (latest if latest != GetVersion()[0] else None)
	# Never fail
	except:
		if _verbose: print('CheckUpdate() failed\n%s' % sys.exc_info()[1])
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


def ReplaceVars(path, meta):
	return path.format(**{
		'episode_id': meta.get('prid', ''),
		'datum': meta.get('gidsdatum', ''),
		'titel': meta.get('titel', None) or meta.get('title', ''),
		'aflevering_titel': meta.get('aflevering_titel', ''),
		'tijdsduur': meta.get('tijdsduur', ''),
		'serie_id': meta.get('serie', {}).get('srid', ''),
		'serie_titel': meta.get('serie', {}).get('serie_titel', ''),
	})


def MakeFilename(outdir, title, ext, meta, safe=True, nospace=True, overwrite=False):
	""" Make a filename from the page title

	Placeholders:
	{episode_id}         Uniek nummer voor deze uitzending
	{datum}              Datum van uitzending
	{titel}              Titel; vaak is dit de serietitel
	{aflevering_titel}   Titel van de aflevering
	{tijdsduur}          Tijdsduur
	{serie_id}           Uniek nummer voor deze serie
	{serie_titel}        Titel van de serie; vaak is dit hetzelfde als de {titel}
	"""

	if title == '-': return '-'

	if title in [None, '']: title = u'{titel}-{episode_id}'
	if not title.endswith(ext): title += '.' + ext
	filename = ReplaceVars(title, meta)

	if safe:
		unsafe = r'"/\\*?<>|:'
		filename = ''.join([ f for f in filename if f not in unsafe ])
	if nospace:
		filename = filename.replace(' ', '_')

	outfile = u'%s/%s' % (outdir, filename)
	# TODO: This is not the best way to do this
	if locale.getpreferredencoding() != 'UTF-8':
		outfile = unicodedata.normalize('NFKD', outfile).encode('ascii', 'ignore').decode()

	if os.path.exists(outfile) and not overwrite:
			raise DownloadNpoError("Bestand `%s' overgeslagen omdat het al bestaat, " % outfile
				+ 'Gebruik -w voor overschrijven)')

	return outfile


def MakeOutdir(outdir, meta):
	outdir = download_npo.ReplaceVars(outdir, meta)

	if not os.path.exists(outdir):
		try:
			os.makedirs(outdir)
		except OSError:
			Error("Output directory `{}' bestaat niet, en kan ook niet gemaakt worden ({})".format(outdir, sys.exc_info()[1]))
			sys.exit(1)
	if not os.path.isdir(outdir):
		Error("Output directory `%s' bestaat maar is geen directory" % outdir)
		sys.exit(1)

	return outdir


def MatchSite(url):
	""" Return a Site object based from url """

	url = re.sub('^www\.', '', url.replace('http://', '').replace('https://', ''))

	sites = download_npo.sites.sites
	for s in download_npo.sites.sites:
		klass = getattr(download_npo.sites, s)
		if re.match(klass.match, url):
			if _verbose: print('Using site class %s' % klass)
			return klass()

	raise DownloadNpoError("Kan geen site vinden voor de URL `%s'" % url)


# TODO: Implement this
def GetDefaults():
	config_path = '{}/download-npo.conf'.format(
		os.getenv('XDG_CONFIG_HOME') or os.path.expanduser('~/.config'))

	if not os.path.exists(config_path):
		if _verbose: print('No config file at {}'.format(config_path))
	
	if _verbose: print('Reading config file from {}'.format(config_path))

	defaults = {
		'verbose': 0,
		'silent': 0,
		'outdir': '',
		'filename': '',
		'dryrun': '',
		'overwrite': '',
		'replacespace': '',
		'safefilename': '',
		'metaonly': '',
		'getsubs': '',
		'quality': '',
	}
	for line in open(config_path, 'r'):
		line = line.strip()
		
		if line[0] == '#' or line == '':
			continue

		k, v = line.split('=')
		defaults[k.strip().tolower()]  = v.strip()

	return defaults


# The MIT License (MIT)
#
# Copyright © 2012-2015 Martin Tournoij
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
