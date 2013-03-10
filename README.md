Download-gemist downloads videos from the Dutch uitzending gemist site. The
rest of the documentation is in Dutch.


Download-gemist download videos van de [uitzending gemist][1] site van de
publieke omroep.

Installatie
===========
[Python][2] is nodig, het is getest met Python 2.7 en 3.3 op FreeBSD en
Windows 7.

Gebruik
=======
download-gemist komt met 3 programma's:

download-gemist
---------------
Commandline tool om een uitzending te downloaden.

Voorbeeld:

    download-gemist http://www.uitzendinggemist.nl/afleveringen/1292817

Zie `download-gemist -h` voor meer help en opties.

download-gemist-list
--------------------
Commandline tool om informatie op te halen van een programma pagina, dit kan
je gebruiken om makkelijk de laatst *n* videos te downloaden.

Dit download niks als zodanig, maar haalt alleen informatie op die je
vervolgens makkelijk aan `download-gemist` kan voeren.

Voorbeeld:

    download-gemist-list http://www.uitzendinggemist.nl/programmas/215-andere-tijden | cut -d'|' -f3 | xargs | download-gemist

Zie `download-gemist-list -h` voor meer opties.

download-gemist-gui
-------------------
Grafische frontend, hiervoor is Tkinter nodig (vaak standaard geïnstalleerd
met Python).


ChangeLog
=========
Versie 1.4, nog niet gereleased
-------------------------------
- Voeg grafische interface toe
- Hernoem `download-gemist-guide` naar `download-gemist-list`
- Fix `download-gemist-list` voor huidige versie van de site

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
