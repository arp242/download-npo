# encoding:utf-8
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-2017 Martin Tournoij <martin@arp242.net>
# See below for full copyright

from __future__ import print_function

import inspect
import json
import os
import re
import sys
import textwrap
import time
import download_npo

# pylint:disable=import-error,no-name-in-module
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


def msg(t):
    f = inspect.stack()[1]
    print('download-npo {}:{} {}'.format(os.path.basename(f[1]), f[2], t))


class Site():
    # matched against the URL (w/o protocol)
    match = None

    # Meta info about this broadcast
    _meta = {}

    def __init__(self):
        if download_npo.verbose >= 2:
            if sys.version_info[0] >= 3:
                http.client.HTTPConnection.debuglevel = 99
            else:
                httplib.HTTPConnection.debuglevel = 99

    def urlopen(self, url):  # pylint:disable=no-self-use
        """ Open a URI; return urllib.request.Request object """
        if download_npo.verbose:
            msg('urlopen: ' + url)

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

    def open_mms(self, url):  # pylint:disable=no-self-use
        """ Open MMS URL """
        # import download_npo.mms
        return download_npo.mms.MMS(url)

    def get_page(self, url):
        """ Open URL, and read() the data """
        data = self.urlopen(url).read()
        if sys.version_info[0] > 2:
            data = data.decode()
        return data.strip()

    def get_json(self, url):
        """ Open URL, and read() the data, and parse it as JSON """
        data = re.sub(r'^[\w\d\?]+\(', r'', self.get_page(url))
        data = re.sub(r'[\);/eprc\s]*$', '', data)
        data = json.loads(data)

        if download_npo.verbose >= 2:
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

    def list(self, url, page):
        raise download_npo.Error('Dit is niet ondersteund voor deze site')


class NPOPlayer(Site):
    """ Base class voor NPOPlayer sites, this should work on all sites using the
    NPO player """

    match = '.*'
    _playerid_regex = r'([A-Z][A-Z_]{1,8}_\d{6,9})'
    base = 'http://ida.omroep.nl/app.php'

    def find_video(self, url, quality=0):
        """ Find video to download
            Returns (downloadurl, player_id, extension)"""

        if not (url.startswith('http://') or url.startswith('https://')):
            url = 'http://www.npo.nl/{}'.format(url)

        page = self.get_page(url)
        page = unquote(page)

        if download_npo.verbose >= 3:
            msg('page: {}'.format(page))

        try:
            player_id = re.search(self._playerid_regex, page).groups()[0]
        except AttributeError:
            raise download_npo.Error('Kan player_id niet vinden')
        if download_npo.verbose:
            msg('Using player_id {}'.format(player_id))

        # {"token":"h4i536f2104v7aepeonjm83s51"}
        try:
            token = json.loads(self.get_page('{}/auth'.format(self.base)))['token']
        except AttributeError:
            raise download_npo.Error('Kan token niet vinden')
        if download_npo.verbose:
            msg('Found token ' + token)

        meta = self.meta(player_id)
        if meta.get('error') and len(meta['error']) > 1:
            raise download_npo.Error(
                'Site geeft aan dat er iets fout is: {}'.format(meta['error']))

        ext = 'mp4'
        if meta.get('items') and isinstance(meta['items'][0][0], dict):
            # Radiouitendingen
            ext = meta['items'][0][0].get('type', 'mp4')

            # MMS / Windows Media Speler
            if meta['items'][0][0].get('formaat') == 'wmv':
                return self.find_video_MMS(player_id)

        # http://ida.omroep.nl/app.php/POW_03414349?adaptive=no&token=djo0nv08rdk46iq7kijrvtktr3
        streams = self.get_json('{}/{}?adaptive=no&token={}'.format(
            self.base, player_id, token))

        url = None
        errors = set()
        for q, stream in enumerate(streams['items'][0][quality:]):
            # Oudere afleveringen; zie #10
            if stream.get('contentType') == 'url':
                url = stream['url']
                break
            else:
                stream = self.get_json(stream['url'])
                if stream.get('errorstring'):
                    # Dit is vooral voor regionale afleveringen (lijkt het ...)
                    if meta.get('items') and len(meta['items'][0]) > 0:
                        url = meta['items'][0][0]['url']
                        break
                    else:
                        errors.add(stream.get('errorstring'))
                else:
                    url = stream['url']
                    break

        if url is None:
            raise download_npo.Error("Foutmelding van site:\n{}".format(
                '\n'.join(['\n'.join(textwrap.wrap(e)) for e in errors])))

        return (self.urlopen(url), player_id, ext)

    def find_video_MMS(self, player_id):
        """ Old MMS format """

        if download_npo.verbose:
            msg('Gebruik find_video_MMS')

        meta = self.meta(player_id)
        stream = self.get_page(meta['items'][0]['url'])
        stream = re.search(r'"(mms://.*?)"', stream).groups()[0]
        if download_npo.verbose:
            msg('MMS stream: %s' % stream)

        # videourl, player_id, ext = site.find_video(v, quality)
        return (self.open_mms(stream), player_id, 'wmv')

    def meta(self, player_id):
        if self._meta.get(player_id) is None:
            meta = self.get_json(
                'http://e.omroep.nl/metadata/{}?callback=cd&version=5.1.0&_={}'.format(
                    player_id, time.time()))

            #  Hier lijkt zo vaak de helft van te ontbreken dat het niet opschiet
            # if meta.get('serie') is not None:
            #     meta['title'] = '{} {}'.format(
            #         meta['serie']['serie_titel'],
            #         meta['aflevering_titel'])
            # else:
            meta['title'] = '%s' % meta.get('titel', '')
            self._meta[player_id] = meta

        return self._meta[player_id]

    def subs(self, player_id):
        # Je zou verwachten dat je met het onderstaande uit de meta-data het
        # eea. over de ondertitels zou kunnen ophalen ... helaas werkt dat niet
        # zo, of misschien dat ik het niet goed doe... Voor nu gebruiken dus
        # hardcoded e.omroep.nl/tt888/, wat goed lijkt te werken.
        # self.meta(player_id)
        # print('%s/%s/' % (meta['sitestat']['baseurl_subtitle'],
        #       meta['sitestat']['subtitleurl']))

        return self.urlopen('http://tt888.omroep.nl/tt888/{}'.format(player_id))

    def list(self, url, page):
        """ List all episodes for a series.
        http://www.npo.nl/andere-tijden/VPWON_1247337/search?media_type=broadcast&start_date=&end_date=&start=8&rows=8
        """

        if not url.startswith('http://'):
            # Must be series ID; e.g. VPWON_1247337
            if '_' in url:
                url = 'http://www.npo.nl/ignored/{}'.format(url)
        if not url.endswith('/search'):
            url += '/search'
        url += '?media_type=broadcast&rows=20&start={}'.format((page - 1) * 20)
        p = self.get_page(url)

        matches = re.findall(r'data-crid=["\']crid://(.*?)["\'].*?<h4>(.*?)<\w+',
                             p, re.DOTALL | re.MULTILINE)

        ret = []
        for m in matches:
            i = m[0].split('/').pop()
            ret.append((i, 'http://{}'.format(i, m[0]), m[1].strip()))
        return ret


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

        return self.urlopen(url), meta['clipData'].get('title'), player_id, 'mp4'

    def meta(self, player_id):
        if self._meta.get(player_id) is None:
            page = self.get_page(
                'http://media.omroepbrabant.nl/p/Commercieel1/q/sourceid_string:{}.js'.format(
                    player_id))
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
