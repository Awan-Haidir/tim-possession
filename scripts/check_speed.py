"""Periksa kecepatan bola: apakah kecepatan hasil hitung (dari posisi) wajar dibanding kecepatan di file?

    python scripts/check_speed.py --data-dir data

Dipakai untuk memastikan aturan bola mati dari restart (ambang 3 dan 6 m/s) bekerja pada data asli.
Hanya mencetak ringkasan angka (aman dibagikan, tidak memuat data frame).
"""
import argparse
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from configs import params as p  # noqa: E402
from possession import io  # noqa: E402


def file_ball_speed(raw_path, n_frames):
    """Kecepatan bola (m/s) langsung dari kolom ketiga grup bola di file ATD; NaN jika hilang."""
    speed = np.full(n_frames, np.nan)
    with open(raw_path) as handle:
        for line in handle:
            parts = line.split(":")
            if len(parts) != 3:
                continue
            frame = int(parts[0]) - 1
            group = parts[2].strip().split(",")
            if 0 <= frame < n_frames and len(group) > 2 and group[0][:1] != "N":
                speed[frame] = float(group[2])
    return speed


def pct(a):
    a = a[np.isfinite(a)]
    return "n/a" if len(a) == 0 else "p50 {:.1f}  p90 {:.1f}  p99 {:.1f}  maks {:.0f}".format(
        *np.percentile(a, [50, 90, 99]), a.max())


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default=os.environ.get("MTAH_DATA_DIR") or os.path.join(ROOT, "data"))
    args = parser.parse_args()

    raw = os.path.join(args.data_dir, p.ATD_RAW_NAME)
    meta = os.path.join(args.data_dir, p.ATD_META_NAME)
    slots = len(io.team_of_slot(meta))
    ball, _players, _speeds = io.load_tracking(raw, p.N_FRAMES, slots)
    ball_m = ball * np.array([p.PITCH_LENGTH_M, p.PITCH_WIDTH_M])
    derived = np.full(p.N_FRAMES, np.nan)
    derived[1:] = np.sqrt((np.diff(ball_m, axis=0) ** 2).sum(axis=1)) * p.FPS
    smooth = pd.Series(derived).rolling(p.BALL_SPEED_SMOOTH_FRAMES, center=True, min_periods=1).median().to_numpy()
    from_file = file_ball_speed(raw, p.N_FRAMES)

    graded = np.zeros(p.N_FRAMES, dtype=bool)
    for first, last in p.GRADED_BLOCKS:
        graded[first:last + 1] = True

    both = np.isfinite(ball_m[:, 0])
    same = (np.diff(ball_m, axis=0) == 0).all(axis=1) & both[1:] & both[:-1]
    print("frame bola berturut-turut dengan posisi IDENTIK : {:.1f}%  (tinggi = posisi bola diperbarui lebih jarang dari 25x/detik)"
          .format(100 * same[graded[1:]].sum() / max(1, (both[1:] & both[:-1] & graded[1:]).sum())))

    for name, arr in (("kecepatan hitung mentah", derived), ("kecepatan hitung (median 5)", smooth),
                      ("kecepatan dari FILE", from_file)):
        a = arr[graded]
        valid = np.isfinite(a)
        print("\n{}".format(name))
        print("  sebaran (m/s)        : {}".format(pct(a)))
        print("  porsi >= 3 m/s       : {:.1f}%   porsi >= 6 m/s: {:.1f}%   (dari frame yang bolanya ada)".format(
            100 * (a[valid] >= 3).mean(), 100 * (a[valid] >= 6).mean()))

    both_ok = np.isfinite(derived) & np.isfinite(from_file) & graded
    if both_ok.sum() > 100:
        ratio = np.median(from_file[both_ok] / np.maximum(derived[both_ok], 1e-6))
        with np.errstate(invalid="ignore", divide="ignore"):
            corr = np.corrcoef(derived[both_ok], from_file[both_ok])[0, 1]
        print("\nhitung vs FILE: korelasi {:.2f}   rasio median (file / hitung) {:.2f}".format(corr, ratio))


if __name__ == "__main__":
    main()