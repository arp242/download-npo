# encoding:utf-8
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-201% Martin Tournoij <martin@arp242.net>
# See below for full copyright

import sys, json, time, re, os

if sys.version_info[0] < 3:
	import urllib2
	import httplib
else:
	import urllib.request as urllib2
	import http.client

import download_npo

# These Classes are matched to the URL (using the match property). First match
# wins.
sites = [
	'OmroepBrabant',
	'NPO',
	'NPOPlayer',
]

class Site():
	# matched against the URL (w/o protocol)
	match = None

	# Meta info about this broadcast
	_meta = {}

	def __init__(self):
		# TODO: Make this work for Python 2
		if download_npo.Verbose() >= 2:
			if sys.version_info[0] >= 3:
				http.client.HTTPConnection.debuglevel = 99
			else:
				httplib.HTTPConnection.debuglevel = 99


	def OpenUrl(self, url):
		""" Open a URI; return urllib.request.Request object """
		if download_npo.Verbose(): print('OpenUrl url: ' + url)

		headers = {
			'User-Agent': 'Opera/9.80 (X11; FreeBSD 9.1-RELEASE-p3 amd64) Presto/2.12.388 Version/12.15',
			'Cookie': 'npo_cc=30; npo_cc_meta=1.0.5:0',
		}
		req = urllib2.Request(url, headers=headers)

		return urllib2.urlopen(req)


	def OpenMMS(self, url):
		""" Open MMS URL """
		import download_npo.mms
		return download_npo.mms.MMS(url)


	def GetPage(self, url):
		""" Open URL, and read() the data """
		data = self.OpenUrl(url).read()
		if sys.version_info[0] > 2: data = data.decode()

		return data.strip()


	def GetJSON(self, url):
		""" Open URL, and read() the data, and parse it as JSON """
		data = re.sub(r'^[\w\d\?]+\(', r'',  self.GetPage(url))
		data = re.sub('[\);/epc\s]*$', '', data)
		data = json.loads(data)

		if download_npo.Verbose() >= 2:
			import pprint
			pprint.pprint(data)

		return data


	def DownloadVideo(self, video, outfile, dryrun=False, getsubs=False):
		""" Download a video and save to outfile (can be - for stdout).

		This is a generator
		yields (total_bytes, bytes_completed, avg_speed_bytes) """

		if outfile == '-': fp = os.fdopen(sys.stdout.fileno(), 'wb')
		elif not dryrun: fp = open(outfile, 'wb+')

		total = int(video.info().get('Content-Length'))
		totalh = download_npo.HumanSize(total)
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


	def FindVideo(self, url, quality=0): raise download_npo.DownloadNpoError('Not implemented')
	def Meta(self, playerId): raise download_npo.DownloadNpoError('Not implemented')
	def Subs(self, playerId): raise download_npo.DownloadNpoError('Deze site ondersteund geen ondertitels')


