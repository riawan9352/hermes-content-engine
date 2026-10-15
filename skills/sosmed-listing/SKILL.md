---
name: sosmed-listing
description: Rekap followers, avg monthly views, dan top performing content dari banyak link profil (Threads/Instagram/TikTok) ke sheet "Listing Acc" dalam sekali jalan.
version: 0.1.0
author: BI1MP Academy
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [listing, followers, profile, google-sheets, threads, instagram, tiktok]
    related_skills: [sosmed-reporting]
    requires_toolsets: [browser, file]
---

# Sosmed Listing

Rekap info banyak akun sekaligus: followers, rata-rata views bulanan,
dan konten terbaik — dari link profil yang ada di sheet "Listing Acc".

## When to Use

- Klien/bos nanya: "followers berapa sekarang? avg views-nya? konten
  terbaiknya mana?" untuk banyak akun
- User punya sheet "Listing Acc" berisi link profil, minta kolom lain
  diisi

Don't use for: metrik per post (itu `sosmed-reporting`).

## Prerequisites

- Tab **`Listing Acc`** dengan header:
  `No, Link Profile, Jumlah Followers, Avg Monthly Views, Top Performing Content`
  (panduan: `../../templates/listing-acc-sheet.md`)
- Kolom Link Profile sudah terisi, akses **Editor**
- Chrome terbuka + user klik **Allow** pada popup remote debugging

## Prompt dari User

```
masih dengan spreadsheet yang sama, lihat sheet "Listing Acc".
isi kolom C dan seterusnya sesuai link tertera
```

(Kalau spreadsheet beda, paste link spreadsheet barunya di atas prompt.)

## How to Run

### 1. Rencanakan

1. Buka sheet "Listing Acc" → baca semua Link Profile
2. Klasifikasi per platform (Threads / Instagram / TikTok)
3. Buka tiap profil → baca followers, views, top content
4. Tempel ke sheet
5. Verifikasi sampel random

### 2. Sumber data per platform

| Kolom | Threads | Instagram |
|-------|---------|-----------|
| Jumlah Followers | halaman profil | meta description profil |
| Avg Monthly Views | angka "recent views" 30 hari (mis. 2,8 juta) | tidak tersedia publik |
| Top Performing Content | post likes tertinggi | post likes tertinggi |

- **TikTok**: followers & top content bisa; avg monthly views tidak
  selalu tersedia publik.
- **Instagram**: avg monthly views tidak tersedia dari luar → biarkan
  kosong dan laporkan ke user.

### 3. Verifikasi — wajib

- Sampel minimal 3 profil → cocokkan angka sheet vs halaman profil
- Laporkan hasilnya

## Kalau Data Kehapus

Kejadian nyata: di tengah proses, data sheet bisa terhapus karena salah
klik. Protokol:

1. **Stop** agent
2. Bilang terus terang: *"datanya kamu hapus. balikin lagi. tadi udah
   sempet ter-paste semua"*
3. Biarkan agent memulihkan (biasanya lewat tombol **Undo** di toolbar
   Google Sheets)

Kalau gagal → **File → Version history → restore** versi sebelum job
dimulai. Stop agent dulu sebelum restore.

## Pitfalls

- Followers bisa berubah tiap saat — angka adalah snapshot saat dibaca.
- Jangan menulis melewati baris data (picu "Invalid range").
- Selalu verifikasi manual sebelum kirim ke klien.

## Verification

- [ ] Semua baris profil terisi (kecuali yang memang tidak tersedia
      publik → dijelaskan)
- [ ] Minimal 3 sampel dicocokkan: sheet vs profil → sama
- [ ] Kolom yang kosong dijelaskan ke user
