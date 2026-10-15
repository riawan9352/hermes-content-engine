# Prompt Bank — Hermes Content Engine

Semua prompt dalam urutan pemakaian. Ganti yang di dalam `[kurung siku]`.

Urutan eksekusi: **02 (reporting) dulu → 03 (listing) → 01/04/05/07
(mesin konten)** sesuai anjuran playbook.

---

## 01 · Setup Mesin Konten (butuh akun Repliz)

```
1. Credential:
access key: [paste]
secret key: [paste]
user ID: [paste]
account ID: [paste]

2. Volume posting: default (12 per hari di Threads, 5 per hari carousel IG)
A. Persona: [siapa lo, umur, konteks hidup, atau "default"]
B. Gaya penulisan: [paste 5-10 contoh post viral, atau "default"]
```

> Credential dari Repliz: access/secret key di Setting → Public API;
> User ID di Account Integration → pilih akun; Account ID di Setting →
> Public API → endpoint account.
>
> **Keamanan:** credential = kunci dompet & akun. Jangan share ke grup,
> jangan muncul di screenshot.

---

## 02 · Reporting (jalankan ini dulu)

```
[paste link Google Sheets]
lihat ke sheet "Reporting"
langsung isi semua views dan engagement sesuai link tertera
```

Prasyarat: sheet `Reporting` terisi kolom Link Posting, akses **Editor**,
skill `sosmed-reporting` terpasang. Klik **Allow** saat popup remote
debugging muncul.

---

## 03 · Listing Akun

```
masih dengan spreadsheet yang sama, lihat sheet "Listing Acc".
isi kolom C dan seterusnya sesuai link tertera
```

Kalau spreadsheet beda, paste link barunya di atas prompt ini.
Struktur sheet: `../templates/listing-acc-sheet.md`.

---

## 04 · Posting Harian (butuh Repliz)

```
1. aku mau buat postingan tentang [topik]
2. posting di threads di jam [jam1], [jam2], [jam3], [jam4]
3. posting di instagram di jam [maks. 3 jam dari sekarang]
4. semua terposted hari ini
```

**Aturan IG:** carousel maksimal dijadwal **3 jam dari waktu prompt**
(tidak bisa untuk besok). Post Threads bebas aturan ini.

---

## 05 · Ganti Gaya Nulis

```
ganti gaya penulisan sesuai format yang aku mau.
Ini referensinya: [paste 5-10 post]
```

---

## 06 · Kalau Data Kehapus (darurat)

```
stop.
datanya kamu hapus. balikin lagi. tadi udah sempet ter-paste semua
```

Kalau agent tidak bisa memulihkan: **File → Version history → restore**
ke versi sebelum job dimulai. Stop agent dulu sebelum memulihkan.

---

## 07 · Draft Harian dari Content Queue (tanpa Repliz)

```
buka [link Google Sheets content queue]
ambil [3] baris berstatus "draft" atau (kalo kosong) pilih dari "ide"
tulis draftnya sesuai brand voice & template yang berlaku
jangan posting — kasih draftnya ke aku buat review
```

Output: draft siap review di chat. Setelah kamu posting manual, isi
kolom `Link Post` + `Status = posted` di queue, lalu jalankan prompt 02
(reporting) untuk mengisi metriknya.

---

## Aturan pemakaian

- Jangan tempel credential/API key di tempat lain selain form resmi
  provider.
- Verifikasi manual tetap wajib di akhir tiap job reporting
  (minimal 3 sampel acak).
- Reporting & listing tidak butuh Repliz; mesin konten (01, 04) butuh
  akun Repliz Premium.
