"""STASIUN 2: membersihkan data (dilakukan oleh program, tidak boleh dengan tangan)."""
import numpy as np


def to_metres(ball, players, length_m, width_m):
    """Koordinat 0-1 menjadi meter. Lapangan tidak persegi, jadi dua sumbu diskalakan berbeda."""
    scale = np.array([length_m, width_m])
    return ball * scale, players * scale


def fill_short_gaps(ball, max_gap):
    """Isi celah bola yang HILANG SINGKAT dengan garis lurus.

    Celah lebih panjang dari max_gap dibiarkan NaN (jangan mengarang, lihat deadball.py).
    Mengembalikan (bola_terisi, observed) ; observed = mask frame yang bolanya benar-benar terlihat.
    """
    filled = ball.copy()
    observed = ~np.isnan(ball[:, 0])
    seen = np.flatnonzero(observed)
    if len(seen) < 2:
        return filled, observed
    gaps = np.diff(seen) - 1
    for k in np.flatnonzero((gaps > 0) & (gaps <= max_gap)):
        a, b = seen[k], seen[k + 1]
        weight = (np.arange(a + 1, b) - a) / float(b - a)
        filled[a + 1:b] = ball[a] * (1 - weight)[:, None] + ball[b] * weight[:, None]
    return filled, observed
