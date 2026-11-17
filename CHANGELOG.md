# Perubahan v1 -> v2
(16 November 2026)

Semua perubahan punya saklar di `configs/params.py`. Dengan semua `USE_*` = False,
`MIN_SPELL_FRAMES = 25` dan `MIN_DEAD_FRAMES = 0`, keluaran v2 IDENTIK dengan v1 (sudah diuji).

## Perbaikan 1: bola mati dan Smart Tagging
- Kecepatan pemain dibaca dari tracking (`io.py`) dan menjadi fitur `slow_fraction`.
- Bola hilang lama tidak lagi otomatis D; harus ada penguat (pemain ikut melambat) atau celah >= 20 detik.
- Restart dari Smart Tagging `SET PIECES`: restart dicari di jendela tag, bola mati dihitung mundur dari restart.
- Tim pelaku restart (tag `Team`, bukan N/A) menjadi pemegang bola di frame restart.
- D yang lebih pendek dari 1 detik dibuang.

## Perbaikan 2: parameter beralasan
- `MIN_SPELL_FRAMES` 25 -> 75. Nilai lama tidak pernah berlaku (lebih kecil dari `SWITCH_FRAMES`).
- `SWITCH_FRAMES` tetap 50 dengan alasan tertulis (lihat `docs/possession_rules.md`).
- `scripts/diagnose.py`: kewajaran hasil dan tabel sensitivitas tanpa ground truth.

## Perbaikan 3: fitur selain pemain terdekat
- Gerbang kontrol: bola jauh dari semua pemain (> 3 m) atau duel (selisih < 0,5 m) = tidak ada bukti, possession dipertahankan.
- Fitur baru tersedia untuk eksperimen: `n_near_home/away`, `slow_fraction`, `ball_speed` (median bergulir).

## Belum diuji pada data asli oleh penulis kerangka ini
Semua perilaku baru diuji dengan data buatan. Jalankan `scripts/diagnose.py` pada data asli dan baca
peringatannya (terutama "frame hidup dengan bukti tim") sebelum memilih versi.
