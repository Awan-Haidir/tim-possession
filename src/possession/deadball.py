"""STASIUN 4a: menentukan frame bola mati (D).

Ini bagian yang paling banyak membutuhkan football analyst. Aturan di bawah adalah kerangka
awal; keputusan akhirnya harus tertulis di docs/possession_rules.md beserta alasannya.
"""
import numpy as np

from .util import true_runs


def detect(features, p, prekickoff_range=None, tagging=None):
    """Mengembalikan array bool: True = bola mati.

    Aturan saat ini:
      1. Bola hilang berturut-turut >= p.DEAD_IF_BALL_MISSING_FRAMES  ->  mati.
      2. (opsional) bola nyaris diam selama p.STILL_BALL_FRAMES        ->  mati.
      3. Frame antara awal babak 2 yang dinilai dan kick-off          ->  mati (FAQ.md).
    TODO (analyst): gunakan `tagging` (SET PIECES + tag Type) sebagai petunjuk akhir stoppage,
    dan tambahkan ciri bola keluar lapangan.
    """
    n = len(features["ball_present"])
    dead = np.zeros(n, dtype=bool)

    for start, end in true_runs(~features["ball_present"]):
        if end - start >= p.DEAD_IF_BALL_MISSING_FRAMES:
            dead[start:end] = True

    if p.USE_STILL_BALL_RULE:
        slow = features["ball_speed"] < p.STILL_BALL_SPEED_MS
        for start, end in true_runs(np.nan_to_num(slow, nan=False).astype(bool)):
            if end - start >= p.STILL_BALL_FRAMES:
                dead[start:end] = True

    if prekickoff_range is not None:
        lo, hi = prekickoff_range
        dead[lo:min(hi, n)] = True

    return dead
