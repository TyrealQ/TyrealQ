import sys
from pathlib import Path

import cv2
import numpy as np

RAMP = np.array(list(" .,:;irsXA253hMHGS#9B&@"))
COLS = 130
CELL_ASPECT = 0.6 * 4.4 / 5.1
CROP = (250, 140, 880, 1000)
BLACK, WHITE = 100, 225
GAMMA = 1.5
SHARPEN = 1.2


def prepare(path):
    im = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
    x0, y0, x1, y1 = CROP
    im = im[y0:y1, x0:x1]
    gray = cv2.cvtColor(im[:, :, :3], cv2.COLOR_BGR2GRAY).astype(float)
    blur = cv2.GaussianBlur(gray, (0, 0), gray.shape[1] / COLS * 1.5)
    gray = gray + SHARPEN * (gray - blur)
    tone = np.clip((gray - BLACK) / (WHITE - BLACK), 0, 1) ** GAMMA
    rows = int(COLS * gray.shape[0] / gray.shape[1] * CELL_ASPECT)
    size = (COLS, rows)
    tone = cv2.resize(tone, size, interpolation=cv2.INTER_AREA)
    alpha = cv2.resize(im[:, :, 3], size, interpolation=cv2.INTER_AREA)
    return tone, alpha


def render(tone, alpha, invert):
    ink = tone if invert else 1 - tone
    idx = 1 + np.rint(ink * (len(RAMP) - 2)).astype(int)
    chars = np.where(alpha < 110, " ", RAMP[idx])
    lines = ["".join(r).rstrip() for r in chars]
    while lines and not lines[0]:
        lines.pop(0)
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    tone, alpha = prepare(src)
    (out / "portrait-dark.txt").write_text(render(tone, alpha, invert=True))
    (out / "portrait-light.txt").write_text(render(tone, alpha, invert=False))
