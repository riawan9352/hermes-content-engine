# Workflow: Reporting Otomatis

Isi views & engagement puluhan link post ke Google Sheets tanpa ketik
angka. Ini workflow pertama yang disarankan — paling cepat kerasa hasil.

## Prasyarat

- [ ] Hermes Agent terinstall & DeepSeek API key sudah colok
      (lihat `setup.md`)
- [ ] Skill `sosmed-reporting` terpasang
- [ ] Google Sheet dengan tab `Reporting`
      (panduan: `../templates/reporting-sheet.md`)
- [ ] Kolom Link Posting sudah terisi, akses **Editor**

## Langkah

### 1. Siapkan sheet

Buat sheet `Reporting` dengan header:
`No, Link Posting, Views, Likes, Comments, Reposts, Shares, Screenshots`.
Isi kolom Link Posting dulu, kolom lain kosong. Share sebagai Editor.

### 2. Kirim prompt

Buka Hermes, paste:

```
[paste link Google Sheets lo]
lihat ke sheet "Reporting"
langsung isi semua views dan engagement sesuai link tertera
```

### 3. Klik Allow

Muncul popup **"Allow remote debugging?"** dari Chrome → klik **Allow**.
Ini izin Hermes menyetir browser kamu.

### 4. Lepas tangan

- Biarkan jendela Chrome terbuka, **jangan diganggu**
- Tanda Hermes aktif: ikon Hermes di tab yang sedang dibuka
- Kerja di aplikasi lain bebas — laptop harus tetap nyala
- Error "Invalid range" dsb. di tengah jalan itu **normal**

### 5. Verifikasi manual (wajib)

Setelah semua task centang:

1. Ambil 3 sampel random (atas–tengah–bawah)
2. Buka link-nya, cocokkan angka di sheet vs platform
3. Kalau cocok semua → laporan siap dikirim

## Kalau ada masalah

| Masalah | Solusi |
|---------|--------|
| Tidak bisa menulis | akses belum Editor → ubah di Share |
| Kolom kosong di IG/TikTok | memang tidak terlihat publik → jelaskan ke klien |
| Data kehapus | Stop → bilang ke Hermes "balikin lagi" → Undo / Version history |
| 90% beres, 10% muter | Stop, selesaikan manual |

## Scale-up

Mulai dari 10 link → verifikasi cocok → minggu depan naik ke 70 link.
