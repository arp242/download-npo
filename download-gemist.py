#!/usr/bin/env python
#
# Download file from the Dutch `Uitzending gemist' site.
#
# https://bitbucket.org/Carpetsmoker/download-gemist
#
# Copyright (c) 2012 Martin Tournoij <martin@arp242.net>
# Freely redistributable and modifiable under the terms of the MIT license
# http://opensource.org/licenses/MIT 
#

import getopt
import re
import sys
import urllib2

_verbose = False
_silent = False

def Help():
	print '%s [-hvV] [-o output_dir] [-f output_file] [url url2...]' % sys.argv[0]
	print ''
	print 'Video URL\'s can be added can be added to the commandline, or read from stdin'
	print '  -o    Set output directory. Default is current directory.'
	print '  -f    Set output filename, relative to -o. The default is the title of'
	print '        the video. Use - for stdout.'
	print '  -h    Show this help.'
	print '  -v    Show version.'
	print '  -V    Show verbose information.'
	print '  -s    Silent. Don\'t show any informational messages'
	print ''

def Version():
	print 'download-gemist 1.0, 2012-10-03'
	print 'https://bitbucket.org/Carpetsmoker/download-gemist'
	print ''
	print 'Copyright (c) Martin Tournoij <martin@arp242.net>'
	print 'Freely redistributable and modifiable under the terms of the MIT license'
	print 'http://opensource.org/licenses/MIT'


def OpenUrl(url):
	"""
	Build request, fake headers
	"""
	headers = {
		'User-Agent': 'Opera/9.80 (X11; FreeBSD 9.0-RELEASE amd64; U; en) Presto/2.10.289 Version/12.02',
	}
	req = urllib2.Request(url, headers=headers)
	page = urllib2.urlopen(req)

	if _verbose:
		print 'OpenUrl url: ' + url

	return (page.info(), page.read())

def VideoRequest(url, cookie):
	"""
	Build request to mp4 video page
	"""

	headers = {
		'User-Agent': 'Opera/9.80 (X11; FreeBSD 9.0-RELEASE amd64; U; en) Presto/2.10.289 Version/12.02',
		'Cookie': cookie,
	}
	req = urllib2.Request(url, headers=headers)

	if _verbose:
		print 'DownloadVideo url: ' + url
	return urllib2.urlopen(req)

def DownloadVideo(url, outdir, filename):
	"""
	Download a video!
	"""
	head, data = OpenUrl(url)

	# <meta content="http://embed.player.omroep.nl/fle/ugfl.swf?episodeID=14099311&amp;volume=100" property="og:video" />
	episode = re.search('<meta content="http.*episodeID=(\d+)', data)
	if not episode:
		print >> sys.stderr, 'Error: Unable to find episodeId'
		sys.exit(1)

	episode = episode.groups()[0]
	if _verbose:
		print 'Using episodeId ' + episode

	if not filename:
		# <title>Andere tijden: De genezen homo - Uitzending Gemist</title>
		title = re.search('<title>(.+) - Uitzending Gemist</title>', data)
		title = title.groups()[0]
		filename = '%s-%s.mp4' % (title.strip().replace(':', '').replace(' ', '_'), episode)

	head, data = OpenUrl('http://www.uitzendinggemist.nl/player/' + episode)

	#cookie = 'balancer://ico15cluster=balancer.;' + head.get('Set-Cookie').split(';')[0]
	cookie = head.get('Set-Cookie').split(';')[0]

	if _verbose:
		print 'Using cookie' + cookie

	# `std' seems to be the highest quality, `bb' slightly lower, `sb' a lot
	# lower
	# <source src="/video_streams/NPS_1198670/h264_std?hash=6e6b0f9d328d5292c7336786a3e2cb77f8b0472e" type="video/mp4"></source>
	# <source src="/video_streams/NPS_1198670/h264_bb?hash=6e6b0f9d328d5292c7336786a3e2cb77f8b0472e" type="video/mp4"></source>
	# <source src="/video_streams/NPS_1198670/h264_sb?hash=6e6b0f9d328d5292c7336786a3e2cb77f8b0472e" type="video/mp4"></source>
	videos = re.findall('<source src="(.*)" type', data)

	if not videos:
		print >> sys.stderr, 'Error: Unable to find videos'
		sys.exit(1)

	if _verbose:
		print 'Found videos: ', videos

	download = None
	for v in videos:
		if 'h264_std' in v:
			download = 'http://www.uitzendinggemist.nl' + v
			break

	if not _silent:
		print "Saving to %s/%s" % (outdir, filename)

	video = VideoRequest(download, cookie)
	total = int(video.info().get('Content-Length')) / 1024 / 1024
	i = 0

	if filename == '-':
		fp = sys.stdout
	else:
		fp = open('%s/%s' % (outdir, filename), 'wb+')

	while True:
		data = video.read(8192)
		if not data:
			break

		if not _silent and i % 4 == 0:
			sys.stdout.write('\r%s MiB of %s MiB total' % (i / 1024, total))
			sys.stdout.flush()
		fp.write(data)
		i += 8

	if filename != '-':
		fp.close()

	if not _silent:
		print '. Ok!'

if __name__ == '__main__':
	try:
		options, videos = getopt.getopt(sys.argv[1:], 'hvVso:f:')
	except getopt.GetoptError:
		print >> sys.stderr, 'Error:', sys.exc_info()[1]
		Help()
		sys.exit(1)

	outdir = '.'
	filename = None
	for flag, arg in options:
		if flag == '-h':
			Help()
			sys.exit(0)
		elif flag == '-v':
			Version()
			sys.exit(0)
		elif flag == '-V':
			_verbose = True
		elif flag == '-s':
			_silent = True
		elif flag == '-o':
			outdir = arg
		elif flag == '-f':
			filename = arg

	if _silent or filename == '-':
		_silent = True

	if len(videos) == 0:
		videos = sys.stdin.read().strip().split(' ')
		#print >> sys.stderr, 'Error: No video URL'
		#Help()
		#sys.exit(1)

	for v in videos:
		if v == '':
			continue
		if _verbose:
			print 'Downloading ' + v
		DownloadVideo(v, outdir, filename)
