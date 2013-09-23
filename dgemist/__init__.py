# encoding:utf-8
#
# Download videos from the Dutch `Uitzending gemist' site.
#
# http://code.arp242.net/download-gemist
#
# Copyright © 2012-2013 Martin Tournoij <martin@arp242.net>
# See below for full copyright
#

from __future__ import print_function
import os, re, sys, time, json

if sys.version_info[0] < 3:
	import urllib2
	from HTMLParser import HTMLParser
else:
	import urllib.request as urllib2
	from html.parser import HTMLParser

__all__ = ['OpenUrl', 'GetVersion', 'CheckUpdate', 'HumanSize', 'HumanTime',
	'GetListing', 'FindVideo', 'DownloadVideo']

_verbose = False


class DgemistError(Exception):
	pass


def OpenUrl(url, cookie=''):
	""" Build request, fake headers & mandatory cookie
	Returns urllib2.urlopen (file-like object) """

	if _verbose:
		print('OpenUrl url: ' + url)

	headers = {
		'User-Agent': 'Opera/9.80 (X11; FreeBSD 9.1-RELEASE-p3 amd64) Presto/2.12.388 Version/12.15',
		'Cookie': 'npo_cc=30; ' + cookie,
	}
	req = urllib2.Request(url, headers=headers)
	page = urllib2.urlopen(req)

	return urllib2.urlopen(req)


def GetVersion():
	""" Get version string """
	return '1.4, 2013-08-22'


def CheckUpdate():
	""" Check if there's a newer version
	returns None or new version string """
	# TODO


def HumanSize(bytesize, np=False):
	""" Return human-readable string of n bytes
	Use np to always return a whole number """
	i = 0
	while bytesize > 1024:
		bytesize /= 1024.0
		i += 1

	return ('%.1f %s' if i > 1 else '%i %s') % (bytesize,
		('b', 'KiB', 'MiB', 'GiB')[i])


def HumanTime(s):
	""" Return human-readable string of n seconds """
	if s > 3600:
		return '%02ih%02im%02is' % (s / 3600, s / 60 % 60, s % 60)
	if s > 60:
		return '%02im%02is' % (s / 60, s % 60)
	return '%02is' % s


def GetListing(url, pages=0):
	""" Get program listing starting from URL, we fetch the current page + pages
	Returns list with (epid, title, url, description) """

	videos = []
	for page in range(1, pages + 2):
		data = OpenUrl('%s/afleveringen?page=%s' % (url, page)).read()
		if sys.version_info.major > 2: data = data.decode()

		matches = re.findall('<li class="episode active knav".*?data-remote-id="\d+?"'
			+ ' id="episode_(\d+)">.*?<a href="/afleveringen/\d+?" '
			+ 'class="episode active knav_link" title="(.+?)">.+?</h3>(.+?)</div>',
			data, re.MULTILINE | re.DOTALL)

		for epid, title, desc in matches:
			videos.append((epid,
				HTMLParser().unescape(re.sub('\(.*?\)', '', title)).strip(),
				'http://www.uitzendinggemist.nl/afleveringen/%s' % (epid),
				HTMLParser().unescape(desc).strip()))

	return videos


def FindVideo(url):
	""" Find video to download
	Returns (downloadurl, pagetitle, playerId, cookie)
	The cookie is a session cookie, which is required when downloading the video
	"""

	data = OpenUrl(url).read()
	if sys.version_info.major > 2: data = data.decode()

	try:
		playerId = re.search('data-player-id="(.*?)"', data).groups()[0]
	except AttributeError:
		raise DgemistError('Kan playerId niet vinden')

	if _verbose: print('Using playerId ' + playerId)

	jsdata = OpenUrl('http://ida.omroep.nl/npoplayer/i.js').read()[-200:]
	if sys.version_info.major > 2: jsdata = jsdata.decode()
	try:
		token = re.search('token = "(.*?)"', jsdata).groups()[0]
	except AttributeError:
		raise DgemistError('Kan token niet vinden')

	if _verbose: print('Using token ' + token)

	title = re.search('<title>(.+) - Uitzending Gemist</title>', data)
	title = HTMLParser().unescape(title.groups()[0]).strip()

	jsondata = OpenUrl('&'.join([
		'http://ida.omroep.nl/odiplus/?prid=%s' % playerId,
		'puboptions=adaptive,h264_bb,h264_sb,h264_std,wmv_bb,wmv_sb,wvc1_std',
		'adaptive=no',
		'part=1',
		'token=%s' % token,
		'callback=jQuery182022468003216732735_1377114929273',
		'_=%s303' % time.time(),
	])).read()

	if sys.version_info.major > 2: jsondata = jsondata.decode()
	jsondata = re.sub('^[\w\d]+\(', '', jsondata[:-1])
	download = json.loads(jsondata)['streams'][0]
	cookie = ''

	return (download, title, playerId, cookie)


def DownloadVideo(videourl, sesscookie, outfile, dryrun=False):
	""" Download a video and save to outfile (can be - for stdout).
	This is a generator
	yields (total_bytes, bytes_completed, avg_speed_bytes)
	"""

	if outfile == '-':
		fp = sys.stdout
	else:
		fp = open(outfile, 'wb+')

	video = OpenUrl(videourl, sesscookie)

	total = int(video.info().get('Content-Length'))
	totalh = HumanSize(total)
	starttime = time.time()
	speed = i = ptime = 0

	if dryrun:
		return

	while True:
		data = video.read(8192)
		i += 8192
		if not data:
			break

		fp.write(data)

		curtime = time.time()
		if curtime - starttime > 2:
			speed = int(i / (curtime - starttime))
		yield (total, i, speed)

	if fp != sys.stdout:
		fp.close()


def MakeFilename(outdir, title, playerId, safe=True, nospace=True, overwrite=False):
	""" Make a filename from the page title """

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
