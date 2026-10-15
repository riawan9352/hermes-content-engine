# Workflow: Mesin Konten (Threads & Carousel IG)

Nulis, render, dan jadwalin post otomatis. Default: **12 post Threads +
5 carousel IG per hari**. Jalankan **terakhir** — setelah reporting &
listing nyaman.

> Estimasi: ±Rp1.200/hari token DeepSeek untuk ~10 thread + 5 carousel.
> Setup awal 2–3 menit.

## Prasyarat

- [ ] Hermes + DeepSeek jalan (`setup.md`)
- [ ] Akun **Repliz Premium** (1 bulan cukup untuk mulai)
- [ ] Akun Threads/IG terintegrasi di Repliz
- [ ] Skill `carousel-renderer` terpasang (untuk render slide)
- [ ] File workflow autopilot (opsional, dari playbook) — atau mulai
      manual dengan prompt 04

## Langkah

### 1. Repliz: daftar, upgrade, connect akun

1. Buka [repliz.com](https://repliz.com) → daftar → upgrade **Premium**
2. **Account Integration** → connect akun (mulai dari Threads + IG)
3. Setelah integrasi, **allow akses dari Hermes** juga — kalau tidak,
   upload tetap gagal walau credential benar

### 2. Kumpulin 4 credential

| Credential | Tempat di Repliz |
|------------|------------------|
| Access key | Setting → Public API |
| Secret key | Setting → Public API |
| User ID | Account Integration → pilih akun → copy ID |
| Account ID | Setting → Public API → buka endpoint account → copy |

### 3. Setup di Hermes

Drag file workflow autopilot ke chat Hermes (kalau ada), lalu kirim
**prompt 01** dari `prompts/PROMPT-BANK.md` (credential + volume +
persona + gaya nulis). Tunggu install 2–3 menit, klik **Run** kalau
diminta.

### 4. Prompt harian — cuma 4 baris

```
1. aku mau buat postingan tentang [topik]
2. posting di threads di jam [jam1], [jam2], [jam3], [jam4]
3. posting di instagram di jam [maks. 3 jam dari sekarang]
4. semua terposted hari ini
```

Cek hasil di Repliz → **Schedule Content**.

## Aturan main

| Aturan | Detail |
|--------|--------|
| Batas 3 jam carousel IG | Upload carousel hanya bisa dijadwal **maks 3 jam dari prompt**. Prompt 11.00 → slot terakhir 14.00. Tidak bisa untuk besok. Post Threads bebas. |
| 10 slide per carousel | Best practice |
| Caption 2.100–2.200 karakter | Default; caption kaya keyword dapat boost |
| Render lokal | Slide dirender lokal (Python) → upload via API Repliz |
| Session pertama lebih lama | Normal |

## Quality control

- Kalau hasil kurang tajam → naik effort (V4 Flash Ultra), atau V4 Pro
  Max untuk kualitas tertinggi
- Pantau biaya: platform.deepseek.com → Usage
- **Gaya boleh dicontek, isi harus original** — copas mentah bikin
  akun ke-flag. Volume 12/hari itu besar.

## Alternatif: n8n

Kalau volume udah puluhan akun dan butuh jalan di server 24/7 → n8n.
Hermes lebih cepat buat mulai & kontrol via chat biasa.
