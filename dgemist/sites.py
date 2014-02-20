# encoding:utf-8

import sys, json, time, re

if sys.version_info[0] < 3:
	import urllib2
else:
	import urllib.request as urllib2

import dgemist

# These Classes are matched to the URL (using the match property). First match
# wins.
sites = [
	'UitzendingGemist',
	'NPO',
	'NPOPlayer',
]

class Site():
	# matched against the URL (w/o protocol)
	match = None

	# Meta info about this broadcast
	_meta = {}

	def OpenUrl(self, url):
		if dgemist.Verbose(): print('OpenUrl url: ' + url)

		headers = {
			'User-Agent': 'Opera/9.80 (X11; FreeBSD 9.1-RELEASE-p3 amd64) Presto/2.12.388 Version/12.15',
			'Cookie': 'npo_cc=30; npo_cc_meta=1.0.5:0',
		}
		req = urllib2.Request(url, headers=headers)
		page = urllib2.urlopen(req)

		return urllib2.urlopen(req)


	def OpenMMS(self, url):
		import dgemist.mms
		return dgemist.mms.MMS(url)

	def GetPage(self, url):
		data = self.OpenUrl(url).read()
		if sys.version_info.major > 2: data = data.decode()

		return data.strip()


	def GetJSON(self, url):
		data = re.sub(r'^[\w\d\?]+\(', r'',  self.GetPage(url))
		data = re.sub('[\);/epc\s]*$', '', data)
		data = json.loads(data)

		if dgemist.Verbose() >= 2:
			import pprint
			pprint.pprint(data)

		return data


	def DownloadVideo(self, video, outfile, dryrun=False):
		""" Download a video and save to outfile (can be - for stdout).

		This is a generator
		yields (total_bytes, bytes_completed, avg_speed_bytes) """

		if outfile == '-': fp = sys.stdout
		elif not dryrun: fp = open(outfile, 'wb+')

		#video = self.OpenUrl(url)

		total = int(video.info().get('Content-Length'))
		totalh = dgemist.HumanSize(total)
		starttime = time.time()
		speed = i = ptime = 0

		if dryrun: return

		while True:
			data = video.read(8192)
			i += 8192
			if not data: break;

			fp.write(data)

			curtime = time.time()
			if curtime - starttime > 2:
				speed = int(i / (curtime - starttime))
			yield (total, i, speed)

		if fp != sys.stdout: fp.close()


	def FindVideo(self, url): raise dgemist.DgemistError('Not implemented')
	def Meta(self, url): raise dgemist.DgemistError('Not implemented')


class NPOPlayer(Site):
	""" Base class voor NPOPlayer sites, this should work on all sites using the
	NPO player """

	match = '.*'

	# TODO: Regionale omroepen hebben een rare playerId, bv:
	# data-player-id="REG_FLEV_STR140220"
	# data-player-id="REG_BRAB_TV1512251"
	_playerid_regex = '([A-Z][A-Z_]{1,7}_\d{6,9})'

	def FindVideo(self, url):
		""" Find video to download
		Returns (downloadurl, pagetitle, playerId)"""

		try:
			playerId = re.search(self._playerid_regex, self.GetPage(url)).groups()[0]
		except AttributeError:
			raise dgemist.DgemistError('Kan playerId niet vinden')
		if dgemist.Verbose(): print('Using playerId ' + playerId)

		try:
			token = re.search('token = "(.*?)"',
				self.GetPage('http://ida.omroep.nl/npoplayer/i.js')).groups()[0]
		except AttributeError:
			raise dgemist.DgemistError('Kan token niet vinden')
		if dgemist.Verbose(): print('Using token ' + token)

		meta = self.Meta(playerId)
		if meta.get('streams') and meta['streams'][0]['formaat'] == 'wmv':
			return self.FindVideo_MMS(playerId)

		streams = self.GetJSON('&'.join([
			'http://ida.omroep.nl/odi/?prid=%s' % playerId,
			'puboptions=adaptive,h264_bb,h264_sb,h264_std,wmv_bb,wmv_sb,wvc1_std',
			'adaptive=no',
			'part=1',
			'token=%s' % token,
			'callback=cb',
			'_=%s' % time.time(),
		]))

		# TODO: Allow selecting of streams (ie. quality)
		stream = self.GetJSON(streams['streams'][0])

		if stream.get('errorstring'):
			# Dit is vooral voor regionale afleveringen (lijkt het ...)
			if meta.get('streams') and len(meta['streams']) > 0:
				url = meta['streams'][0]['url']
			else:
				raise dgemist.DgemistError("Foutmelding van site: `%s'" % stream['errorstring'])
		else:
			url = stream['url']

		return (self.OpenUrl(url), meta.get('title'), playerId, 'mp4')


	def FindVideo_MMS(self, playerId):
		""" Old MMS format """

		if dgemist.Verbose(): print('Gebruik FindVideo_MMS')

		meta = self.Meta(playerId)
		stream = self.GetPage(meta['streams'][0]['url'])
		stream = re.search(r'"(mms://.*?)"', stream).groups()[0]
		if dgemist.Verbose(): print('MMS stream: %s' % stream)

		return (self.OpenMMS(stream), meta.get('title'), playerId, 'wmv')


	def Meta(self, playerId):
		if self._meta.get(playerId) is None:
			meta = self.GetJSON('http://e.omroep.nl/metadata/aflevering/%s?callback=cb&_=%s' % (
				playerId, time.time()))

			if meta.get('serie') is not None:
				meta['title'] = '%s %s' % (meta['serie']['serie_titel'], meta['aflevering_titel'])
			else:
				meta['title'] = '%s' % meta['titel']
			self._meta[playerId] = meta

		return self._meta[playerId]



class UitzendingGemist(NPOPlayer):
	match = '^(www\.)?uitzendinggemist.nl'
	_playerid_regex = 'data-player-id="(.*?)"'


class NPO(NPOPlayer):
	match = '(www\.)?npo.nl'
	_playerid_regex = 'data-prid="(.*?)"'


# The MIT License (MIT)
#
# Copyright © 2012-2014 Martin Tournoij
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
