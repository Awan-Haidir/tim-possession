"""Uji kecil dengan data buatan (bukan data lomba). Jalankan:  python tests/test_smooth.py"""
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from possession import smooth  # noqa: E402
from possession.writer import count_possessions  # noqa: E402


def test_majority_vote_removes_flicker():
    codes = np.array([0] * 20 + [1] + [0] * 20, dtype=np.int8)
    out = smooth.majority_vote(codes, 3)
    assert (out == 0).all()


def test_hysteresis_ignores_short_switch_and_backdates_real_one():
    # 100 frame tim 0; 10 frame tim 1 (terlalu singkat); 100 frame tim 0; lalu 100 frame tim 1 (nyata)
    codes = np.array([0] * 100 + [1] * 10 + [0] * 100 + [1] * 100, dtype=np.int8)
    dead = np.zeros(len(codes), dtype=bool)
    out = smooth.hysteresis(codes, dead, switch_frames=30)
    assert (out[:210] == 0).all()                    # kedipan 10 frame diabaikan
    assert (out[210:] == 1).all()                    # perpindahan nyata terjadi di frame 210, tidak terlambat


def test_dead_ball_clears_and_restarts():
    codes = np.array([0] * 50 + [1] * 50, dtype=np.int8)
    dead = np.zeros(100, dtype=bool)
    dead[40:60] = True
    labels = smooth.combine(smooth.hysteresis(codes, dead, 30), dead)
    assert (labels[40:60] == 2).all()
    assert labels[39] == 0 and labels[60] == 1       # setelah restart ikut tim pertama yang teramati


def test_merge_short_islands():
    labels = np.array([0] * 50 + [1] * 5 + [0] * 50, dtype=np.int8)
    out = smooth.merge_short_islands(labels, min_len=25)
    assert (out == 0).all()
    assert count_possessions(out) == 1


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_"):
            func()
            print("ok  ", name)
