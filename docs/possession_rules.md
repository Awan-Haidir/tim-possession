# Aturan possession dan bola mati (diisi oleh football analyst)

Dokumen ini menjadi dasar bagian "possession rules" di dokumen teknis.
Setiap aturan harus logika UMUM (berlaku di seluruh pertandingan), bukan terikat frame tertentu.
Setiap angka di `configs/params.py` harus punya alasan sepak bola di sini.

## 1. Kapan possession berpindah

| Situasi | Keputusan | Alasan sepak bola | Parameter terkait |
|---|---|---|---|
| Lawan menyentuh bola sekilas (deflection) | Tidak berpindah | Tidak ada kontrol | `SWITCH_FRAMES` |
| Lawan menguasai bola beberapa detik | Berpindah | Proxy kontrol (CHALLENGE.md) | `SWITCH_FRAMES` |
| Duel udara tanpa kontrol lanjutan | Tidak berpindah | Sesuai CHALLENGE.md | |
| Bola lepas atau diperebutkan | Tetap tim terakhir | Sesuai CHALLENGE.md | |
| (tambahkan) | | | |

## 2. Bola mati (D)

| Jenis | Ciri di tracking | Kapan D mulai | Kapan D berakhir |
|---|---|---|---|
| Lemparan ke dalam | | | |
| Tendangan gawang | | | |
| Tendangan sudut | | | |
| Tendangan bebas | | | |
| Kick-off (awal dan setelah gol) | | | |

Catatan: frame 110.808–113.741 (sebelum kick-off babak 2) semuanya D (FAQ.md).

## 3. Alasan nilai parameter

| Parameter | Nilai | Alasan |
|---|---|---|
| `MAX_BALL_GAP_FRAMES` | 12 | |
| `DEAD_IF_BALL_MISSING_FRAMES` | 75 | |
| `SWITCH_FRAMES` | 50 | |
| `MIN_SPELL_FRAMES` | 25 | |

## 4. Kasus sulit dan keputusannya

| Situasi | Keputusan |
|---|---|
| Tembakan diblok | |
| Kiper menangkap bola | |
| Kiper menepis bola | |
| Bola lepas di kerumunan | |
| Tendangan bebas cepat | |
