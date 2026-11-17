"""Perubahan v2 mana yang menggeser hasil? Matikan satu per satu dan bandingkan. TANPA ground truth.

    python scripts/ablation.py --data-dir data

Baris "semua saklar mati" harus sama dengan hasil v1 Anda (possession dan rata-rata detik).
Tujuannya memahami penyebab perubahan, bukan mencari skor terbaik.
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


ALL_OFF = dict(USE_CORROBORATION=False, USE_SMART_TAGGING=False, USE_RESTART_TEAM_HINT=False,
               USE_CONTROL_GATE=False, MIN_SPELL_FRAMES=25, MIN_DEAD_FRAMES=0)

SCENARIOS = [
    ("v2 penuh (default)", {}),
    ("tanpa gerbang kontrol", dict(USE_CONTROL_GATE=False)),
    ("tanpa petunjuk tim restart", dict(USE_RESTART_TEAM_HINT=False)),
    ("tanpa Smart Tagging", dict(USE_SMART_TAGGING=False, USE_RESTART_TEAM_HINT=False)),
    ("tanpa penguat bola hilang", dict(USE_CORROBORATION=False)),
    ("MIN_SPELL_FRAMES = 25", dict(MIN_SPELL_FRAMES=25)),
    ("semua saklar mati (= v1)", ALL_OFF),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default=os.environ.get("MTAH_DATA_DIR") or os.path.join(ROOT, "data"))
    args = parser.parse_args()

    base = with_params()
    prep = pipeline.prepare(args.data_dir, base)
    graded = np.zeros(prep["n_frames"], dtype=bool)
    for first, last in base.GRADED_BLOCKS:
        graded[first:last + 1] = True

    print("{:<30}{:>11}{:>9}{:>7}{:>7}{:>7}{:>7}".format(
        "skenario", "possession", "rata2(s)", "H%", "A%", "D%", "X%"))
    for name, changes in SCENARIOS:
        p = with_params(**changes)
        codes = pipeline.label(prep, p)
        spells = writer.count_possessions(codes)
        alive = int(np.sum((codes == 0) | (codes == 1)))
        mean = alive / p.FPS / spells if spells else 0.0
        shares = [100.0 * np.mean(codes[graded] == v) for v in range(4)]
        print("{:<30}{:>11}{:>9.1f}{:>7.1f}{:>7.1f}{:>7.1f}{:>7.1f}".format(name, spells, mean, *shares))
    print("\nPersentase dihitung dari frame yang dinilai saja.")


if __name__ == "__main__":
    main()