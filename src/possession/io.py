"""STASIUN 1: membaca data. Hanya membaca, tidak mengubah apa pun.

Format baris mentah ATD:  <frame_id>:<pemain>;<pemain>;...:<bola>
tiap grup berbentuk "x,y,kecepatan"; nilai hilang ditulis NaN.
frame_id mulai dari 1, sedangkan submission mulai dari 0  ->  video_frame = frame_id - 1
"""
import xml.etree.ElementTree as ET

import numpy as np


def team_of_slot(meta_path, home=0, away=1):
    """Array panjang n_slot: 0 jika slot milik tim home, 1 jika away.

    Tim pertama di metadata adalah home (konvensi FIFA/EPTS; untuk laga ini Barcelona).
    Slot BUKAN orang: ada 46 slot untuk 22 pemain, slot muncul, hilang, dan bertukar identitas.
    """
    root = ET.parse(meta_path).getroot()
    team_ids = [team.get("id") for team in root.iter("Team")]
    if len(team_ids) != 2:
        raise ValueError("{}: diharapkan 2 tim, ditemukan {}".format(meta_path, len(team_ids)))
    slots = [player.get("teamId") for player in root.iter("Player")]
    if not slots:
        raise ValueError("{}: tidak ada elemen Player".format(meta_path))
    return np.array([home if tid == team_ids[0] else away for tid in slots], dtype=np.int8)


def _xy(group):
    group = group.strip()
    if not group or group[0] == "N":          # "NaN,NaN,NaN" atau kosong
        return np.nan, np.nan
    parts = group.split(",")
    return float(parts[0]), float(parts[1])


def load_tracking(raw_path, n_frames, n_slots):
    """Baca tracking mentah.

    Mengembalikan:
      ball    (n_frames, 2)          posisi bola ternormalisasi 0-1, NaN jika tidak terlihat
      players (n_frames, n_slots, 2) posisi pemain ternormalisasi 0-1, NaN jika slot kosong
    """
    ball = np.full((n_frames, 2), np.nan)
    players = np.full((n_frames, n_slots, 2), np.nan)
    with open(raw_path) as handle:
        for line in handle:
            parts = line.split(":")
            if len(parts) != 3:
                continue
            frame = int(parts[0]) - 1
            if not 0 <= frame < n_frames:
                continue
            ball[frame] = _xy(parts[2])
            for slot, group in enumerate(parts[1].split(";")):
                if slot >= n_slots:
                    break
                players[frame, slot] = _xy(group)
    return ball, players


def load_smart_tagging(path, fps=25):
    """Daftar fase/set piece: [{code, start_frame, end_frame, tags}].

    Waktu di XML = detik sejak frame pertama video, jadi frame = round(detik * fps).
    PERINGATAN: ini otomatis, bukan ground truth. Tag Team bernilai 'N/A' pada 36 instance,
    termasuk SEMUA lemparan ke dalam. Interval adalah jendela waktu, bukan titik presisi.
    """
    events = []
    for instance in ET.parse(path).getroot().iter("instance"):
        start_s = float(instance.findtext("start"))
        end_s = float(instance.findtext("end"))
        events.append({
            "code": (instance.findtext("code") or "").strip(),
            "start_frame": int(round(start_s * fps)),
            "end_frame": int(round(end_s * fps)),
            "tags": {label.findtext("group"): label.findtext("text")
                     for label in instance.findall("label")},
        })
    return events
