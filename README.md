# Hermes Content Engine

Paket skill, prompt, template, dan script untuk otomasi konten sosmed
(Threads & Instagram) memakai **Hermes Agent** — reporting otomatis,
listing akun, dan render carousel.

> Workflow terinspirasi dari praktik di *Hermes Playbook* (AI for
> Productivity ID). Ebook asli tidak disertakan — repo ini hanya berisi
> implementasi skill/prompt/script-nya sendiri.

## Isi Repo

| Folder | Isi |
|--------|-----|
| `skills/sosmed-reporting/` | Skill: isi views/likes/comments/reposts/shares ke Google Sheets otomatis |
| `skills/sosmed-listing/` | Skill: rekap followers & top content banyak akun sekali jalan |
| `skills/carousel-renderer/` | Skill: render spec JSON → PNG 1080×1350 (+ animasi GIF/MP4) |
| `prompts/PROMPT-BANK.md` | 6 prompt siap pakai (setup, posting, reporting, listing, undo) |
| `templates/` | Struktur sheet Google Sheets untuk Reporting & Listing Acc |
| `docs/` | Panduan setup + step-by-step tiap workflow |
| `checklists/` | Checklist hari pertama |

## Instalasi

1. Install [Hermes Agent](https://hermes-agent.nousresearch.com).
2. Siapkan **DeepSeek API key** (top up $5 cukup) → paste di
   Hermes → Settings → Providers → DeepSeek.
3. Copy folder skill yang dibutuhkan ke folder skills Hermes, **atau**
   drag folder skill-nya langsung ke kolom chat Hermes.

```bash
# contoh: install skill reporting
cp -r skills/sosmed-reporting ~/.hermes/skills/
```

4. Ikuti panduan di `docs/` sesuai workflow yang mau dijalankan.

## Urutan Mulai (sesuai playbook)

1. **Reporting dulu** → `docs/workflow-reporting.md` (paling cepat kerasa hasil)
2. **Listing akun** → `docs/workflow-listing.md`
3. **Mesin konten** → `docs/workflow-content.md` (butuh akun Repliz)

## Keamanan

- API key & credential **tidak boleh** masuk repo. Pakai `.env` (sudah
  di-gitignore) atau paste langsung ke chat Hermes (jangan di-commit).
- Jangan screenshot/sbagikan API key DeepSeek & credential Repliz.

## License

MIT — lihat `LICENSE`.
