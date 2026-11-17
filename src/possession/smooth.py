"""STASIUN 5: menghilangkan kedipan. Perbaikan terbesar menurut baseline (spellF1 0,05 -> 0,24).

Satu possession bukan 25 keputusan per detik, melainkan satu rentetan panjang.
"""
import numpy as np

from .util import run_bounds


def majority_vote(codes, window, home=0, away=1, nobody=-1):
    """Suara terbanyak pada jendela terpusat +/- window frame. nobody jika tidak ada suara."""
    codes = np.asarray(codes)
    if window <= 0:
        return codes.copy()
    cum_home = np.concatenate(([0], np.cumsum(codes == home)))
    cum_away = np.concatenate(([0], np.cumsum(codes == away)))
    index = np.arange(len(codes))
    lo = np.maximum(0, index - window)
    hi = np.minimum(len(codes), index + window + 1)
    h = cum_home[hi] - cum_home[lo]
    a = cum_away[hi] - cum_away[lo]
    out = np.full(len(codes), nobody, dtype=np.int8)
    seen = (h + a) > 0
    out[seen] = np.where(h[seen] >= a[seen], home, away)
    return out


def hysteresis(team_codes, dead, switch_frames, nobody=-1, restart_hint=None):
    """Possession pindah hanya jika tim lain terus terdekat selama switch_frames frame.

    Dengan penanggalan mundur (back-dating): setelah pindah terkonfirmasi, titik pindah
    dimundurkan ke frame pertama bukti baru, jadi tidak terlambat (keterlambatan 1 detik
    merugikan spellF1 secara nyata). Bola mati mengosongkan pemegang; setelah restart,
    tim pertama yang teramati menjadi pemegang.
    restart_hint (opsional): array tim per frame, bernilai tim hanya di frame restart. Di frame itu
    pemegang langsung diatur ke tim pelaku restart (tim yang menendang atau melempar memegang bola).
    Mengembalikan array tim per frame (nobody pada frame mati atau belum diketahui).
    """
    n = len(team_codes)
    out = np.full(n, nobody, dtype=np.int8)
    current, cand, cand_count, cand_start = nobody, nobody, 0, 0
    for i in range(n):
        if dead[i]:
            current, cand, cand_count = nobody, nobody, 0
            continue
        if restart_hint is not None and restart_hint[i] != nobody:
            current, cand, cand_count = restart_hint[i], nobody, 0
        t = team_codes[i]
        if current == nobody:
            if t != nobody:
                current = t
        elif t == nobody:
            pass                                   # tidak ada bukti: pertahankan
        elif t == current:
            cand, cand_count = nobody, 0
        else:
            if t == cand:
                cand_count += 1
            else:
                cand, cand_count, cand_start = t, 1, i
            if cand_count >= switch_frames:
                out[cand_start:i + 1] = t          # penanggalan mundur
                current, cand, cand_count = t, nobody, 0
                continue
        out[i] = current
    return out


def combine(team_codes, dead, label_d=2, label_x=3):
    """Gabungkan tim dan bola mati menjadi kode label: 0=H, 1=A, 2=D, 3=X."""
    labels = np.where(team_codes == 0, 0, np.where(team_codes == 1, 1, label_x)).astype(np.int8)
    labels[dead] = label_d
    return labels


def merge_short_islands(labels, min_len):
    """Rentetan H/A yang lebih pendek dari min_len dan diapit tim yang sama dianggap kedipan."""
    out = labels.copy()
    starts, ends = run_bounds(labels)
    for k in range(1, len(starts) - 1):
        value = labels[starts[k]]
        before, after = labels[starts[k - 1]], labels[starts[k + 1]]
        if value in (0, 1) and (ends[k] - starts[k]) < min_len and before == after and before in (0, 1):
            out[starts[k]:ends[k]] = before
    return out
