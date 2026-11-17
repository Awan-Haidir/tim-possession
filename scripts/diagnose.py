"""Diagnosis TANPA ground truth: apakah hasil masuk akal? Dan seberapa sensitif terhadap parameter?

    python scripts/diagnose.py --data-dir data

Hasilnya dipakai untuk menilai kewajaran dan memilih parameter di daerah yang STABIL.
Jangan memilih parameter dari skor 5 menit publik (dilarang, dan terbukti menyesatkan).
"""
import argparse
import os
import sys
import types

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from configs import params  # noqa: E402
from possession import pipeline, writer  # noqa: E402
from possession.util import true_runs  # noqa: E402


def with_params(**changes):
    p = types.SimpleNamespace(**{k: v for k, v in vars(params).items() if k.isupper()})
    for key, value in changes.items():
        setattr(p, key, value)
    return p


def graded_mask(n, blocks):
    mask = np.zeros(n, dtype=bool)
    for first, last in blocks:
        mask[first:last + 1] = True
    return mask


def summary(codes, p):
    alive = int(np.sum((codes == 0) | (codes == 1)))
    spells = writer.count_possessions(codes)
    return spells, (alive / p.FPS / spells if spells else 0.0)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default=os.environ.get("MTAH_DATA_DIR") or os.path.join(ROOT, "data"))
    args = parser.parse_args()

    p = with_params()
    prep = pipeline.prepare(args.data_dir, p)
    f, n = prep["features"], prep["n_frames"]
    graded = graded_mask(n, p.GRADED_BLOCKS)
    codes, d = pipeline.label(prep, p, return_details=True)

    print("== DATA (hanya frame yang dinilai: {}) ==".format(int(graded.sum())))
    print("bola terlihat setelah isi celah singkat : {:5.1f}%".format(100 * f["ball_present"][graded].mean()))
    print("bola terlihat asli                      : {:5.1f}%".format(100 * prep["observed"][graded].mean()))

    print("\n== BOLA MATI (D) ==")
    total = d["dead"][graded].sum()
    print("D total                  : {:6.1f}% dari frame yang dinilai".format(100 * total / graded.sum()))
    for name in ("missing", "restart", "still", "prekick"):
        print("  aturan {:<8} aktif    : {:6.1f}%".format(name, 100 * d["parts"][name][graded].mean()))
    runs = [e - s for s, e in true_runs(d["dead"] & graded)]
    if runs:
        secs = np.array(runs) / p.FPS
        print("jumlah rentetan D        : {}   median {:.1f} detik   persentil 90 {:.1f} detik   terpanjang {:.0f} detik"
              .format(len(runs), np.median(secs), np.percentile(secs, 90), secs.max()))

    no_corr = with_params(USE_CORROBORATION=False)
    from possession import deadball
    dead_old, _, _ = deadball.detect(f, no_corr, None, p.PRE_KICKOFF_2ND_HALF)
    print("D jika bola hilang lama LANGSUNG dianggap mati (v1): {:.1f}%".format(100 * dead_old[graded].mean()))

    if prep["events"]:
        found = [r for r in d["restarts"] if r["frame"] is not None]
        print("\n== RESTART DARI SMART TAGGING ==")
        print("set piece dalam tag      : {}".format(len(d["restarts"])))
        print("restart berhasil ditemukan: {}   gagal: {}".format(len(found), len(d["restarts"]) - len(found)))
        if found:
            lengths = np.array([r["frame"] - r["start"] for r in found]) / p.FPS
            print("lama bola mati sebelum restart: median {:.1f} detik   persentil 90 {:.1f} detik"
                  .format(np.median(lengths), np.percentile(lengths, 90)))
        print("restart dengan tim diketahui (bukan N/A): {}".format(
            sum(1 for r in found if r["team"] != p.NOBODY)))

    print("\n== BUKTI KONTROL ==")
    alive = graded & ~d["dead"]
    print("frame hidup dengan bukti tim (setelah gerbang kontrol): {:.1f}%".format(
        100 * (d["evidence"][alive] >= 0).mean()))
    print("  (jika jauh di bawah ~50%, longgarkan CONTROL_RADIUS_M atau CONTEST_MARGIN_M)")

    print("\n== HASIL AKHIR ==")
    spells, mean = summary(codes, p)
    print("possession {}   rata-rata {:.1f} detik".format(spells, mean))
    for name, value in zip("HADX", range(4)):
        print("  {}  {:5.1f}%".format(name, 100 * np.mean(codes[graded] == value)))

    print("\n== SENSITIVITAS: jumlah possession / rata-rata detik ==")
    print("(pilih nilai di daerah yang stabil, bukan yang kebetulan terbaik)")
    switches = (25, 37, 50, 75, 100)
    mins = (0, 50, 75, 100)
    print("{:>14}".format("MIN_SPELL \\ SWITCH") + "".join("{:>16}".format(s) for s in switches))
    for m in mins:
        row = "{:>14}".format(m)
        for s in switches:
            q = with_params(SWITCH_FRAMES=s, MIN_SPELL_FRAMES=m)
            c = pipeline.label(prep, q)
            sp, mu = summary(c, q)
            row += "{:>16}".format("{} / {:.1f}".format(sp, mu))
        print(row)


if __name__ == "__main__":
    main()
