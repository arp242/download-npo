ChangeLog
=========

Versie 2.9, 2017-09-28
----------------------
- Verwijder `download-gemist-list` weer. Ik heb zelf geen tijd/zin om dit steeds
  bij te houden, en blijkt toch vaak kapot te gaan. Als je je geroepen voelt:
  voel je vrij om een PR te openen met een fix :-)

Versie 2.8, 2017-07-04
----------------------
- Fix voor de huidige versie van de site. `download-gemist-list` werkt niet, dat
  fix ik later.

Versie 2.7.2, 2017-05-01
------------------------
- Gebruik de juiste extensie voor radiouitzendingen (en mogelijk andere
  uitzendingen).
- Betere detectie voor als ondertitels niet bestaan.

Versie 2.7.1, 2017-03-23
------------------------
- Fix voor radio uitzendingen; blijkbaar was hier het eea. veranderd op de site.

Versie 2.7, 2017-03-19
------------------------
- Voeg `download-npo-list` weer toe.
- Fix voor sommige oudere afleveringen.

Versie 2.6, 2017-03-02
----------------------
- Fix voor huidige versie van de site.
- Bugfix voor Python2 icm. `-f` flag en unicode.

Versie 2.5.2, 2017-02-01
------------------------
- Python 2.6 is **niet** meer ondersteund. Je hebt nu minimaal Python 2.7+ or
  3.3+ nodig.
- Fix `UnicodeEncodeError` met Python 2.
- Fix instructies voor Windows.
- Versie 2.5 en 2.5.1 overgeslagen door gedoe met PyPI.

Versie 2.4.2, 2017-01-31
------------------------
- Fix ook downloaden van ondertiteling voor de huidige versie van de site.

Versie 2.4.1, 2017-01-27
------------------------
- Fix voor de huidige versie van de site.

Versie 2.4, 2016-10-03
----------------------
- Fix voor radio-uitzendingen.
- De waarschuwing als metadata niet weggescheven kan worden omdat `mutagen`
  ontbreekt wordt nu alleen getoond als `-V` gebruikt wordt.
- Bugfix: utf-8 karakters in `-o` en `-f` voor Python 2 & niet-UTF-8 omgevingen.
- Versie 2.3 overgeslagen door gedoe met PyPI.

Versie 2.2, 2016-02-29
----------------------
- Schrijf metadata naar mp4 bestand als de `mutagen` module beschikbaar is.
- Installeer `.desktop` bestand en icoon, zodat het te zien is in
  Ubuntu/Unity/etc.
- Verschillende bugfixes.

Versie 2.1, 2015-09-18
----------------------
- De GUI (`download-gemist-gui`) is nu een heel stuk beter.
- Ondersteun config file in `~/.config/download-npo.conf` (zie `--help`).
- `--help` optie voor meer help (`-h` is nog steeds vrij kort).
- De `-o` en `-f` opties (voor de filename) accepteert nu ook een aantal
  placeholders om informatie uit de metadata op te nemen. Zie `download-npo
  --help` voor meer info.
- Fix `-f -` (output naar stdout) voor Python 3.
- Voeg `play-npo` toe, wrapper om video's direct af te spelen.
- Splits URLs van stdin op elke whitespace (en niet alleen op een spatie).
- De ondertiteling werd altijd gedownload, ook als `-n` opgegeven was (dank aan
  Jan Hoek voor het melden).

Versie 2.0.1, 2015-07-04
------------------------
- Fix voor de huidige versie van de site.

Versie 2.0, 2015-01-20
----------------------
- **Hernoem tool naar `download-npo`**; iemand anders heeft een soortgelijk
  programma gemaakt en dat dezelfde naam genoemd. In overleg is besloten mijn
  programma te hernoemen om verwarring te voorkomen.
- Implementeer Omroep Brabant.
- Werk ook zonder `http://` (ie. `download-npo npo.nl/...`
- Nieuwe optie: `-k` voor het selecteren van de kwaliteit.
- Fallback nu naar lagere kwaliteit streams, als `-k` niet opgegeven is en de
  hoogste kwaliteit niet beschikbaar is.

Versie 1.7, 2014-10-25
----------------------
- uitzendinggemist.nl is nu npo.nl, hernoem hier en daar dingen.
- Fix voor Python 2.6
- Fix voor lokale omroepen (omroep Brabant ed.)
- `-V` kan nu tot 3 keer opgegeven worden
- `-t` toevoegd om ook ondertitels mee te downloaden. Met `-T` worden alleen de
  ondertitels gedownload.
- `-m` om alleen de metadata te laten zien, in YAML formaat; `-M` voor JSON
  formaat.

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

