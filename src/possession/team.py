"""STASIUN 4b: bukti tim yang menguasai bola per frame (mentah, masih berkedip)."""
import numpy as np


def evidence(features, p):
    """Tim yang punya bukti kontrol di tiap frame (0=home, 1=away, -1=tidak ada bukti).

    Baseline hanya memakai pemain terdekat. Dengan USE_CONTROL_GATE ada dua tambahan:
      1. Bola jauh dari semua pemain (> CONTROL_RADIUS_M): bola di udara atau lepas. Tidak ada
         bukti kontrol, jadi possession dipertahankan (umpan jauh tidak mengubah pemegang).
      2. Dua tim hampir sama dekat (selisih < CONTEST_MARGIN_M): duel. Belum ada pemenang jelas.
    Frame tanpa bukti tidak menggeser possession (lihat smooth.hysteresis).
    """
    nearest = features["nearest_team"].copy()
    if not p.USE_CONTROL_GATE:
        return nearest

    near_d = features["nearest_dist"]
    other = np.where(nearest == 0, features["d_away"], features["d_home"])
    out = nearest.copy()
    out[near_d > p.CONTROL_RADIUS_M] = -1
    with np.errstate(invalid="ignore"):
        contested = (other - near_d) < p.CONTEST_MARGIN_M
    out[contested & (nearest >= 0)] = -1
    return out
