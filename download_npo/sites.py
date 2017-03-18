# encoding:utf-8
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-2017 Martin Tournoij <martin@arp242.net>
# See below for full copyright

from __future__ import print_function

import sys
import json
import time
import re
import os
import download_npo

if sys.version_info[0] < 3:
    import urllib2
    import httplib
    from urllib import unquote
else:
    import urllib.request as urllib2
    import http.client
    from urllib.parse import unquote

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

    def openURL(self, url):
        """ Open a URI; return urllib.request.Request object """
        if download_npo.Verbose():
            print('openURL: ' + url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
            'Cookie': 'npo_cc=tmp; npo_cc_www.npogeschiedenis.nl=tmp',
        }
        req = urllib2.Request(url, headers=headers)
        try:
            return urllib2.urlopen(req)
        except urllib2.HTTPError:
            raise download_npo.Error(
                'De URL {} is niet gevonden (404 error)'.format(url))

    def openMMS(self, url):
        """ Open MMS URL """
        import download_npo.mms
        return download_npo.mms.MMS(url)

    def get_page(self, url):
        """ Open URL, and read() the data """
        data = self.openURL(url).read()
        if sys.version_info[0] > 2:
            data = data.decode()
        return data.strip()

    def get_json(self, url):
        """ Open URL, and read() the data, and parse it as JSON """
        data = re.sub(r'^[\w\d\?]+\(', r'', self.get_page(url))
        data = re.sub(r'[\);/eprc\s]*$', '', data)
        data = json.loads(data)

        if download_npo.Verbose() >= 2:
            import pprint
            pprint.pprint(data)

        return data

    def write_meta(self, player_id, path):
        """ Try to write metadata to the file. """

        try:
            if path.endswith('.mp4'):
                from mutagen.mp4 import MP4
                meta = self.meta(player_id)
                fp = MP4(path)
                fp['tvsh'] = meta.get('serie', {}).get('serie_titel', '')
                fp['desc'] = (meta.get('aflevering_titel', '') or
                              meta.get('titel', None) or
                              meta.get('title', ''))
                fp.save()
            elif path.endswith('.mp3'):
                from mutagen.mp3 import MP3
                meta = self.meta(player_id)
                fp = MP3(path)
                # TODO
                fp.save()
        except ImportError:
            print('\nmutagen module niet gevonden; metadata niet ingesteld.',
                file=sys.stderr)
            return

    def download_video(self, player_id, video, outfile, dryrun=False, getsubs=False):
        """ Download a video and save to outfile (can be - for stdout).

        This is a generator
        yields (total_bytes, bytes_completed, avg_speed_bytes) """

        if outfile == '-':
            fp = os.fdopen(sys.stdout.fileno(), 'wb')
        elif not dryrun:
            fp = open(outfile, 'wb+')

        total = int(video.info().get('Content-Length'))
        starttime = time.time()
        speed = i = 0

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
            self.write_meta(player_id, outfile)

    def find_video(self, url, quality=0):
        raise download_npo.Error('Not implemented')

    def meta(self, player_id):
        raise download_npo.Error('Not implemented')

    def subs(self, player_id):
        raise download_npo.Error('Deze site ondersteund geen ondertitels')

    def list(self, url, fmt, page):
        raise download_npo.Error('Dit is niet ondersteund voor deze site')


