"""STASIUN 4b: menentukan tim yang menguasai bola per frame (mentah, masih berkedip)."""


def nearest_team(features):
    """Baseline: tim pemain terdekat ke bola. -1 jika bola atau pemain tidak diketahui.

    TODO (data scientist): gabungkan jarak, kecepatan bola, jumlah pemain dekat bola
    (features['n_near_home'], features['n_near_away']), dsb.
    """
    return features["nearest_team"].copy()
