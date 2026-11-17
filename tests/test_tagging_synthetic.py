"""Uji bola mati dari Smart Tagging dan gerbang kontrol, dengan data BUATAN.
Jalankan:  python tests/test_tagging_synthetic.py

Skenario (800 frame, 4 slot: 0,1 = home di x=0,30 ; 2,3 = away di x=0,70):
    0-99     bola diam dekat pemain away (away memegang)
    100-199  bola melaju (10 m/s) ke arah home          -> bola di udara, jauh dari semua pemain
    200-399  bola diam dekat pemain home                -> bola mati (tag SET PIECES: Goal Kick)
    400-549  bola ditendang ke arah away (6,6 m/s)
    550-799  bola diam dekat pemain away
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
from possession import pipeline  # noqa: E402

N = 800


def ball_x(i):
    if i < 100:
        return 0.69
    if i < 200:
        return 0.69 - 0.0038 * (i - 99)
    if i < 400:
        return 0.31
    if i < 550:
        return 0.31 + 0.0025 * (i - 399)
    return 0.69


def make_data(folder, team_tag):
    os.makedirs(os.path.join(folder, "tactical"))
    meta = ('<root><Team id="T1"><Name>Home</Name></Team><Team id="T2"><Name>Away</Name></Team>'
            '<Player teamId="T1"/><Player teamId="T1"/><Player teamId="T2"/><Player teamId="T2"/></root>')
    with open(os.path.join(folder, params.ATD_META_NAME), "w") as handle:
        handle.write(meta)
    fixed = "0.30,0.50,0;0.30,0.60,0;0.70,0.50,0;0.70,0.60,0"
    with open(os.path.join(folder, params.ATD_RAW_NAME), "w") as handle:
        for i in range(N):
            handle.write("{}:{}:{:.4f},0.50,0\n".format(i + 1, fixed, ball_x(i)))
    xml = ('<file><ALL_INSTANCES><instance><start>15.0</start><end>17.0</end><code>SET PIECES</code>'
           '<label><group>Team</group><text>{}</text></label>'
           '<label><group>Type</group><text>Goal Kick</text></label>'
           '<label><group>Half</group><text>1st Half</text></label>'
           '</instance></ALL_INSTANCES></file>').format(team_tag)
    with open(os.path.join(folder, params.SMART_TAGGING_NAME), "w") as handle:
        handle.write(xml)


def run(team_tag="Barcelona", **changes):
    p = types.SimpleNamespace(**{k: v for k, v in vars(params).items() if k.isupper()})
    p.SWITCH_FRAMES = 25
    for key, value in changes.items():
        setattr(p, key, value)
    with tempfile.TemporaryDirectory() as tmp:
        make_data(tmp, team_tag)
        prep = pipeline.prepare(tmp, p, n_frames=N)
        return pipeline.label(prep, p, blocks=[(0, N - 1)], prekickoff_range=None, return_details=True)


def test_restart_makes_dead_ball_and_home_restarts():
    codes, details = run()
    assert details["restarts"][0]["frame"] == 400            # restart ditemukan: diam lalu melaju
    assert (codes[200:400] == 2).all()                       # bola mati dari terakhir kali bola melaju
    assert (codes[:100] == 1).all()
    assert codes[400] == 0                                   # tim pelaku restart (Barcelona = home)
    assert (codes[560:] == 1).all()                          # bola tiba di away: possession pindah


def test_control_gate_keeps_possession_while_ball_is_in_the_air():
    with_gate, _ = run()
    assert (with_gate[100:200] == 1).all()                   # bola di udara: away tetap memegang
    without_gate, _ = run(USE_CONTROL_GATE=False)
    assert (without_gate[150:200] == 0).any()                # tanpa gerbang: pemain terdekat memindahkan


def test_restart_team_hint_wins_over_weak_evidence():
    codes, _ = run(team_tag="Atletic Club")
    assert (codes[400:440] == 1).all()                       # away melakukan restart, bukti home belum cukup
    codes_no_hint, _ = run(team_tag="Atletic Club", USE_RESTART_TEAM_HINT=False)
    assert codes_no_hint[400] == 0                           # tanpa petunjuk: ikut bukti pertama


def test_without_smart_tagging_no_dead_ball_when_ball_is_visible():
    codes, _ = run(USE_SMART_TAGGING=False)
    assert not (codes[250:350] == 2).any()                   # bola terlihat dan hilang tidak, jadi hidup


if __name__ == "__main__":
    for name, func in sorted(globals().items()):
        if name.startswith("test_"):
            func()
            print("ok  ", name)
