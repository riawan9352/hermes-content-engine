# Template Sheet: Listing Acc

## Cara buat (2 menit)

1. Pakai **spreadsheet yang sama** dengan Reporting (tab baru), atau
   spreadsheet baru.
2. Buat tab baru bernama **`Listing Acc`**.
3. **Cara cepat:** File → Import → Upload → `listing-acc-sheet.csv`.
   **Cara manual:** ketik header di baris 1:

   ```
   No | Link Profile | Jumlah Followers | Avg Monthly Views | Top Performing Content
   ```

4. Isi kolom **Link Profile** dengan link profil akun (campur Threads,
   Instagram, TikTok). Kolom lain biarkan kosong.
5. Pastikan akses **Editor**.

## Prompt

```
masih dengan spreadsheet yang sama, lihat sheet "Listing Acc".
isi kolom C dan seterusnya sesuai link tertera
```

(Kalau spreadsheet beda, paste link spreadsheet barunya di atas prompt ini.)

## Yang diisi otomatis

| Kolom | Threads | Instagram |
|-------|---------|-----------|
| Jumlah Followers | dari halaman profil | dari meta description profil |
| Avg Monthly Views | angka "recent views" 30 hari di profil | tidak tersedia publik |
| Top Performing Content | post likes tertinggi | post likes tertinggi |

Detail teknis: `../skills/sosmed-listing/SKILL.md`