class NPOPlayer(Site):
        """ Base class voor NPOPlayer sites, this should work on all sites using the
        NPO player """

        match = '.*'
        _playerid_regex = '([A-Z][A-Z_]{1,8}_\d{6,9})'

        def find_video(self, url, quality=0):
                """ Find video to download
                Returns (downloadurl, playerId, extension)"""

                if not (url.startswith('http://') or url.startswith('https://')):
                        url = 'http://www.npo.nl/%s' % url

                page = self.GetPage(url)
                page = unquote(page)

                if download_npo.Verbose() >= 3:
                        print('page: %s' % page)

                try:
                        playerId = re.search(self._playerid_regex, page).groups()[0]
                except AttributeError:
                        raise download_npo.DownloadNpoError('Kan playerId niet vinden')
                if download_npo.Verbose(): print('Using playerId ' + playerId)

                #{"token":"h4i536f2104v7aepeonjm83s51"}

                try:
                        token = json.loads(self.GetPage('http://ida.omroep.nl/app.php/auth'))['token']
                except AttributeError:
                        raise download_npo.DownloadNpoError('Kan token niet vinden')
                if download_npo.Verbose(): print('Found token ' + token)

                meta = self.meta(playerId)
                if meta.get('error') and len(meta['error']) > 1:
                        raise download_npo.DownloadNpoError(
                                'Site geeft aan dat er iets fout is: {}'.format(meta['error']))

                ext = 'mp4'
                if meta.get('items') and type(meta['items'][0][0]) == dict:
                        # Radiouitendingen
                        ext = meta['items'][0][0].get('type', 'mp4')

                        # MMS / Windows Media Speler
                        if meta['items'][0][0].get('formaat') == 'wmv':
                                return self.find_video_MMS(playerId)

                # http://ida.omroep.nl/app.php/POW_03414349?adaptive=no&token=djo0nv08rdk46iq7kijrvtktr3
                streams = self.GetJSON('http://ida.omroep.nl/app.php/{}?adaptive=no&token={}'.format(playerId, token))

                url = None
                errors = []
                for q, stream in enumerate(streams['items'][0][quality:]):
                        stream = self.GetJSON(stream['url'])
                        if stream.get('errorstring'):
                                # Dit is vooral voor regionale afleveringen (lijkt het ...)
                                if meta.get('items') and len(meta['items'][0]) > 0:
                                        url = meta['items'][0][0]['url']
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

                return (self.OpenUrl(url), playerId, ext)


        def find_video_MMS(self, playerId):
                """ Old MMS format """

                if download_npo.Verbose(): print('Gebruik find_video_MMS')

                meta = self.meta(playerId)
                stream = self.GetPage(meta['items'][0]['url'])
                stream = re.search(r'"(mms://.*?)"', stream).groups()[0]
                if download_npo.Verbose(): print('MMS stream: %s' % stream)

                #videourl, playerId, ext = site.find_video(v, quality)
                return (self.OpenMMS(stream), playerId, 'wmv')


        def meta(self, playerId):
                if self._meta.get(playerId) is None:
                        meta = self.GetJSON('http://e.omroep.nl/metadata/%s?callback=cd&version=5.1.0&_=%s' % (
                                playerId, time.time()))

                        # Hier lijkt zo vaak de helft van te ontbreken dat het niet opschiet
                        #if meta.get('serie') is not None:
                        #       meta['title'] = '%s %s' % (meta['serie']['serie_titel'], meta['aflevering_titel'])
                        #else:
                        meta['title'] = '%s' % meta.get('titel', '')
                        self._meta[playerId] = meta

                return self._meta[playerId]


        def subs(self, playerId):
                # Je zou verwachten dat je met het onderstaande uit de meta-data het
                # eea. over de ondertitels zou kunnen ophalen ... helaas werkt dat niet
                # zo, of misschien dat ik het niet goed doe... Voor nu gebruiken dus
                # hardcoded e.omroep.nl/tt888/, wat goed lijkt te werken.
                #self.Meta(playerId)
                #print('%s/%s/' % (meta['sitestat']['baseurl_subtitle'],
                #       meta['sitestat']['subtitleurl']))

                return self.OpenUrl('http://tt888.omroep.nl/tt888/%s' % playerId)


        def list(self, url, fmt, page):
                ''' 
                http://www.npo.nl/andere-tijden/VPWON_1247337/search?media_type=broadcast&start_date=&end_date=&start=8&rows=8
                '''

                if not url.startswith('http://'):
                        # Must be series ID; e.g. VPWON_1247337
                        if '_' in url:
                                url = 'http://www.npo.nl/ignored/{}'.format(url)
                if not url.endswith('/search'):
                        url += '/search'
                url += '?media_type=broadcast&rows=20&start={}'.format((page-1) * 20)
                p = self.GetPage(url)

                '''
                <div class='js-search-result list-item non-responsive row-fluid'
                data-crid='crid://npo.nl/WO_NTR_7087971'>
                <div class='span4'>
                <div class='image-container'>
                <a href="/truck-het-land-in-met-convoy-vara/23-01-2017/WO_NTR_7087971"><img
                alt="Afbeelding van Truck: het land in met Convoy, VARA" class="program-image"
                data-images="[&quot;//images.poms.omroep.nl/image/s174/c174x98/855819.png&quot;]"
                data-toggle="image-skimmer"
                src="//images.poms.omroep.nl/image/s174/c174x98/855819.png" />
                <div class="overlay-icon"><span class="npo-glyph camera"></span> 4:27</div>
                </a></div>
                </div>
                <div class='span8'>
                <a href="/truck-het-land-in-met-convoy-vara/23-01-2017/WO_NTR_7087971"><h4>
                Andere Tijden: 'Vrije jongens op de weg'
                <span class='inactive'>(NTR en VPRO)</span>
                <span class='av-icon'></span>
                </h4>
                '''

                matches = re.findall(r'data-crid=["\']crid://(.*?)["\'].*?<h4>(.*?)<\w+',
                        p, re.DOTALL | re.MULTILINE)

                for m in matches:
                        i = m[0].split('/').pop()
                        print('{} http://{} {}'.format(i, m[0], m[1].strip()))


class NPO(NPOPlayer):
    match = r'(www\.)?npo.nl'
    _playerid_regex = r'data-[mpr]{1,2}id="(.*?)"'


class OmroepBrabant(Site):
    match = r'(www\.)?omroepbrabant.nl'

    def find_video(self, url, quality=0):
        """ Find video to download
        Returns (downloadurl, pagetitle, player_id, extension)"""
        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://%s' % url

        page = self.get_page(url)
        try:
            jsurl = re.search(r'data-url="(.*?)"', page).groups()[0]
            player_id = re.search(r'sourceid_string:(\d+)', jsurl).groups()[0]
        except AttributeError:
            raise download_npo.Error('Kan player_id niet vinden')

        meta = self.meta(player_id)

        streams = meta['clipData']['assets']
        streams.sort(key=lambda v: int(v['bandwidth']), reverse=True)
        url = streams[0]['src']

        return self.openURL(url), meta['clipData'].get('title'), player_id, 'mp4'

    def meta(self, player_id):
        if self._meta.get(player_id) is None:
            page = self.get_page('http://media.omroepbrabant.nl/p/Commercieel1/q/sourceid_string:{}.js'.format(player_id))
            page = re.search('var opts = (.*);', page).groups()[0]

            data = json.loads(page)
            del data['playerCSS']
            del data['playerHTML']

            self._meta[player_id] = data

        return self._meta[player_id]


# The MIT License (MIT)
#
# Copyright © 2012-2017 Martin Tournoij
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
