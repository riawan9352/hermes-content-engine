---
name: carousel-renderer
description: Render carousel slides (HTML) to PNG 1080×1350 via Chrome headless. Reusable untuk semua batch carousel.
version: 0.1.0
author: BI1MP Academy
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [carousel, render, html, png, content, design]
    related_skills: [sosmed-reporting]
    requires_toolsets: [terminal, file]
---

# Carousel Renderer

Render file spesifikasi JSON → HTML per slide → screenshot PNG 1080×1350 via Chrome headless. Output terorganisir per folder carousel.

## When to Use

- User punya spec carousel (JSON) dan minta di-render jadi gambar PNG
- Batch render 6+ carousel sekaligus
- Regenerate slide setelah edit teks/layout

Don't use for: animasi/video, editing gambar existin, posting ke platform (itu urusan skill lain).

## Prerequisites

- Google Chrome atau Microsoft Edge terinstall (minimal salah satu)
- Python 3.10+ di PATH
- ffmpeg di PATH (hanya untuk mode animated/rigged: GIF + MP4)

## How to Run

### 1. Siapkan spec JSON

Format spec ada di `references/spec-format.md`. Minimal:

```json
{
  "carousels": [
    {
      "id": "01",
      "title": "Judul Carousel",
      "theme": "garis-jelas",
      "source_credit": "Sumber: nama + link",
      "slides": [
        {
          "num": 1,
          "headline": "Teks utama slide",
          "subline": "Teks pendukung (opsional)",
          "caption_box": "Teks caption box bawah (opsional)",
          "character": "kakek-penemu-open"
        }
      ]
    }
  ]
}
```

### 2. Jalankan render

**Statis (PNG):**

```bash
python skills/carousel-renderer/scripts/render_carousel.py spec.json --outdir output/
```

**Animated sederhana (GIF + MP4 — float, bob, pulse):**

```bash
python skills/carousel-renderer/scripts/render_animated.py spec.json --outdir output/
```

**Rigged (karakter puppet dengan ekspresi & pose per slide — butuh choreography):**

```bash
python skills/carousel-renderer/scripts/render_rigged.py spec.json --outdir output/ --slides 1,2,7
```

Animated/rigged butuh **ffmpeg** di PATH. Parameter: 2 detik loop, 10 fps
(20 frame), output `slide-XX.gif` + `slide-XX.mp4`.

### 3. Verifikasi output

Cek folder `output/` — tiap carousel punya subfolder sendiri berisi `slide-01.png` … `slide-07.png` (dan `.gif`/`.mp4` untuk mode animated).

## Tema Visual yang Tersedia

Lihat `references/theme-specs.md` untuk detail warna, font, dan karakter per tema.

| ID Tema | Gaya | Cocok untuk |
|---------|------|-------------|
| `gadget-masa-depan` | membulat, pastel | AI sebagai alat ajaib |
| `bengkel-diagnostik` | teknis, HUD | data/diagnostik |
| `garis-jelas` | komik klasik | penjelasan umum |
| `kantor-kacau` | komedi situasional | kesalahan, humor |
| `latihan-suci` | bold, training | belajar, progres |
| `malam-art-deco` | noir, dramatis | fakta serius, data |

## Pitfalls

- Chrome headless butuh waktu ~1-2 detik per slide. 42 slide ≈ 1-2 menit.
- Kalau PNG hitam kosong: cek apakah Chrome ada di `--chrome PATH` atau di PATH sistem.
- Font display bergantung font sistem — kalau hasil beda, install font dulu atau ganti ke font web-safe.

## Verification

- [ ] Semua slide PNG ada di folder yang benar
- [ ] Dimensi tepat 1080×1350 px
- [ ] Teks terbaca jelas, tidak terpotong
- [ ] Palet warna sesuai tema
- [ ] Badge nomor slide benar (1/7 … 7/7)
- [ ] Source credit muncul di slide terakhir (kalau diisi)
