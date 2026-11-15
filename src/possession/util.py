"""Fungsi kecil yang dipakai banyak modul."""
import numpy as np


def run_bounds(values):
    """Pecah array menjadi rentetan nilai sama. Mengembalikan (starts, ends) dengan ends eksklusif."""
    values = np.asarray(values)
    if len(values) == 0:
        return np.array([], dtype=int), np.array([], dtype=int)
    change = np.flatnonzero(values[1:] != values[:-1]) + 1
    starts = np.concatenate(([0], change))
    ends = np.concatenate((change, [len(values)]))
    return starts, ends


def true_runs(mask):
    """Daftar (awal, akhir_eksklusif) untuk setiap rentetan True pada mask boolean."""
    mask = np.asarray(mask, dtype=bool)
    if not mask.any():
        return []
    padded = np.concatenate(([False], mask, [False]))
    change = np.flatnonzero(padded[1:] != padded[:-1])
    return list(zip(change[0::2], change[1::2]))
