Download-gemist downloads videos from the Dutch uitzending gemist site. The
rest of the documentation is in Dutch.


Download-gemist download videos van de [uitzending gemist][1] site van de
publieke omroep.

Installatie
===========
Voor Windows kun is [de installer][d-win] het makkelijkst.

Voor UNIX en Linux kan je [de source][d-unix] downloaden, [Python][2] is
nodig, voor de grafische interface is ook Tkinter nodig (deel van Python maar
soms een aparte package).

Gebruik
=======
download-gemist komt met 3 programma’s:

download-gemist
---------------
Commandline tool om een uitzending te downloaden.

Voorbeeld:  
`download-gemist http://www.uitzendinggemist.nl/afleveringen/1292817`

Zie `download-gemist -h` voor meer help en opties.

download-gemist-list
--------------------
Commandline tool om informatie op te halen van een programma pagina, dit kan
je gebruiken om makkelijk de laatst *n* videos te downloaden.

Dit download niks als zodanig, maar haalt alleen informatie op die je
vervolgens makkelijk aan `download-gemist` kan voeren.

Voorbeeld:  
`download-gemist-list http://www.uitzendinggemist.nl/programmas/215-andere-tijden | cut -d'|' -f3 | xargs | download-gemist`

Zie `download-gemist-list -h` voor meer opties.

download-gemist-gui
-------------------
Grafische frontend, hiervoor is Tkinter nodig (vaak standaard geïnstalleerd
met Python).

FAQ
===

Help! Het werkt niet!
---------------------
In het grootste deel van de gevallen komt dit omdat er iets kleins is
veranderd op de uitzending gemist site. Aangezien ik niet alle dagen videos
aan het downloaden ben kan het soms even duren voordat ik dit zie (en oplos).
Stuur even een mail naar [martin@arp242.net][3], vaak is dit een kleine
aanpassing van 2 minuten.

Kan ik ook een video streamen zonder het eerst op te slaan?
-----------------------------------------------------------
Uiteraard!

`download-gemist -f - http://www.uitzendinggemist.nl/afleveringen/1330944 | mplayer -cache 4096 -cache-min 99 -`

Is dit legaal?
--------------
Volgens de [algemene voorwaarden][4] van uitzending gemist:

> De Content mag uitsluitend door middel van normaal browserbezoek worden
> geraadpleegd via de pagina’s van de publieke omroepwebsites, de
> Omroepplayers of andere door de publieke omroep aangeboden diensten. Het is
> niet toegestaan de Content op geautomatiseerde wijze te (laten) raadplegen
> en/of analyseren bijvoorbeeld via scripts, spiders en of bots.

Echter, volgens de [mediawet van 2008][5] (paragraaf 2.1):

> 2. 2. Publieke mediadiensten voldoen aan democratische, sociale en culturele
>    behoeften van de Nederlandse samenleving door het aanbieden van
>    media-aanbod dat:
>
>    [...]
>
>    f. voor iedereen toegankelijk is.
>
> 3. Het programma-aanbod van de algemene programmakanalen van de landelijke,
> 	 regionale en lokale publieke mediadiensten wordt via omroepzenders
> 	 verspreid naar alle huishoudens in het verzorgingsgebied waarvoor de
> 	 programma’s zijn bestemd zonder dat zij voor de ontvangst andere kosten
> 	 moeten betalen dan de kosten van aanschaf en gebruik van technische
> 	 voorzieningen die de ontvangst mogelijk maken.

Aangezien het technisch niets uitmaakt of de plugins gedownload worden met dit
scriptje of een browser (ze kunnen bij uitzending gemist nergens het verschil
aan merken), en er ook geen advertenties zijn (en dus geen omzetverlies),
lijkt het erop dat deze paragraaf uit de algemene voorwaarden niet helemaal in
lijn met de mediawet is.


ChangeLog
=========
Versie 1.4, nog niet gereleased
-------------------------------
- Voeg grafische interface toe (`download-gemist-gui`)
- **Hernoem `download-gemist-guide` naar `download-gemist-list`**
- `setup.py` script, Windows installer
- Gebruik nu overal Nederlands ipv. Engels of een mix van beide
- Fix `download-gemist-list` voor huidige versie van de site
- `download-gemist-list` leest nu ook van stdin

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
[d-win]: https://bitbucket.org/Carpetsmoker/download-gemist/downloads
[d-unix]: https://bitbucket.org/Carpetsmoker/download-gemist/downloads
