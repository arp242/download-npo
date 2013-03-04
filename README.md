Download-gemist downloads videos from the Dutch uitzending gemist site.
The rest of the documentation is in Dutch.


download-gemist download videos van de `download gemist' site van de publieke omroep.

[Python](http://python.org/) is nodig, het is getest met Python 2.7 en 3.3 op FreeBSD en Windows 7.

download-gemist komt met 2 commandline tools:

### download-gemist
Download een uitzending van een URL.

Normaal gebruik:
`download-gemist http://www.uitzendinggemist.nl/afleveringen/1292817`

Zie `download-gemist -h' voor meer help en opties.

### download-gemist-guide
Haal informatie op van een programma pagina, dit kan je gebruiken om makkelijk
de laatst /n/ videos te downloaden.

Dit download niks als zodanig, maar haalt alleen informatie op die je
vervolgens makkelijk an `download-gemist` kan voeren.

Een aantal voorbeelden voor UNIX en Linux systemen:

Standaard gebruik:
`download-gemist-guide http://www.uitzendinggemist.nl/programmas/215-andere-tijden | cut -d'|' -f3 | xargs | download-gemist`

Download eerste 2 uitzendingen:
`download-gemist-guide http://www.uitzendinggemist.nl/programmas/215-andere-tijden | head -n 2 | cut -d'|' -f3 | xargs | download-gemist`

Download alle uitzendingen muv. episodes 1288776 and 1252447:  
`download-gemist-guide http://www.uitzendinggemist.nl/programmas/215-andere-tijden | grep -Ev '^12(88776|52447)' | cut -d'|' -f3 | xargs | download-gemist`

Zie `download-gemist-guide -h` voor meer opties.
