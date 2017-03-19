#!/usr/bin/env python
# encoding:utf-8
#
# Download videos from the Dutch `Uitzending gemist' site.
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-2017 Martin Tournoij <martin@arp242.net>
# See below for full copyright
#

from __future__ import print_function
import getopt
import os
import re
import signal
import subprocess
import sys
import time
import download_npo


_options = {}


def usage(show_more_help=True):
    print('{} [-hvdnVsofwcmMtTk] [-o output_dir] [-f output_file] [url url2 ...]'.format(
        sys.argv[0]))
    print('')
    print('Video URL kan vanaf de commandline opgegeven worden, of via stdin')
    print('')
    print('  -h  Toon korte help; gebruik --help voor een langere help')
    print('  -v  Toon versie')
    print('  -d  Schrijf een config bestand met de standaard waarden')
    print("  -n  Download niks, laat zien wat we zouden doen")
    print('  -V  Toon meer informatie over wat we doen; gebruik 2 of 3 keer voor meer info')
    print('  -s  Stil: geef geen informatieve berichten (alleen errors)')
    print('  -o  Zet output directory. Default is huidige directory')
    print('  -f  Bestandsnaam, relatief aan -o; default is titel {titel}-{episode_id}')
    print('      Gebruik - voor stdout')
    print('  -w  Overschrijf bestaande bestanden (default is om bestand over te slaan')
    print('      als deze al bestaat)')
    print('  -c  Verwijder geen karakters in de bestandsnaam muv. spaties')
    print('        - Als je -c 2x opgeeft, worden spaties ook behouden')
    print('        - De default is om alle ongeldige FAT32/NTFS karakters te')
    print('          verwijderen en spaties te vervangen door underscores')
    print('  -m  Toon enkel de metadata in YAML formaat')
    print('  -M  Toon enkel de metadata in JSON formaat')
    print('  -t  Download ook ondertiteling, als deze bestaat')
    print('  -T  Download alleen ondertiteling, geef een error als deze niet bestaan')
    print('  -k  Selecteer de kwaliteit; hoog (default), middel of laag')
    print('')

    if show_more_help:
        print('Gebruik --help om een langere help te tonen')


def long_usage():
    usage(False)
    print('De -o en -f opties kunnen een aantal variabelen bevatten. Deze worden er met')
    print('de Python .format() methode ingezet.')
    print('Als een variabele niet bestaan in de data die npo.nl ons geeft, dan wordt dit')
    print("stil genegeerd. Let op dat er relatief veel video's lijken te zijn met meta-data")
    print("die incompleet is (met name de wat oudere video's). Ook het formaat/inhoud van")
    print('de data is niet altijd consequent. Alleen de aanwezigheid van {episode_id} is')
    print('gegarandeerd, dus ik zou deze er altijd bij zetten om lege bestandsnamen zoals')
    print("'.mp4' te voorkomen.")
    print('')
    print('  {episode_id}        Uniek nummer voor deze uitzending')
    print('  {datum}             Datum van uitzending')
    print('  {titel}             Titel; vaak is dit de serietitel')
    print('  {aflevering_titel}  Titel van de aflevering')
    print('  {tijdsduur}         Tijdsduur')
    print('  {serie_id}          Uniek nummer voor deze serie')
    print('  {serie_titel}       Titel van de serie; vaak is dit hetzelfde als de {titel}')
    print('')
    print('Je kan eventueel ook defaults opslaan in de een config bestand, dit wordt gelezen')
    print('uit {}.'.format(download_npo.config_path()))
    print('Met -d wordt er een config bestand geschreven met de standaard waarden.')
    print('Zie de comments in het bestand voor meer details.')


def error(msg):
    """ Print message to stderr, can't use print because of Python 2/3
    incompatibility """
    sys.stderr.write(u'error: {}\n'.format(msg))


def term_width():
    """ Try and get the terminal width """

    # Python 3.3 and newer
    if getattr(os, 'get_terminal_size', None) is not None:
        try:
            return os.get_terminal_size().columns
        except OSError:
            pass

    # No reliable/easy way on Windows in 3.2 and older
    if sys.platform == 'win32':
        return 80

    try:
        proc = subprocess.Popen(['tput cols'], shell=True, stdout=subprocess.PIPE)
        out = proc.communicate()
        if proc.wait() != 0:
            raise OSError
        return int(out[0])
    except OSError:
        return 80


termwidth = termwidthchanged = None


def download_video(site, player_id, videourl, outfile):
    global termwidth, termwidthchanged
    termwidth = term_width()
    termwidthchanged = False

    # Update on terminal resize, if the OS supports it
    if getattr(signal, 'SIGWINCH', None):
        def updterm(_sig, _stack):
            global termwidth, termwidthchanged
            termwidth = term_width()
            termwidthchanged = True
        signal.signal(signal.SIGWINCH, updterm)

    filename = os.path.basename(outfile)
    starttime = time.time()
    ptime = remaining = 0
    dl = site.download_video(player_id, videourl, outfile, _options['dryrun'])
    for total, completed, speed in dl:
        curtime = time.time()
        if curtime - starttime > 2:
            speed = int(completed / (curtime - starttime))
            if speed == 0:
                remaining = 0
            else:
                remaining = (total - completed) / speed

        if curtime >= ptime + 1:
            if total < 0:
                line = '  {completed} van onbekende groote met {speed:>4}/s    '.format(
                    completed=download_npo.human_size(completed),
                    speed=download_npo.human_size(speed))
            else:
                line = '{complete:>3}% van {total}; nog {remaining:>4} te gaan met {speed:>4}/s    '
                line = line.format(
                    total=download_npo.human_size(total),
                    complete=int(completed / (total / 100)),
                    speed=download_npo.human_size(speed),
                    remaining=download_npo.human_time(remaining))

            if termwidthchanged:
                termwidthchanged = False
                print('')

            if len(filename) + len(line) > termwidth:
                title = filename[:termwidth - len(line) - 2] + u'..'
            else:
                title = filename
            sys.stdout.write('\r%s%s' % (title, line))
            sys.stdout.flush()
            ptime = curtime

    if _options['dryrun']:
        print(outfile)
    else:
        print()


