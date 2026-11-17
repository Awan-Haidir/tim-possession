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
PLAYER_SLOW_MS = 1.0              # pemain dianggap berjalan/diam jika lebih lambat dari ini (m/s)
BALL_SPEED_SMOOTH_FRAMES = 5      # median bergulir untuk meredam goyangan posisi bola (~0,2 detik)

# --- SAKLAR VERSI. Semua False + MIN_SPELL_FRAMES=25 + MIN_DEAD_FRAMES=0 = perilaku v1 (persis) ----
USE_CORROBORATION = True          # bola hilang lama dianggap mati hanya jika ada penguat
USE_SMART_TAGGING = True          # pakai SET PIECES sebagai penanda restart
USE_RESTART_TEAM_HINT = True      # tim pelaku restart memegang bola setelah restart
USE_CONTROL_GATE = True           # bola di udara/lepas atau diperebutkan = belum ada bukti kontrol

# --- deadball.py ---------------------------------------------------------------------------------
# Bola hilang berturut-turut selama ini (setelah interpolasi) dianggap bola mati.
DEAD_IF_BALL_MISSING_FRAMES = 75  # 3 detik. HIPOTESIS awal.
# Aturan opsional: bola nyaris diam cukup lama = bola mati. Mati secara bawaan sampai Anda uji.
USE_STILL_BALL_RULE = False
STILL_BALL_SPEED_MS = 0.5
STILL_BALL_FRAMES = 50
# Penguat untuk bola hilang lama (hanya jika USE_CORROBORATION): dianggap mati jika median
# "porsi pemain yang berjalan/diam" selama celah >= nilai ini, ATAU celah sangat panjang.
DEAD_SLOW_FRACTION = 0.5
DEAD_MISSING_ALWAYS_FRAMES = 500  # 20 detik tanpa bola: pasti bukan permainan normal (VAR, cedera, dsb.)
# Restart dari Smart Tagging (SET PIECES). Jendela tag adalah rentang beberapa detik di sekitar
# restart, jadi saat restart dicari di dalamnya: bola diam (quiet) lalu melaju.
RESTART_BALL_SPEED_MS = 3.0       # bola dianggap "ditendang/dilempar" jika lebih cepat dari ini
RESTART_QUIET_SPEED_MS = 1.0      # bola dianggap diam jika lebih lambat dari ini (atau tidak terlihat)
RESTART_QUIET_FRAMES = 15         # harus diam selama ini sebelum restart (0,6 detik)
# Bola mati dimulai dari kapan? Mundur dari restart sampai terakhir kali bola melaju kencang.
OPEN_PLAY_BALL_SPEED_MS = 6.0     # umpan, tembakan, sapuan jauh di atas ini; bola mati di bawahnya
DEAD_LOOKBACK_FRAMES = 500        # batas mundur: 20 detik
MIN_DEAD_FRAMES = 25              # bola mati yang lebih pendek dari ini dianggap noise (1 detik)

# --- team.py (gerbang kontrol) -------------------------------------------------------------------
# Tim hanya dianggap punya bukti kontrol jika pemain terdekatnya cukup dekat dan tidak sedang
# diperebutkan. Selain itu frame ini "tidak ada bukti" dan possession dipertahankan.
CONTROL_RADIUS_M = 3.0            # bola jauh dari semua pemain = di udara atau lepas
CONTEST_MARGIN_M = 0.5            # selisih jarak dua tim lebih kecil dari ini = duel

# --- smooth.py -----------------------------------------------------------------------------------
# Lawan harus lebih dekat ke bola selama ini (frame berturut-turut) sebelum possession dianggap pindah.
# Alasan: CHALLENGE.md memberi proxy kontrol "pemain menguasai bola beberapa detik" atau "lebih
# dari dua umpan beruntun" (sekitar 2-3,5 detik). 50 frame = 2 detik = batas bawah proxy itu.
# Sumbernya juga: dari baris baseline yang diterbitkan panitia, jendela +/-2 detik terbaik di
# antara +/-1, 2 dan 5 detik. Penanggalan mundur membuat keterlambatan ini tidak merugikan.
SWITCH_FRAMES = 50                # 2 detik.
# Possession yang lebih pendek dari ini, diapit tim lawan yang sama di kedua sisi (tanpa bola mati),
# belum mencapai "kontrol" (tengah proxy: 3 detik) dan dianggap bagian possession lawan.
# Catatan: nilai <= SWITCH_FRAMES tidak pernah berlaku, karena hysteresis sudah menjamin >= SWITCH_FRAMES.
MIN_SPELL_FRAMES = 75             # 3 detik.
# Petunjuk tim restart berlaku di frame restart (jika tag Team bukan N/A).
