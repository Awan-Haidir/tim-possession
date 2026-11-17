"""Seberapa tahan hasil terhadap parameter gerbang kontrol dan bola mati? TANPA ground truth.

    python scripts/sweep.py --data-dir data

Tiga tabel. Cari daerah di mana angka berubah pelan (stabil); hindari tepi yang berubah tajam.
Jangan memilih sel yang "kebetulan terbaik", dan jangan mencocokkan dengan statistik ground truth publik.
Sel berisi: jumlah possession / persen D.
"""
import argparse
import os
import sys
import types

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from configs import params  # noqa: E402
from possession import pipeline, writer  # noqa: E402


def with_params(**changes):
    p = types.SimpleNamespace(**{k: v for k, v in vars(params).items() if k.isupper()})
    for key, value in changes.items():
        setattr(p, key, value)
    return p


def table(prep, graded, title, row_name, rows, col_name, cols):
    print("\n{}".format(title))
    print("{:>26}".format("{} \\ {}".format(row_name, col_name)) + "".join("{:>14}".format(c) for c in cols))
    for r in rows:
        line = "{:>26}".format(r)
        for c in cols:
            p = with_params(**{row_name: r, col_name: c})
            codes = pipeline.label(prep, p)
            line += "{:>14}".format("{} / {:.1f}%".format(
                writer.count_possessions(codes), 100.0 * np.mean(codes[graded] == 2)))
        print(line)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default=os.environ.get("MTAH_DATA_DIR") or os.path.join(ROOT, "data"))
    args = parser.parse_args()

    base = with_params()
    prep = pipeline.prepare(args.data_dir, base)
    graded = np.zeros(prep["n_frames"], dtype=bool)
    for first, last in base.GRADED_BLOCKS:
        graded[first:last + 1] = True

    table(prep, graded, "1. Gerbang kontrol (default 3.0 dan 0.5)",
          "CONTROL_RADIUS_M", (2.0, 3.0, 4.0, 5.0), "CONTEST_MARGIN_M", (0.25, 0.5, 1.0))
    table(prep, graded, "2. Bola hilang dianggap mati (default 0.5 dan 75)",
          "DEAD_SLOW_FRACTION", (0.3, 0.5, 0.7), "DEAD_IF_BALL_MISSING_FRAMES", (50, 75, 125, 200))
    table(prep, graded, "3. Mundur dari restart (default 500) dan jumlah D minimum (default 25)",
          "DEAD_LOOKBACK_FRAMES", (250, 375, 500, 750), "MIN_DEAD_FRAMES", (0, 25, 50))


if __name__ == "__main__":
    main()