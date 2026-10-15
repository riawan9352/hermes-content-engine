# Checklist Hari Pertama — Mulai dari Reporting

Urutan berdasarkan Hermes Playbook Bab 7. Jangan langsung setup
semuanya — mulai dari yang paling cepat kerasa hasilnya: **reporting**
(read-only, risiko nol).

## Setup environment

- [ ] Install [Hermes Agent](https://hermes-agent.nousresearch.com)
- [ ] Daftar [DeepSeek Platform](https://platform.deepseek.com) → top up
      $5 → bikin API key (simpan, hanya muncul sekali!)
- [ ] Colok key: Hermes → Settings → Providers → DeepSeek
- [ ] Pilih model: **DeepSeek V4 Flash**, Effort **Medium**
      (untuk reporting)
- [ ] Pasang skill: drag folder `skills/sosmed-reporting` ke chat Hermes
      (atau copy ke folder skills Hermes)
- [ ] Toolset `browser` aktif di Hermes

## Setup sheet (5 menit, manual)

- [ ] Buat Google Sheets baru → rename sheet jadi `Reporting`
- [ ] Isi header:
      `No, Link Posting, Views, Likes, Comments, Reposts, Shares, Screenshots`
- [ ] Isi 10 link post pertama di kolom Link Posting (mulai kecil!)
- [ ] Share → akses **Editor** (bukan Viewer)
- [ ] (Opsional) Duplicate sheet sebagai backup sebelum job pertama

Cara cepat: import `templates/reporting-sheet.csv` via File → Import.

## Job pertama

- [ ] Buka Hermes, kirim **prompt 02** dari `prompts/PROMPT-BANK.md`
      (link sheet + 2 baris instruksi)
- [ ] Klik **Allow** saat pop-up "Allow remote debugging?"
- [ ] Biarkan jendela Chrome tidak diganggu sampai selesai
- [ ] **Verifikasi manual: cek 3 sampel acak** (atas-tengah-bawah),
      cocokkan dengan post aslinya
- [ ] Jika cocok → naikkan ke 70 link minggu depan
- [ ] Jika tidak cocok → perbaiki, jalankan ulang; jangan kirim hasil
      ke klien

## Setelah nyaman (minggu ke-2)

- [ ] Tambah sheet `Listing Acc` → jalankan **prompt 03** (listing
      followers multi-akun), pasang skill `sosmed-listing`
- [ ] Baru pertimbangkan mesin konten (Repliz Premium + prompt 01/04) —
      paling berisiko ke ban, butuh gaya nulis sendiri, bukan copas

## Darurat

- Data kehapus → **prompt 06**: `stop. datanya kamu hapus. balikin lagi...`
- Agent muter-muter di 10% terakhir yang sudah 90% beres → stop,
  lanjutkan manual
- Kacau parah → File → Version history → restore