def download(download_videos, filename, outdir, metaonly, getsubs, quality):
    exitcode = 0
    for vid in download_videos:
        if vid == '':
            continue
        if download_npo.verbose:
            print('Downloading ' + vid)

        try:
            site = download_npo.match_site(vid)
            videourl, player_id, ext = site.find_video(vid, quality)

            if not metaonly:
                outdir = download_npo.make_outdir(outdir, site.meta(player_id))
                outfile = download_npo.make_filename(outdir, filename, ext,
                                                     site.meta(player_id),
                                                     _options['safefilename'],
                                                     _options['replacespace'],
                                                     _options['overwrite'])
                if download_npo.verbose:
                    print('Saving to %s' % outfile)

            if getsubs > 0:
                subout = download_npo.make_filename(outdir, filename, 'srt',
                                                    site.meta(player_id),
                                                    _options['safefilename'],
                                                    _options['replacespace'],
                                                    _options['overwrite'])
                if download_npo.verbose:
                    print('Saving subs to %s' % subout)
        except download_npo.Error as exc:
            error(exc)
            exitcode = 1
            continue

        if metaonly == 1:
            try:
                import yaml
            except ImportError:
                print('error: yaml extensie niet gevonden')
                print('Om de metadata als YAML te tonen is de YAML extensie nodig:')
                print('http://pyyaml.org/')
                print('Je kan eventueel ook -M gebruiken om de metadata als JSON te tonen')
                sys.exit(1)
            print(yaml.dump(site.meta(player_id)))
        elif metaonly == 2:
            import json
            print(json.dumps(site.meta(player_id), indent=True))
        elif getsubs == 2:
            if _options['dryrun']:
                print(subout)
            else:
                with open(subout, 'wb') as fp:
                    fp.write(site.subs(player_id).read())
        else:
            if getsubs == 1:
                if _options['dryrun']:
                    print(subout)
                else:
                    with open(subout, 'wb') as fp:
                        fp.write(site.subs(player_id).read())

            if not _options['silent']:
                download_video(site, player_id, videourl, outfile)
            else:
                for _ in site.download_video(player_id, videourl, outfile):
                    pass

    sys.exit(exitcode)


def main():
    global _options

    try:
        params, videos = getopt.getopt(sys.argv[1:], 'hvVsnwcmMtTo:f:k:d', ['help'])
    except getopt.GetoptError:
        error('error: {}'.format(sys.exc_info()[1]))
        usage()
        sys.exit(1)

    options = download_npo.defaults()
    download_npo.verbose = int(options['verbose'])

    for flag, arg in params:
        if flag == '-h':
            usage()
            sys.exit(0)
        elif flag == '--help':
            long_usage()
            sys.exit(0)
        elif flag == '-d':
            download_npo.write_defaults()
            sys.exit(0)
        elif flag == '-v':
            print('download-npo ' + ', '.join(download_npo.version()))
            print('http://code.arp242.net/download-npo')
            sys.exit(0)
        elif flag == '-V':
            download_npo.verbose += 1
        elif flag == '-s':
            options['silent'] = True
        elif flag == '-o':
            options['outdir'] = arg
        elif flag == '-f':
            options['filename'] = arg
        elif flag == '-n':
            options['dryrun'] = True
        elif flag == '-w':
            options['overwrite'] = True
        elif flag == '-c' and not options['safefilename']:
            options['replacespace'] = False
        elif flag == '-c':
            options['safefilename'] = False
        elif flag == '-m':
            options['metaonly'] = 1
        elif flag == '-M':
            options['metaonly'] = 2
        elif flag == '-t':
            options['getsubs'] = 1
        elif flag == '-T':
            options['getsubs'] = 2
        elif flag == '-k':
            try:
                options['quality'] = ['hoog', 'middel', 'laag'].index(arg)
            except ValueError:
                error("Ongeldige optie voor -k: `{}'.".format(arg))
                error("Geldige opties: `hoog', `middel', `laag'")
                sys.exit(1)

    if not options['metaonly'] and options['filename'] == '-':
        options['silent'] = True

    _options = options
    v = download_npo.check_update()
    if v is not None and not options['silent']:
        error('Waarschuwing: De laatste versie is %s, je gebruikt nu versie %s' % (
            v, download_npo.version()[0]))

    if len(videos) == 0:
        sys.stderr.write('Lezen van stdin (gebruik -h voor help)...')
        sys.stderr.flush()

        try:
            videos = re.split(r'\s', sys.stdin.read().strip())
        except KeyboardInterrupt:
            print('')
            sys.exit(0)

    try:
        download(videos, options['filename'], options['outdir'],
                 options['metaonly'], options['getsubs'], options['quality'])
    except KeyboardInterrupt:
        print('')


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
