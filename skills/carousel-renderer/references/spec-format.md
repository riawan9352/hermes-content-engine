# Format Spec Carousel (JSON)

Spec adalah file JSON berisi daftar carousel + teks per slide.
Renderer membaca spec → bikin HTML per slide → screenshot PNG 1080×1350.

## Struktur

```json
{
  "carousels": [
    {
      "id": "01",                      // nomor/ID carousel
      "title": "Judul Carousel",
      "theme": "gadget-masa-depan",    // lihat theme-specs.md
      "source_credit": "Sumber: nama + link",  // muncul di slide terakhir
      "slides": [
        {
          "num": 1,                    // nomor slide (badge 1/7, dst)
          "headline": "Teks utama",
          "subline": "Teks pendukung (opsional, boleh kosong)",
          "caption_box": "Teks box bawah (opsional)",
          "character": "kakek-penemu-open"   // variasi karakter (opsional)
        }
      ]
    }
  ]
}
```

## Field

| Field | Wajib | Catatan |
|-------|-------|---------|
| `id` | ya | unik per carousel |
| `title` | ya | judul internal |
| `theme` | ya | id tema — daftar di `theme-specs.md` |
| `source_credit` | tidak | tampil kecil di slide terakhir |
| `slides[].num` | ya | 1..N, menentukan badge |
| `slides[].headline` | ya | teks besar |
| `slides[].subline` | tidak | teks kecil di bawah headline |
| `slides[].caption_box` | tidak | box caption bawah |

## Encoding

Simpan sebagai **UTF-8** (boleh UTF-8 with BOM — script memakai
`utf-8-sig`). Hindari emoji/karakter unicode aneh di script, karena
console Windows memakai cp1252.

## Contoh lengkap

`../templates/example-carousel-spec.json`
