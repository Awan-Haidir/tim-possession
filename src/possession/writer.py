"""STASIUN 6: menulis file submission dan memeriksa bentuknya."""
import os

import numpy as np

LETTERS = np.array(["H", "A", "D", "X"])


def apply_graded_blocks(labels, blocks, label_x=3):
    """Frame di luar babak yang dinilai ditulis X (tidak dinilai, jadi tidak merugikan)."""
    out = np.full(len(labels), label_x, dtype=np.int8)
    for first, last in blocks:
        out[first:last + 1] = labels[first:last + 1]
    return out


def write_csv(codes, path):
    """Tulis CSV `frame,label`, satu baris per frame, header persis, akhir baris '\\n'."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    letters = LETTERS[np.asarray(codes, dtype=np.int8)]
    with open(path, "w", newline="\n") as handle:
        handle.write("frame,label\n")
        handle.writelines("{},{}\n".format(i, letter) for i, letter in enumerate(letters))
    return path


def count_possessions(codes):
    """Jumlah possession = rentetan berurutan H atau A (D memisahkan). Untuk pemeriksaan kewajaran."""
    from .util import run_bounds
    starts, _ = run_bounds(codes)
    return int(sum(1 for s in starts if codes[s] in (0, 1)))
