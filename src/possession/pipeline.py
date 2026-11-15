"""Menyambung semua stasiun. Satu fungsi, urutan jelas, tanpa angka acak (hasil selalu sama)."""
import os

from . import clean, deadball, features as feat, io, smooth, team, writer


def run(data_dir, p, n_frames=None, blocks=None, prekickoff_range="default"):
    """Hasilkan kode label (0=H, 1=A, 2=D, 3=X) untuk setiap frame.

    n_frames / blocks / prekickoff_range hanya diganti oleh tes dengan data sintetis.
    """
    n_frames = n_frames or p.N_FRAMES
    blocks = p.GRADED_BLOCKS if blocks is None else blocks
    if prekickoff_range == "default":
        prekickoff_range = p.PRE_KICKOFF_2ND_HALF

    raw_path = os.path.join(data_dir, p.ATD_RAW_NAME)
    meta_path = os.path.join(data_dir, p.ATD_META_NAME)

    team_of_slot = io.team_of_slot(meta_path, p.HOME, p.AWAY)
    ball, players = io.load_tracking(raw_path, n_frames, len(team_of_slot))

    ball, players = clean.to_metres(ball, players, p.PITCH_LENGTH_M, p.PITCH_WIDTH_M)
    ball, _observed = clean.fill_short_gaps(ball, p.MAX_BALL_GAP_FRAMES)

    features = feat.compute(ball, players, team_of_slot, p.NEAR_RADIUS_M, p.FPS)

    dead = deadball.detect(features, p, prekickoff_range=prekickoff_range)
    raw_team = team.nearest_team(features)
    stable_team = smooth.hysteresis(raw_team, dead, p.SWITCH_FRAMES, p.NOBODY)

    labels = smooth.combine(stable_team, dead, p.LABEL_D, p.LABEL_X)
    labels = smooth.merge_short_islands(labels, p.MIN_SPELL_FRAMES)
    return writer.apply_graded_blocks(labels, blocks, p.LABEL_X)
