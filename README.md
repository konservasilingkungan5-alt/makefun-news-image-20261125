[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/konservasilingkungan5-alt/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/konservasilingkungan5-alt/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# The World Today — Wednesday 25 November 2026

A one-page newspaper front page summing up the world's news of
Wednesday 25 November 2026: 32 stories from 5 regions, drawn by a
program written from scratch in this repository.

Bounty: [Sum up 25 November's world news in one image](https://make.fun/bounty/news-image-20261125) ($100, 50 places paid; closes Friday 27 November 2026, 07:00 WIB).

## What the image shows

- **Masthead and date** — THE WORLD TODAY, Wednesday 25 November 2026.
- **Numbers strip** — 30 killed in the Cairo fuel fire; 19 killed
  in RSF drone attacks in Sudan; 490,334 Russian soldiers dead
  since 2022 (leaked data); 14 economies face proposed US
  tariffs; 115 billion euros, Ukraine's financing need for 2027;
  Bangladesh garment wage up 36%.
- **The leads** — US proposes tariffs on 14 economies; Houthis
  claim an attack on the Ras Tanura refinery; judges recommend
  dropping the Netanyahu bribery case.
- **World map** — a schematic map with the places in the day's news
  marked: Warsaw, London, Kyiv, Odesa, Cairo, Riyadh, Aden, Gaza,
  Baghdad, Damazin, Jakarta and Dhaka.
- **The day in brief** — 16 stories, from the Poland no-fly zone
  and the Cairo fire to the Cartagena rescue, the Bangladesh wage
  rise and the Ukraine financing need.
- **Also on Wednesday** — 13 more stories, including the leaked
  Russian death toll, the Iraq court ruling and the FAA
  ground-stop probe.
- **Date check footer** — the Benghazi strike was on 24 November
  and the two Libyan soldiers' deaths were reported on
  25 November; the Houthi advance on Aden was first reported at
  00:00 UTC on 25 November.

## How it is made

`main.py` is a single self-contained Python 3.13 program using only
the standard library. It draws everything itself — its own 5x7
bitmap font, its own canvas and shapes, and its own PNG encoder —
and writes a 1024x1024 PNG. It uses no network, no clock and no
randomness, so every run writes the same bytes.

## Run it

```sh
python3 main.py /output/entry.png
```

Run it twice and compare: the two files are byte-identical.

## Sources

All 32 stories were first reported on Wednesday 25 November 2026.
See [SOURCES.md](SOURCES.md) for the story-by-story list with
source URLs and dates.

## Licence

MIT — see [LICENSE](LICENSE).
