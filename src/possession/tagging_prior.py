"""STASIUN 4c (opsional): petunjuk dari Smart Tagging.

Smart Tagging otomatis, bukan kebenaran. Perlakukan sebagai bukti, bukan jawaban.
Tag Team di data berbunyi 'Barcelona' / 'Atletic Club' / 'N/A'.
"""
import numpy as np


def team_hint(events, n_frames, p):
    """Array int8 petunjuk tim per frame dari tag Team (-1 jika tidak ada).

    Saat ini belum dipakai oleh pipeline. Hubungkan ke team.py atau smooth.py setelah diuji.
    """
    hint = np.full(n_frames, -1, dtype=np.int8)
    for event in events:
        team = (event["tags"].get("Team") or "").strip().lower()
        if not team or team == "n/a":
            continue
        value = p.HOME if "barcelona" in team else p.AWAY
        hint[max(0, event["start_frame"]):min(n_frames, event["end_frame"])] = value
    return hint


def restarts(events):
    """Daftar (awal, akhir, jenis) untuk set piece (restart), mis. 'Throw-in', 'Corner Kick'."""
    return [(e["start_frame"], e["end_frame"], e["tags"].get("Type"))
            for e in events if e["code"].strip().lower() == "set pieces"]
