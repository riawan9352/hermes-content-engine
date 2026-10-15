---
name: sosmed-reporting
description: Isi views, likes, comments, reposts, dan shares dari link post Threads/TikTok/Instagram ke Google Sheets "Reporting" secara otomatis, lengkap dengan screenshot bukti dan verifikasi sel per sel.
version: 0.1.0
author: BI1MP Academy
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [reporting, engagement, google-sheets, threads, tiktok, instagram, automation]
    related_skills: [carousel-renderer, sosmed-listing]
    requires_toolsets: [browser, file, terminal]
---

# Sosmed Reporting

Buka tiap link post di browser, baca angka views & engagement-nya, lalu
tempel ke Google Sheets tab "Reporting" — termasuk screenshot bukti per
link. Tanpa ketik angka manual.

## When to Use

- User kasih link Google Sheets + bilang "lihat ke sheet Reporting, isi
  views dan engagement sesuai link tertera"
- Laporan mingguan/bulanan berisi puluhan link post

Don't use for: bikin konten, posting, atau rekap followers profil
(pakai `sosmed-listing`).

## Prerequisites

- Google Sheet punya tab **"Reporting"** dengan struktur di
  `references/sheet-structure.md`
- Akses sheet **Editor** (bukan Viewer — kalau Viewer, tidak bisa menulis)
- Kolom **Link Posting** sudah terisi, kolom lain kosong
- Chrome terbuka + user klik **Allow** pada popup
  "Allow remote debugging?" saat diminta

## Prompt dari User

Cukup satu blok seperti ini:

```
[paste link Google Sheets]
lihat ke sheet "Reporting"
langsung isi semua views dan engagement sesuai link tertera
```

## How to Run

### 1. Rencanakan kerja (task list)

Susun 5 langkah, kira-kira:

1. Buka sheet "Reporting" → baca semua link di kolom Link Posting
2. Klasifikasi tiap link per platform (Threads / TikTok / Instagram)
3. Buka tiap link di browser, baca views + engagement
4. Tempel angka & screenshot ke sheet
5. Verifikasi sampel random (atas–tengah–bawah)

### 2. Kerja per batch

- Pecah link jadi batch **1–20 link** supaya stabil
- Link redirect (mis. format share Threads) → buka dulu ke halaman post
  aslinya, baru baca angkanya
- Sambil jalan, ambil **screenshot bukti** tiap post → simpan di kolom
  Screenshots

### 3. Isi sheet

Kolom yang diisi per link (lihat `references/sheet-structure.md`):

| Kolom | Sumber |
|-------|--------|
| Views | angka views di post |
| Likes | angka likes |
| Comments | angka comments |
| Reposts | angka reposts (Threads) |
| Shares | angka shares |
| Screenshot | screenshot bukti dari post |

### 4. Verifikasi — wajib

Sebelum bilang selesai:

- Ambil **minimal 3 sampel random**: atas, tengah, bawah sheet
- Buka lagi link-nya, cocokkan angka di sheet vs angka di platform
- Laporkan hasil cocok/tidak ke user

## Batasan Platform (bukan error!)

| Platform | Yang tidak terlihat dari luar | Solusi |
|----------|------------------------------|--------|
| Instagram | Views & shares | Connect akun via Repliz (akun sendiri saja) |
| TikTok | Reposts | Tidak bisa dari luar |
| TikTok | — (opsional) | Tambah kolom `Saved` kalau mau ambil jumlah save |

Kosong = memang tidak terlihat publik, **bukan gagal**.

## Error Handling

- Error seperti *"Invalid range. The range you specified exceeds the
  sheet size"* **normal** — itu Hermes baru belajar struktur sheet.
  Coba strategi lain (baca header dulu, atau seleksi per blok) lalu lanjut.
- Cursor bergerak sendiri mencari tombol = bagian dari eksplorasi. Biarkan.
- Kalau data di sheet terhapus di tengah jalan:
  1. **Stop** dulu
  2. Bilang terus terang ke user: *"datanya kamu hapus. balikin lagi."*
  3. Pakai **Undo** (Ctrl+Z / tombol Undo di toolbar Google Sheets),
     atau **Version history** → restore versi sebelumnya
- Kalau sudah 90% beres tapi muter-muter di sisa 10% → stop, lanjutkan
  manual. Lebih cepat daripada dari nol.

## Pitfalls

- Kolom header di sheet harus persis sesuai template — kalau header
  salah, tanya user dulu sebelum menulis.
- Jangan menulis ke baris kosong di bawah data (bikin "Invalid range").
- Selalu pastikan akses **Editor**, bukan Viewer.
- Jangan menutup/mengganggu jendela Chrome selama Hermes bekerja.

## Verification

- [ ] Semua baris berisi link terisi angkanya (kecuali yang memang tidak
      terlihat publik)
- [ ] Screenshot bukti terpasang di kolom Screenshots
- [ ] Minimal 3 sampel dicek ulang: sheet vs platform → cocok
- [ ] Kolom kosong dijelaskan (bukan error)
