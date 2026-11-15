# Profile card: working guide

The profile shows one SVG card: an ASCII portrait on the left and a terminal-style panel on the right. Two versions are built, one for each GitHub theme, and `README.md` picks between them with `prefers-color-scheme`. A scheduled workflow refreshes the GitHub numbers once a day.

## Files

| Path | Role |
|---|---|
| `art/cutout.png` | Website portrait (`tyrealq.github.io/images/Ty.png`) with the background removed |
| `art/portrait-dark.txt`, `art/portrait-light.txt` | ASCII portrait for each theme. On dark, bright areas use dense characters; on light, dark areas do |
| `scripts/cutout.swift` | Removes the photo background with the macOS Vision framework |
| `scripts/make_ascii.py` | Turns `cutout.png` into the two ASCII files (needs `opencv-python` and `numpy`) |
| `scripts/build_card.py` | Fetches GitHub stats and writes `card-dark.svg` and `card-light.svg` (standard library only) |
| `.github/workflows/update.yml` | Runs `build_card.py` daily at 06:17 UTC and on demand; commits only when a card changes |
| `preview/index.html` | Local preview that mimics the GitHub profile page, with a light/dark switch |
| `ruff.toml` | Lint settings for the scripts. The target is Python 3.9 because the local `python3` is 3.9; the workflow uses 3.12 |

## Commands

Run from the repo root.

```bash
# Rebuild the cards with live numbers
GITHUB_TOKEN=$(gh auth token) python3 scripts/build_card.py

# Preview at http://127.0.0.1:8765/preview/
python3 -m http.server 8765 --bind 127.0.0.1

# Lint the scripts
uvx ruff check scripts/

# Redo the portrait from a new photo (only when the photo changes)
swift scripts/cutout.swift /path/to/photo.png art/cutout.png
python3 scripts/make_ascii.py art/cutout.png art
```

## Editing

- **Panel text**: edit `PROFILE` and `CONTACT` at the top of `build_card.py`, then rebuild. The panel is 54 characters wide (`PANEL_COLS`) and values start at column 17 (`KEY_W` + 1), so a value longer than 37 characters runs past the edge.
- **Stats**: `stat_lines()` in `build_card.py` controls which numbers appear. Commits are summed across every year from `contributionYears`. The workflow uses the built-in Actions token, which sees public activity only, so its commit total can be lower than a local run with a personal token.
- **Colors**: `THEMES` in `build_card.py`. Keys use IU crimson (`#990000`) on light and a lighter red (`#ff7b72`) on dark.
- **Portrait**: the settings at the top of `make_ascii.py`. `CROP` frames the head in `cutout.png` pixels, `COLS` sets the detail, `BLACK` and `WHITE` set the brightness range taken from the skin tones, and `GAMMA` darkens mid-tones. If `COLS` changes, change `ART_SIZE` and `ART_LINE` in `build_card.py` by the same proportion so the portrait keeps its height.
- **Links under the card**: edit `README.md`.
