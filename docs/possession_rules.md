# Aturan possession dan bola mati (football analyst)

Setiap aturan adalah logika UMUM (berlaku di seluruh pertandingan), bukan terikat frame tertentu.
Setiap angka di `configs/params.py` punya alasan di sini. Ini bahan bagian "possession rules" di dokumen teknis.

## 1. Kapan bola mati (D)

Bola mati terjadi jika bola sepenuhnya melewati garis gawang atau garis samping, atau wasit menghentikan permainan.

| Penyebab | Restart | Bisa dideteksi dari data? |
|---|---|---|
| Bola keluar lewat garis samping | Lemparan ke dalam | Ya, lewat Smart Tagging (`Throw-in`) |
| Bola keluar lewat garis gawang | Tendangan gawang atau sudut | Ya, lewat Smart Tagging |
| Gol | Kick-off | Ya, lewat Smart Tagging (`Kick Off (After Goal)`) |
| Pelanggaran, handball, offside | Tendangan bebas atau penalti | Sebagian (Smart Tagging `Free Kick`) |
| Cedera, pergantian pemain, VAR, jeda minum | Dropped ball atau lanjut | Sulit: hanya lewat petunjuk tidak langsung |
| Gangguan luar (penonton, benda asing, bola rusak) | Dropped ball atau lanjut | Sulit |
| Awal babak | Kick-off | Ya (frame 110.808–113.741 semuanya D) |

## 2. BUKAN bola mati (jangan dipotong)

| Situasi | Alasan |
|---|---|
| Bola di tangan kiper | Masih dalam permainan; possession tetap tim kiper |
| Bola mengenai tiang atau mistar | Masih hidup |
| Bola di udara, belum sepenuhnya melewati garis | Masih hidup |
| Advantage | Wasit membiarkan permainan lanjut |
| Tendangan bebas atau lemparan cepat | D hanya sebentar |
| Bola hilang dari tracking (tertutup pemain, di udara) | Bola hilang BUKAN bola mati |

## 3. Aturan bola mati di program

| Aturan | Cara kerja | Alasan sepak bola |
|---|---|---|
| A. Bola hilang lama | Celah >= 3 detik dianggap D hanya jika pemain juga melambat serempak (median >= 50% pemain < 1 m/s), atau celah >= 20 detik | Saat permainan berhenti pemain berjalan; bola hilang saat bermain biasanya karena tertutup atau di udara |
| B. Restart dari Smart Tagging | Di jendela `SET PIECES` dicari restart: bola diam >= 0,6 detik lalu melaju > 3 m/s. D dihitung dari terakhir kali bola melaju > 6 m/s sampai restart (maksimal 20 detik ke belakang) | Restart selalu didahului bola diam; umpan, tembakan, dan sapuan jauh lebih cepat dari 6 m/s, bola yang menunggu restart nyaris diam |
| C. Bola diam lama | Dimatikan dulu | Pemain bisa memegang bola diam saat bermain |
| D. Sebelum kick-off babak 2 | Frame 110.808–113.741 = D | Diterbitkan di FAQ.md |
| Buang D < 1 detik | Dianggap noise | Stoppage nyata lebih lama |

**Keterbatasan yang diakui:** jendela Smart Tagging hanya mencakup restart, jadi bola mati karena cedera, VAR, atau pelanggaran tanpa tag hanya terdeteksi lewat aturan A. Throw-in tidak punya tag tim.

## 4. Kapan possession berpindah

| Situasi | Keputusan | Alasan | Parameter |
|---|---|---|---|
| Lawan menyentuh bola sekilas atau deflection | Tidak berpindah | Tidak ada kontrol | `SWITCH_FRAMES` |
| Lawan terus yang terdekat >= 2 detik | Berpindah (titik pindah dimundurkan ke bukti pertama) | Proxy kontrol di CHALLENGE.md: "pemain menguasai bola beberapa detik" | `SWITCH_FRAMES = 50` |
| Bola di udara atau lepas (jauh dari semua pemain) | Possession dipertahankan | Umpan jauh tidak mengubah pemegang | `CONTROL_RADIUS_M = 3.0` |
| Duel (dua tim hampir sama dekat) | Possession dipertahankan sampai ada pemenang jelas | Belum ada kontrol | `CONTEST_MARGIN_M = 0.5` |
| Possession lawan < 3 detik, diapit tim yang sama | Dianggap bagian possession tim itu | Belum mencapai kontrol | `MIN_SPELL_FRAMES = 75` |
| Restart | Tim pelaku restart memegang bola | Tim yang menendang atau melempar menguasai bola | tag `Team` (bukan N/A) |
| Duel udara tanpa kontrol lanjutan | Tidak berpindah | CHALLENGE.md | |
| Bola lepas atau diperebutkan | Tetap tim terakhir | CHALLENGE.md | |

## 5. Alasan nilai parameter (hipotesis, bukan hasil tuning ke ground truth)

| Parameter | Nilai | Alasan |
|---|---|---|
| `MAX_BALL_GAP_FRAMES` | 12 (0,5 detik) | Celah sekecil itu hampir selalu tertutup pemain; bola tidak berpindah jauh |
| `SWITCH_FRAMES` | 50 (2 detik) | Batas bawah proxy kontrol (2–3,5 detik). Dari baris baseline yang diterbitkan, jendela +/-2 detik terbaik dibanding +/-1 dan +/-5 detik |
| `MIN_SPELL_FRAMES` | 75 (3 detik) | Tengah proxy kontrol. Nilai <= `SWITCH_FRAMES` tidak pernah berlaku |
| `DEAD_IF_BALL_MISSING_FRAMES` | 75 | Bola tertutup dalam permainan jarang lebih dari 3 detik |
| `DEAD_MISSING_ALWAYS_FRAMES` | 500 (20 detik) | Bola hilang 20 detik hampir pasti jeda panjang |
| `PLAYER_SLOW_MS` | 1,0 m/s | Berjalan pelan; bermain biasanya jogging dan lari |
| `OPEN_PLAY_BALL_SPEED_MS` | 6,0 | Umpan pendek profesional jauh lebih cepat |
| `RESTART_BALL_SPEED_MS` | 3,0 | Tendangan atau lemparan jauh lebih cepat |
| `CONTROL_RADIUS_M` | 3,0 | Pemain yang menguasai bola berada dalam beberapa meter |
| `CONTEST_MARGIN_M` | 0,5 | Selisih jarak lebih kecil dari ini = duel |

Pemilihan nilai dilakukan dengan alasan di atas dan diperiksa kestabilannya lewat `scripts/diagnose.py`
(tabel sensitivitas), BUKAN dari skor ground truth publik.

## 6. Kasus sulit

| Situasi | Keputusan |
|---|---|
| Tembakan diblok | Tetap tim penembak sampai lawan mengontrol bola |
| Kiper menangkap bola | Berpindah ke tim kiper |
| Kiper menepis bola | Tetap tim penyerang sampai ada kontrol baru |
| Bola lepas di kerumunan | Tim terakhir yang menguasai |
| Tendangan bebas cepat | D berakhir saat bola disentuh kembali |
