# Possession per frame — More than a Hack 2027 (Initial Challenge)

Tim: **<NAMA TIM>**

Untuk setiap frame pertandingan Barcelona vs Athletic, program ini menghasilkan label
`H` (home menguasai), `A` (away menguasai), `D` (bola mati), atau `X` (tidak dinilai / tidak menjawab).

## Cara menjalankan

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows PowerShell; di Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

# 1. taruh data lomba di data/tactical/ (JANGAN di-commit)
# 2. hasilkan submission (satu perintah)
python scripts/run_pipeline.py --data-dir data --out outputs/<nama_tim>.csv

# 3. periksa format
python evaluation/validate_submission.py outputs/<nama_tim>.csv

# 4. (opsional) cek kebenaran pipeline pada 5 menit publik
cp outputs/<nama_tim>.csv evaluation/results/
python evaluation/run_evaluation.py
```

Data berada di `data/tactical/`:
`BAR-ATH_tactical_atd.txt`, `BAR-ATH_tactical_atd.xml`, `BAR-ATH_tactical_smart_tagging.xml`,
`BAR-ATH_tactical_homography.csv`. Lokasi lain dapat diatur dengan `MTAH_DATA_DIR` atau `--data-dir`.

## Uji tanpa data (data buatan)

```bash
python tests/test_smooth.py
python tests/test_pipeline_synthetic.py
```

## Struktur

```
configs/params.py        semua angka di satu tempat (dengan alasan di docs/possession_rules.md)
src/possession/
  io.py                  baca tracking, metadata tim, Smart Tagging
  clean.py               ke meter, isi celah bola yang pendek
  features.py            jarak, kecepatan, pemain di sekitar bola
  deadball.py            frame bola mati (D)
  team.py                tim yang menguasai bola (mentah)
  tagging_prior.py       petunjuk dari Smart Tagging (belum terhubung)
  smooth.py              hilangkan kedipan (hysteresis, penggabungan pulau pendek)
  writer.py              tulis CSV
  pipeline.py            menyambung semua stasiun
scripts/run_pipeline.py  satu perintah penghasil submission
evaluation/              salinan alat panitia (lihat NOTICE.md)
docs/                    aturan possession dan dokumen teknis
```

## Reproduksi dan aturan lomba

- File dihasilkan sepenuhnya oleh algoritma; tidak ada label tangan dan tidak ada koreksi manual.
- Tidak memakai ground truth privat atau data event pertandingan ini.
- Ground truth publik hanya untuk memeriksa bahwa pipeline benar, bukan untuk memilih parameter.
- Tanpa angka acak: dua kali menjalankan menghasilkan file identik. Periksa dengan
  `Get-FileHash` (PowerShell) atau `sha256sum`.
- Data pertandingan tidak ada di repo ini dan tidak boleh didistribusikan.
- Berkas dari repo panitia tercantum di `NOTICE.md` (lisensi MIT).
