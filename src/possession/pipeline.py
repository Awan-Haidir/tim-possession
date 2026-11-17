"""Menyambung semua stasiun. Tanpa angka acak: hasil selalu sama.

Dibagi dua agar eksperimen cepat:
  prepare()  lambat (membaca 190 MB tracking), dijalankan sekali
  label()    cepat (aturan dan parameter), bisa diulang dengan parameter berbeda
"""
import os

import numpy as np

from . import clean, deadball, features as feat, io, smooth, tagging_prior, team, writer


def prepare(data_dir, p, n_frames=None):
    """Baca dan bersihkan data, hitung fitur. Mengembalikan dict untuk label()."""
    n_frames = n_frames or p.N_FRAMES
    raw_path = os.path.join(data_dir, p.ATD_RAW_NAME)
    meta_path = os.path.join(data_dir, p.ATD_META_NAME)
    tagging_path = os.path.join(data_dir, p.SMART_TAGGING_NAME)

    team_of_slot = io.team_of_slot(meta_path, p.HOME, p.AWAY)
    ball, players, player_speed = io.load_tracking(raw_path, n_frames, len(team_of_slot))
    ball, players = clean.to_metres(ball, players, p.PITCH_LENGTH_M, p.PITCH_WIDTH_M)
    ball, observed = clean.fill_short_gaps(ball, p.MAX_BALL_GAP_FRAMES)
    features = feat.compute(ball, players, player_speed, team_of_slot, p)

    events = []
    if p.USE_SMART_TAGGING:
        if os.path.isfile(tagging_path):
            events = io.load_smart_tagging(tagging_path, p.FPS)
        else:
            print("PERINGATAN: Smart Tagging tidak ditemukan ({}); dilewati.".format(tagging_path))
    return {"features": features, "events": events, "n_frames": n_frames, "observed": observed}


def label(prep, p, blocks=None, prekickoff_range="default", return_details=False):
    """Hasilkan kode label (0=H, 1=A, 2=D, 3=X) untuk setiap frame dari hasil prepare()."""
    blocks = p.GRADED_BLOCKS if blocks is None else blocks
    if prekickoff_range == "default":
        prekickoff_range = p.PRE_KICKOFF_2ND_HALF
    features = prep["features"]
    n = prep["n_frames"]

    dead, restarts, parts = deadball.detect(features, p, prep["events"], prekickoff_range)
    evidence = team.evidence(features, p)

    hint = None
    if p.USE_RESTART_TEAM_HINT:
        hint = np.full(n, p.NOBODY, dtype=np.int8)
        for restart in restarts:
            if restart["frame"] is not None and restart["team"] != p.NOBODY:
                hint[restart["frame"]] = restart["team"]

    stable = smooth.hysteresis(evidence, dead, p.SWITCH_FRAMES, p.NOBODY, hint)
    labels = smooth.combine(stable, dead, p.LABEL_D, p.LABEL_X)
    labels = smooth.merge_short_islands(labels, p.MIN_SPELL_FRAMES)
    codes = writer.apply_graded_blocks(labels, blocks, p.LABEL_X)
    if return_details:
        return codes, {"dead": dead, "restarts": restarts, "parts": parts, "evidence": evidence}
    return codes


def run(data_dir, p, n_frames=None, blocks=None, prekickoff_range="default"):
    """prepare() lalu label(): satu panggilan untuk tes dan skrip."""
    prep = prepare(data_dir, p, n_frames)
    return label(prep, p, blocks, prekickoff_range)
