"""Semua angka yang dipakai pipeline ada di sini, bukan tersebar di kode.

ATURAN PENTING:
- Nilai di bawah adalah HIPOTESIS AWAL (placeholder) yang harus diputuskan oleh tim, dengan alasan
  sepak bola yang ditulis di docs/possession_rules.md.
- JANGAN memilih nilai dengan mencari skor terbaik pada ground truth publik 5 menit. Itu dilarang
  oleh RULES.md dan terbukti menyesatkan (lihat EVALUATION.md).
- JANGAN menaruh aturan atau angka yang terikat pada frame tertentu di pertandingan ini.
"""

# --- fakta pertandingan (dari DATA.md, diterbitkan panitia) ------------------------------------
N_FRAMES = 199319                 # jumlah frame video tactical = jumlah baris submission
FPS = 25
PITCH_LENGTH_M, PITCH_WIDTH_M = 105.3, 68.0

# Kode tim untuk tracking. Tim pertama di metadata XML adalah home (Barcelona).
HOME, AWAY, NOBODY = 0, 1, -1

# Kode label akhir (urutan sama dengan scorer panitia: H, A, D, X)
LABEL_H, LABEL_A, LABEL_D, LABEL_X = 0, 1, 2, 3

# Frame yang dinilai (batas diterbitkan di DATA.md). Di luar ini label ditulis X.
GRADED_BLOCKS = [(11185, 90651), (110808, 190197)]
# Babak 2 dinilai mulai 110808 tetapi baru kick-off di 113742; frame di antaranya semua D (FAQ.md).
PRE_KICKOFF_2ND_HALF = (110808, 113742)   # [awal, akhir) dalam frame

# --- nama file data (di dalam <data_dir>/tactical/) --------------------------------------------
ATD_RAW_NAME = "tactical/BAR-ATH_tactical_atd.txt"
ATD_META_NAME = "tactical/BAR-ATH_tactical_atd.xml"
SMART_TAGGING_NAME = "tactical/BAR-ATH_tactical_smart_tagging.xml"

# --- clean.py ------------------------------------------------------------------------------------
# Celah bola hilang yang lebih pendek dari ini diisi dengan garis lurus (interpolasi).
MAX_BALL_GAP_FRAMES = 12          # sekitar 0,5 detik. HIPOTESIS: tentukan dengan alasan sepak bola.

# --- features.py ---------------------------------------------------------------------------------
NEAR_RADIUS_M = 5.0               # pemain dianggap "dekat bola" dalam radius ini (meter)

# --- deadball.py ---------------------------------------------------------------------------------
# Bola hilang berturut-turut selama ini (setelah interpolasi) dianggap bola mati.
DEAD_IF_BALL_MISSING_FRAMES = 75  # 3 detik. HIPOTESIS awal.
# Aturan opsional: bola nyaris diam cukup lama = bola mati. Mati secara bawaan sampai Anda uji.
USE_STILL_BALL_RULE = False
STILL_BALL_SPEED_MS = 0.5
STILL_BALL_FRAMES = 50

# --- smooth.py -----------------------------------------------------------------------------------
# Lawan harus lebih dekat ke bola selama ini (frame berturut-turut) sebelum possession dianggap pindah.
SWITCH_FRAMES = 50                # 2 detik. HIPOTESIS awal (proxy "kontrol", lihat CHALLENGE.md).
# Possession yang lebih pendek dari ini, diapit possession tim yang sama, dianggap kedipan.
MIN_SPELL_FRAMES = 25             # 1 detik.
