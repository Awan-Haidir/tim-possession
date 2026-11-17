"""Uji pipeline ujung ke ujung dengan data tracking BUATAN (bukan data pertandingan).
Jalankan:  python tests/test_pipeline_synthetic.py
"""
import os
import sys
import tempfile
import types

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "src"))

from configs import params  # noqa: E402
from possession import pipeline, writer  # noqa: E402

N = 600


def make_synthetic(folder):
    """4 slot: 0,1 = home di kiri; 2,3 = away di kanan. Bola dekat home lalu dekat away."""
    os.makedirs(os.path.join(folder, "tactical"))
    meta = ('<root><Team id="T1"><Name>Home</Name></Team><Team id="T2"><Name>Away</Name></Team>'
            '<Player teamId="T1"/><Player teamId="T1"/><Player teamId="T2"/><Player teamId="T2"/></root>')
    with open(os.path.join(folder, params.ATD_META_NAME), "w") as handle:
        handle.write(meta)

    fixed = ["0.30,0.50,0", "0.30,0.60,0", "0.70,0.50,0", "0.70,0.60,0"]
    lines = []
    for i in range(N):
        if i < 300:
            ball = "0.31,0.50,0"
            if i % 50 == 25:
                ball = "0.69,0.50,0"                  # kedipan 1 frame ke dekat away
        else:
            ball = "0.69,0.50,0"
        if 100 <= i <= 110:
            ball = "NaN,NaN,NaN"                      # celah singkat (11 frame), harus terisi
        if 450 <= i < 540:
            ball = "NaN,NaN,NaN"                      # celah panjang (90 frame) = bola mati
        lines.append("{}:{}:{}".format(i + 1, ";".join(fixed), ball))
    with open(os.path.join(folder, params.ATD_RAW_NAME), "w") as handle:
        handle.write("\n".join(lines) + "\n")


def test_pipeline_end_to_end():
    p = types.SimpleNamespace(**{k: v for k, v in vars(params).items() if k.isupper()})
    p.SWITCH_FRAMES = 25
    p.USE_SMART_TAGGING = False
    with tempfile.TemporaryDirectory() as tmp:
        make_synthetic(tmp)
        codes = pipeline.run(tmp, p, n_frames=N, blocks=[(0, N - 1)], prekickoff_range=None)
        assert len(codes) == N
        assert (codes[450:540] == 2).all()            # celah panjang jadi D
        assert (codes[:300] == 0).all()               # kedipan hilang, home menguasai
        assert (codes[300:450] == 1).all()            # away menguasai
        assert writer.count_possessions(codes) == 3   # H, A, (D), A
        out = os.path.join(tmp, "out.csv")
        writer.write_csv(codes, out)
        with open(out) as handle:
            assert handle.readline() == "frame,label\n"
            assert len(handle.readlines()) == N
        # deterministik: dua kali jalan -> hasil sama
        again = pipeline.run(tmp, p, n_frames=N, blocks=[(0, N - 1)], prekickoff_range=None)
        assert (again == codes).all()


if __name__ == "__main__":
    test_pipeline_end_to_end()
    print("ok   test_pipeline_end_to_end")
