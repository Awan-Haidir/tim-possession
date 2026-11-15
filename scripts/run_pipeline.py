"""SATU perintah yang menghasilkan file submission dari data lomba.

    python scripts/run_pipeline.py --data-dir data --out outputs/<nama_tim>.csv

Lalu periksa:
    python evaluation/validate_submission.py outputs/<nama_tim>.csv
"""
import argparse
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from configs import params  # noqa: E402
from possession import pipeline, writer  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data-dir", default=os.environ.get("MTAH_DATA_DIR") or os.path.join(ROOT, "data"))
    parser.add_argument("--out", default=os.path.join(ROOT, "outputs", "submission.csv"))
    args = parser.parse_args()

    codes = pipeline.run(args.data_dir, params)
    path = writer.write_csv(codes, args.out)

    print("ditulis: {}  ({} baris)".format(path, len(codes)))
    for name, value in zip("HADX", range(4)):
        count = int(np.sum(codes == value))
        print("  {}  {:>7}  {:5.1f}%".format(name, count, 100.0 * count / len(codes)))
    print("  possession: {}".format(writer.count_possessions(codes)))
    print("\nBerikutnya: python evaluation/validate_submission.py {}".format(path))


if __name__ == "__main__":
    main()
