"""STASIUN 4a: menentukan frame bola mati (D).

Ini bagian yang paling banyak membutuhkan football analyst. Aturan di bawah adalah hipotesis;
keputusan akhirnya harus tertulis di docs/possession_rules.md beserta alasannya.

Aturan (setiap aturan punya saklar di configs/params.py):
  A. Bola hilang lama. Bola hilang tidak otomatis berarti bola mati (bisa tertutup pemain atau
     di udara). Dengan USE_CORROBORATION celah >= DEAD_IF_BALL_MISSING_FRAMES dianggap mati hanya
     jika pemain juga melambat serempak, atau celahnya sangat panjang.
  B. Restart dari Smart Tagging (SET PIECES). Di dalam jendela tag dicari saat restart (bola diam
     lalu melaju). Bola mati dihitung dari terakhir kali bola melaju kencang sampai restart.
  C. (opsional) bola nyaris diam cukup lama.
  D. Frame dari awal babak 2 yang dinilai sampai kick-off = mati (FAQ.md).
"""
import numpy as np

from . import tagging_prior
from .util import true_runs


def _drop_short_runs(mask, min_len):
    if min_len <= 0:
        return mask
    out = mask.copy()
    for start, end in true_runs(mask):
        if end - start < min_len:
            out[start:end] = False
    return out


def find_restart_frame(speed, start, end, p):
    """Frame pertama di [start, end] saat bola melaju setelah cukup lama diam. None jika tidak ada.

    Frame bola tidak terlihat (NaN) dihitung diam: bola yang dipegang pelempar sering tertutup.
    """
    n = len(speed)
    quiet = ~(speed >= p.RESTART_QUIET_SPEED_MS)
    fast = speed >= p.RESTART_BALL_SPEED_MS
    for f in range(max(1, start), min(n, end + 1)):
        if fast[f] and f - p.RESTART_QUIET_FRAMES >= 0 and quiet[f - p.RESTART_QUIET_FRAMES:f].all():
            return f
    return None


def dead_start(speed, restart, floor, p):
    """Frame awal bola mati: tepat setelah terakhir kali bola melaju kencang sebelum restart."""
    lo = max(floor, restart - p.DEAD_LOOKBACK_FRAMES)
    fast_idx = np.flatnonzero(speed[lo:restart] >= p.OPEN_PLAY_BALL_SPEED_MS)
    return lo + int(fast_idx[-1]) + 1 if len(fast_idx) else lo


def detect(features, p, events=None, prekickoff_range=None):
    """Mengembalikan (dead, restarts, parts).

      dead      bool per frame, True = bola mati
      restarts  daftar {frame, start, team, type, window} (frame None jika restart tidak ketemu)
      parts     dict mask per aturan, untuk diagnosis
    """
    present = features["ball_present"]
    n = len(present)
    speed = features["ball_speed"]
    slow = features["slow_fraction"]

    # --- A. bola hilang lama --------------------------------------------------------------
    by_missing = np.zeros(n, dtype=bool)
    for start, end in true_runs(~present):
        length = end - start
        if length < p.DEAD_IF_BALL_MISSING_FRAMES:
            continue
        if not p.USE_CORROBORATION:
            by_missing[start:end] = True
            continue
        window = slow[start:end]
        median = np.median(window[np.isfinite(window)]) if np.isfinite(window).any() else np.nan
        if length >= p.DEAD_MISSING_ALWAYS_FRAMES or (np.isfinite(median) and median >= p.DEAD_SLOW_FRACTION):
            by_missing[start:end] = True

    # --- B. restart dari Smart Tagging ----------------------------------------------------
    by_restart = np.zeros(n, dtype=bool)
    restarts = []
    if p.USE_SMART_TAGGING and events:
        floor = 0
        for event in tagging_prior.restart_events(events, p):
            frame = find_restart_frame(speed, event["start"], event["end"], p)
            record = {"frame": frame, "start": None, "team": event["team"], "type": event["type"],
                      "window": (event["start"], event["end"])}
            if frame is not None:
                begin = dead_start(speed, frame, floor, p)
                by_restart[begin:frame] = True
                record["start"] = begin
                floor = frame
            restarts.append(record)

    # --- C. bola diam lama (opsional) -----------------------------------------------------
    by_still = np.zeros(n, dtype=bool)
    if p.USE_STILL_BALL_RULE:
        still = np.nan_to_num(speed < p.STILL_BALL_SPEED_MS, nan=0).astype(bool)
        for start, end in true_runs(still):
            if end - start >= p.STILL_BALL_FRAMES:
                by_still[start:end] = True

    # --- D. sebelum kick-off babak 2 ------------------------------------------------------
    by_prekick = np.zeros(n, dtype=bool)
    if prekickoff_range is not None:
        lo, hi = prekickoff_range
        by_prekick[lo:min(hi, n)] = True

    dead = _drop_short_runs(by_missing | by_restart | by_still, p.MIN_DEAD_FRAMES) | by_prekick
    parts = {"missing": by_missing, "restart": by_restart, "still": by_still, "prekick": by_prekick}
    return dead, restarts, parts
