Download-gemist van download video's from the Dutch uitzending gemist site.

There are 2 tools:

### download-gemist
Can download a single episode from the episode URL.

Basic usage:
`download-gemist http://www.uitzendinggemist.nl/afleveringen/1292817`

See `download-gemist -h` for options.

### download-gemist-guide
This fetches information from a program page. You can use it download multiple
videos.

Note this doesn't actually download anything. Instead, it prints in the
episode ID, title, URL, date, and description (in this order) seperated by a
pipe (`|') character.

You can use standard UNIX tools. For example:

Basic usage:
  `download-gemist-guide http://www.uitzendinggemist.nl/programmas/215-andere-tijden | cut -d'|' -f3 | xargs | download-gemist

Downoad first two items:
  `download-gemist-guide http://www.uitzendinggemist.nl/programmas/215-andere-tijden | head -n 2 | cut -d'|' -f3 | xargs | download-gemist

Download all items except episode 1288776 and 1252447:
  `download-gemist-guide http://www.uitzendinggemist.nl/programmas/215-andere-tijden | grep -Ev '^12(88776|52447)' | cut -d'|' -f3 | xargs | download-gemist

See `download-gemist-guide -h` for options.
