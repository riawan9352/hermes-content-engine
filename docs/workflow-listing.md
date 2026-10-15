# Workflow: Listing Akun

Rekap followers & konten terbaik banyak akun (12 akun sekali jalan).
Jalankan setelah reporting nyaman.

## Prasyarat

- [ ] Reporting (workflow sebelumnya) sudah jalan
- [ ] Skill `sosmed-listing` terpasang
- [ ] Tab **`Listing Acc`** di spreadsheet yang sama
      (panduan: `../templates/listing-acc-sheet.md`)
- [ ] Kolom Link Profile terisi, akses Editor

## Langkah

### 1. Buat tab Listing Acc

Header:
`No, Link Profile, Jumlah Followers, Avg Monthly Views, Top Performing Content`
— isi Link Profile saja.

### 2. Kirim prompt (di session yang sama)

```
masih dengan spreadsheet yang sama, lihat sheet "Listing Acc".
isi kolom C dan seterusnya sesuai link tertera
```

### 3. Allow + lepas tangan

Klik **Allow** pada popup remote debugging. Biarkan Chrome.

### 4. Verifikasi

Cek sampel minimal 3 profil: sheet vs halaman profil → harus sama.

## Kalau data kehapus

Stop → bilang *"datanya kamu hapus. balikin lagi"* → biarkan agent
Undo. Gagal? Version history → restore.

## Catatan

- Avg monthly views Instagram tidak tersedia publik → jelaskan.
- Angka followers = snapshot, bisa berubah tiap saat.
