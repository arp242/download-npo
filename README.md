**Download-gemist downloads videos from the Dutch uitzending gemist site. The
rest of the documentation is in Dutch.**


Download-gemist download videos van de [uitzending gemist][1] site van de
publieke omroep. In principe zouden alle sites die gebruik maken van de zogeten
“NPOPlayer” moeten werken, zoals bv. npo.nl, ncrv.nl, enz. (al zijn deze niet
allemaal getest).


Installatie
===========
- **[Windows installer][d-win]**
- **[Source][d-unix]**, voor BSD, Linux, UNIX, en OSX. [Python][2] is nodig
  (Python 2.7 & 3.3 zijn getest), voor de grafische interface is ook `Tkinter`
  nodig (deel van Python maar soms een aparte package).

Als je oudere Silverlight/Windows media player uitzendingen wilt downloaden heb
je [libmms][libmms] nodig. Dit werkt vooralsnog alleen op POSIX (ie.
niet-Windows) systemen.


Gebruik
=======
download-gemist is een commandline-tool, er is ook een grafische frontend
`download-gemist-gui`

Voorbeeld:  
`download-gemist http://www.uitzendinggemist.nl/afleveringen/1292817`

Zie `download-gemist -h` voor meer help en opties.


FAQ
===

Help! Het werkt niet! PANIEK!
-----------------------------
In het grootste deel van de gevallen komt dit omdat er iets kleins is
veranderd op de uitzending gemist site. Aangezien ik niet alle dagen videos
aan het downloaden ben kan het soms even duren voordat ik dit zie (& fix).
Stuur even een mail naar [martin@arp242.net][3] met de URL die je gebruik en de
volledige output van het commando (vaak is dit een kleine aanpassing van enkele
minuten).


Kan ik ook een video streamen zonder het eerst op te slaan?
-----------------------------------------------------------
Uiteraard!

`download-gemist -f - http://www.uitzendinggemist.nl/afleveringen/1330944 | mplayer -cache 4096 -cache-min 99 -`


ChangeLog
=========

Laatste source
--------------
- Fix voor lokale omroepen (omroep Brabant ed.)
- Je mag nu ook alleen het videonummer meegeven, (bv. de `1404271` in
  `http://www.uitzendinggemist.nl/afleveringen/1404271`)


Versie 1.6.3, 2014-02-18
------------------------
- Fixes in release, Windows-build van 1.6.2 was fubar


Versie 1.6.2, 2014-02-10
------------------------
- Fix voor huidige versie van de site
- Ondersteun ook oudere (MMS/ASF) uitzendingen


Versie 1.6.1, 2014-01-05
------------------------
- Bugfix: Uitzendingen die niet bij een serie horen gaven een error
- Iets betere errors in de GUI
- Aantal kleine verbeteringen


Versie 1.6, 2013-12-28
----------------------
- Geef waarschuwing als je een oudere versie gebruikt
- Werkt ook op andere sites met de NPOPlayer (npo.nl, ncrv.nl, etc.)
- Betere bestandsnamen
- Voeg grafische interface toe (`download-gemist-gui`)
- Windows installer
- `download-gemist-list` verwijderd; zo heel nuttig is het niet, en kost toch
  continue tijd om te onderhouden


Versie 1.5.1, 2013-10-09
------------------------
- Fix voor huidige versie van de site


Versie 1.5, 2013-10-06
----------------------
- `download-gemist-list` werkt nu ook bij `/weekarchief/` pagina’s
- Bugfix: Output bestand werd toch gemaakt bij `-n`
- Bugfix: `-p` bij `download-gemist-list` haalde altijd 1 pagina te veel op
- Bugfix: UnicodeError met python2 & `download-gemist-list`


Versie 1.4.2, 2013-10-01
------------------------
- Fix voor huidige versie van de site


Versie 1.4.1, 2013-09-23
------------------------
- Fix voor huidige versie van de site


Versie 1.4, 2013-08-22
----------------------
- Fix voor huidige versie van de site
- **Hernoem `download-gemist-guide` naar `download-gemist-list`**
- Gebruik nu overal Nederlands ipv. Engels of een mix van beide
- `download-gemist-list` leest nu ook van stdin
- `setup.py` script


Versie 1.3, 2013-03-05
----------------------
- Fix voor huidige versie van de site
- Betere voortgang-indicator


Versie 1.2, 2012-11-11
----------------------
- Voeg `download-gemist-guide` toe
- Voeg `-c` en `-w` opties toe
- Werkt nu ook met Python 3
- Fix voor huidige versie van de site


Versie 1.1, 2012-10-11
----------------------
- Geen `:` in bestandsnamen (problemen met FAT32)
- Fix voor huidige versie van de site


Versie 1.0, 2012-10-03
----------------------
- Eerste release



[1]: http://www.uitzendinggemist.nl/
[2]: http://python.org/
[3]: mailto:martin@arp242.net
[4]: http://www.publiekeomroep.nl/artikelen/algemene-voorwaarden-privacy
[5]: http://www.st-ab.nl/wetten/1107_Mediawet_2008.htm
[d-win]: https://bitbucket.org/Carpetsmoker/download-gemist/downloads/download-gemist-setup-1.6.3.exe
[d-unix]: https://bitbucket.org/Carpetsmoker/download-gemist/downloads/download-gemist-1.6.3.tar.gz
[libmms]: http://sourceforge.net/projects/libmms/
