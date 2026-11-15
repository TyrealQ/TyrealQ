# CLAUDE.md — TyrealQ (GitHub profile README)

This repo is the special `TyrealQ/TyrealQ` repository: GitHub shows its `README.md` at the top of the profile page at github.com/TyrealQ. Because `README.md` is the public profile itself, the working guide lives in `scripts/README.md` instead.

- `README.md` holds only the card (`<picture>` with `card-dark.svg` and `card-light.svg`) and the link row. The card's Contact block (`CONTACT` in `scripts/build_card.py`) lists only what the link row does not, so never repeat a link-row entry there.
- `card-dark.svg` and `card-light.svg` are generated. Edit `scripts/build_card.py`, never the SVGs.
- The daily workflow commits to `master` as `github-actions[bot]`; pull before editing locally.
- Commits and pushes go through `/q-skills:commit` and `/q-skills:ship`.

Files, commands, and update steps: @scripts/README.md
