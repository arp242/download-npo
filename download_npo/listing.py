#!/usr/bin/env python
# encoding:utf-8
#
# http://code.arp242.net/download-npo
#
# Copyright © 2012-2017 Martin Tournoij <martin@arp242.net>
# See below for full copyright
#

from __future__ import print_function
import getopt
import sys
import re
import download_npo


def usage(show_more_help=True):
    print('Experimenteel!')
    print('')
    print('Voorbeeld:')
    print('  ./download-npo-list http://www.npo.nl/andere-tijden/VPWON_1247337')
    print('')
    print('Gebruikt -p voor pagina 2, 3, etc.')
    print('')
    print('Format is:')
    print('ID URL omschrijving')
    print('')
    print('Let op! Sommige afleveringen komen meer dan een keer voor;'
          'vaak met een andere playerid.')
    print('Meestal is de omschrijving dan wel hetzelfde.')
    if show_more_help:
        print('Gebruik --help om een langere help te tonen')


def long_usage():
    usage(False)


def error(msg):
    """ Print message to stderr, can't use print because of Python 2/3
    incompatibility """
    sys.stderr.write(u'error: %s\n' % msg)


def main():
    try:
        params, series = getopt.getopt(sys.argv[1:], 'hvVsf:p:', ['help'])
    except getopt.GetoptError:
        error('error: %s' % sys.exc_info()[1])
        usage()
        sys.exit(1)

    options = download_npo.defaults()
    download_npo.verbose = int(options['verbose'])

    fmt = ''
    page = 1
    for flag, arg in params:
        if flag == '-h':
            usage()
            sys.exit(0)
        elif flag == '--help':
            long_usage()
            sys.exit(0)
        elif flag == '-v':
            print(download_npo.version())
            sys.exit(0)
        elif flag == '-V':
            download_npo.verbose += 1
        elif flag == '-s':
            options['silent'] = True
        elif flag == '-f':
            fmt = arg
        elif flag == '-p':
            page = int(arg)

    v = download_npo.check_update()
    if v is not None and not options['silent']:
        error('Waarschuwing: De laatste versie is %s, je gebruikt nu versie %s' % (
            v, download_npo.version()[0]))

    if len(series) == 0:
        sys.stderr.write('Lezen van stdin (gebruik -h voor help)...')
        sys.stderr.flush()

        try:
            series = re.split(r'\s', sys.stdin.read().strip())
        except KeyboardInterrupt:
            print('')
            sys.exit(0)
    try:
        for s in series:
            if s == '':
                continue
            download_npo.match_site(s).list(s, fmt, page)
    except download_npo.Error as exc:
        error(exc)
        sys.exit(1)
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