class NPOPlayer(Site):
	""" Base class voor NPOPlayer sites, this should work on all sites using the
	NPO player """

	match = '.*'
	_playerid_regex = '([A-Z][A-Z_]{1,7}_\d{6,9})'

	def FindVideo(self, url, quality=0):
		""" Find video to download
		Returns (downloadurl, playerId, extension)"""

		if not (url.startswith('http://') or url.startswith('https://')):
			url = 'http://%s' % url

		page = self.GetPage(url)
		try:
			playerId = re.search(self._playerid_regex, page).groups()[0]
		except AttributeError:
			raise download_npo.DownloadNpoError('Kan playerId niet vinden')
		if download_npo.Verbose(): print('Using playerId ' + playerId)

		try:
			token = re.search('token = "(.*?)"',
				self.GetPage('http://ida.omroep.nl/npoplayer/i.js')).groups()[0]
		except AttributeError:
			raise download_npo.DownloadNpoError('Kan token niet vinden')
		if download_npo.Verbose(): print('Found token ' + token)

		new_token = self.transform_token(token)
		if download_npo.Verbose(): print('Transformed token to ' + new_token)

		meta = self.Meta(playerId)
		if meta.get('streams') and type(meta['streams'][0]) == dict and meta['streams'][0]['formaat'] == 'wmv':
			return self.FindVideo_MMS(playerId)

		streams = self.GetJSON('&'.join([
			'http://ida.omroep.nl/odi/?prid=%s' % playerId,
			'puboptions=adaptive,h264_bb,h264_sb,h264_std,wmv_bb,wmv_sb,wvc1_std',
			'adaptive=no',
			'part=1',
			'token=%s' % new_token,
			'callback=cb',
			'_=%s' % time.time(),
		]))

		url = None
		errors = []
		for q, streamurl in enumerate(streams['streams'][quality:]):
			stream = self.GetJSON(streamurl)
			if stream.get('errorstring'):
				# Dit is vooral voor regionale afleveringen (lijkt het ...)
				if meta.get('streams') and len(meta['streams']) > 0:
					url = meta['streams'][0]['url']
					break
				else:
					sys.stderr.write("Warning: De kwaliteit `%s' lijkt niet beschikbaar.\n" % ['hoog', 'middel', 'laag'][q])
					sys.stderr.flush()
					errors.append(stream.get('errorstring'))
			else:
				url = stream['url']
				break

		if url is None:
			raise download_npo.DownloadNpoError("Foutmelding van site: `%s'" % ', '.join(errors))

		return (self.OpenUrl(url), playerId, 'mp4')


	def transform_token(self, token):
		""" Silly tricks om het token te veranderen. Dit vermoedelijk een extra
		"bescherming" om dit soort dingen te voorkomen...

		Dit komt uit `function d(req)' in de JS. keyValue == token."""

		first = second = None
		for i, c in enumerate(token):
			try:
				int(c)
				is_int = True
			except ValueError:
				is_int = False

			if is_int and i > 4 and i < len(token) - 5:
				if first is None:
					first = i
				elif second is None:
					second = i

		new_token = [ c for c in token ]
		if first is not None and second is not None:
			new_token[first] = token[second]
			new_token[second] = token[first]
		else:
			new_token[12] = token[13]
			new_token[13] = token[12]

		return ''.join(new_token)


	def FindVideo_MMS(self, playerId):
		""" Old MMS format """

		if download_npo.Verbose(): print('Gebruik FindVideo_MMS')

		meta = self.Meta(playerId)
		stream = self.GetPage(meta['streams'][0]['url'])
		stream = re.search(r'"(mms://.*?)"', stream).groups()[0]
		if download_npo.Verbose(): print('MMS stream: %s' % stream)

		return (self.OpenMMS(stream), meta.get('title'), playerId, 'wmv')


	def Meta(self, playerId):
		if self._meta.get(playerId) is None:

			meta = self.GetJSON('http://e.omroep.nl/metadata/%s?callback=cd&version=5.1.0&_=%s' % (
				playerId, time.time()))

			# Hier lijkt zo vaak de helft van te ontbreken dat het niet opschiet
			#if meta.get('serie') is not None:
			#	meta['title'] = '%s %s' % (meta['serie']['serie_titel'], meta['aflevering_titel'])
			#else:
			meta['title'] = '%s' % meta['titel']
			self._meta[playerId] = meta

		return self._meta[playerId]


	def Subs(self, playerId):
		# Je zou verwachten dat je met het onderstaande uit de meta-data het
		# eea. over de ondertitels zou kunnen ophalen ... helaas werkt dat niet
		# zo, of misschien dat ik het niet goed doe... Voor nu gebruiken dus
		# hardcoded e.omroep.nl/tt888/, wat goed lijkt te werken.
		#self.Meta(playerId)
		#print('%s/%s/' % (meta['sitestat']['baseurl_subtitle'],
		#	meta['sitestat']['subtitleurl']))

		return self.OpenUrl('http://e.omroep.nl/tt888/%s' % playerId)


class NPO(NPOPlayer):
	match = '(www\.)?npo.nl'
	_playerid_regex = 'data-prid="(.*?)"'



class OmroepBrabant(Site):
	match ='(www\.)?omroepbrabant.nl'
	
	
	def FindVideo(self, url, quality=0):
		""" Find video to download
		Returns (downloadurl, pagetitle, playerId, extension)"""
		if not (url.startswith('http://') or url.startswith('https://')):
			url = 'http://%s' % url

		page = self.GetPage(url)
		try:
			jsurl = re.search('data-url="(.*?)"', page).groups()[0]
			playerId = re.search('sourceid_string:(\d+)', jsurl).groups()[0]
		except AttributeError:
			raise download_npo.DownloadNpoError('Kan playerId niet vinden')

		meta = self.Meta(playerId)

		streams = meta['clipData']['assets']
		streams.sort(key=lambda v: int(v['bandwidth']), reverse=True)
		url = streams[0]['src']

		return (self.OpenUrl(url), meta['clipData'].get('title'), playerId, 'mp4')


	def Meta(self, playerId):
		if self._meta.get(playerId) is None:
			page = self.GetPage('http://media.omroepbrabant.nl/p/Commercieel1/q/sourceid_string:%s.js' % playerId)
			page = re.search('var opts = (.*);', page).groups()[0]

			data = json.loads(page)
			del data['playerCSS']
			del data['playerHTML']

			#if meta.get('serie') is not None:
			#	meta['title'] = '%s %s' % (meta['serie']['serie_titel'], meta['aflevering_titel'])
			#else:
			#	meta['title'] = '%s' % meta['titel']

			self._meta[playerId] = data

		return self._meta[playerId]


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