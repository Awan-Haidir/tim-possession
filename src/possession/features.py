"""STASIUN 3: mengubah posisi menjadi ukuran yang bermakna bagi sepak bola.

Semua posisi sudah dalam meter. Tempat menambah ide dari football analyst
(arah hadap, tekanan, bentuk tim, dsb.).
"""
import numpy as np
import pandas as pd


def compute(ball, players, player_speed, team_of_slot, p, chunk=20000):
    """Fitur per frame. Mengembalikan dict array sepanjang jumlah frame.

      ball_present     bool   bola punya posisi (setelah pengisian celah singkat)
      nearest_team     int8   tim pemain terdekat ke bola (-1 jika tidak diketahui)
      nearest_dist     float  jarak pemain terdekat ke bola (m)
      d_home, d_away   float  jarak pemain terdekat tiap tim (m)
      n_near_home/away int    jumlah pemain tiap tim dalam radius p.NEAR_RADIUS_M dari bola
      ball_speed       float  kecepatan bola (m/s), median bergulir; NaN jika bola tidak terlihat
      slow_fraction    float  porsi pemain terlacak yang berjalan/diam (< p.PLAYER_SLOW_MS)
    """
    n = players.shape[0]
    is_home = team_of_slot == 0
    is_away = team_of_slot == 1

    nearest_team = np.full(n, -1, dtype=np.int8)
    nearest_dist = np.full(n, np.inf)
    d_home = np.full(n, np.inf)
    d_away = np.full(n, np.inf)
    n_home = np.zeros(n, dtype=np.int16)
    n_away = np.zeros(n, dtype=np.int16)
    slow_fraction = np.full(n, np.nan)

    for lo in range(0, n, chunk):
        hi = min(n, lo + chunk)
        diff = players[lo:hi] - ball[lo:hi, None, :]
        dist = np.sqrt((diff ** 2).sum(axis=2))          # NaN jika pemain atau bola hilang
        dist = np.where(np.isnan(dist), np.inf, dist)
        best = dist.argmin(axis=1)
        best_dist = dist[np.arange(hi - lo), best]
        known = np.isfinite(best_dist)
        nearest_dist[lo:hi] = best_dist
        nearest_team[lo:hi] = np.where(known, team_of_slot[best], -1)
        d_home[lo:hi] = dist[:, is_home].min(axis=1) if is_home.any() else np.inf
        d_away[lo:hi] = dist[:, is_away].min(axis=1) if is_away.any() else np.inf
        near = dist <= p.NEAR_RADIUS_M
        n_home[lo:hi] = near[:, is_home].sum(axis=1)
        n_away[lo:hi] = near[:, is_away].sum(axis=1)

        speed = player_speed[lo:hi]
        valid = ~np.isnan(speed)
        tracked = valid.sum(axis=1)
        slow = ((speed < p.PLAYER_SLOW_MS) & valid).sum(axis=1)
        slow_fraction[lo:hi] = np.where(tracked > 0, slow / np.maximum(tracked, 1), np.nan)

    ball_present = ~np.isnan(ball[:, 0])
    raw_speed = np.full(n, np.nan)
    raw_speed[1:] = np.sqrt((np.diff(ball, axis=0) ** 2).sum(axis=1)) * p.FPS
    ball_speed = (pd.Series(raw_speed)
                  .rolling(p.BALL_SPEED_SMOOTH_FRAMES, center=True, min_periods=1)
                  .median().to_numpy())

    return {
        "ball_present": ball_present,
        "nearest_team": nearest_team,
        "nearest_dist": nearest_dist,
        "d_home": d_home,
        "d_away": d_away,
        "n_near_home": n_home,
        "n_near_away": n_away,
        "ball_speed": ball_speed,
        "slow_fraction": slow_fraction,
    }
