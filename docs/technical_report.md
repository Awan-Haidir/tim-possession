# Dokumen teknis — <NAMA TIM>

(Beberapa halaman saja. Simpan sebagai `<nama_tim>.pdf` atau `<nama_tim>.md` saat mengumpulkan.)

## 1. Pendekatan
Apa yang dibangun dan mengapa memilih ini dibanding alternatifnya.

## 2. Aset yang dipakai dan dibuang
| Aset | Dipakai? | Bagaimana / mengapa dibuang |
|---|---|---|
| Tracking tactical (ATD) | | |
| Smart Tagging | | |
| Homography | | |
| Video tactical | | |
| Data broadcast | | |

## 3. Data latih
Sebutkan setiap data berlabel yang dipakai, sumbernya, siapa yang melabeli, dan jumlahnya.
Tidak boleh ada yang berasal dari pertandingan ini. Jika tidak ada: "Tidak ada; pendekatan berbasis aturan."

## 4. Aturan possession yang diimplementasikan
(Ringkas dari `docs/possession_rules.md`: bola lepas, duel, restart, bola mati.)

## 5. Penanganan data hilang dan berisik
Bola hilang (sekitar 41% frame yang dinilai), ID tertukar, celah tracking.

## 6. Keterbatasan
Di mana pendekatan gagal dan apa yang akan diperbaiki jika ada waktu.

## 7. Reproduksi
```
pip install -r requirements.txt
python scripts/run_pipeline.py --data-dir data --out outputs/<nama_tim>.csv
python evaluation/validate_submission.py outputs/<nama_tim>.csv
```
