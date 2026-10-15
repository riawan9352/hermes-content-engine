# Setup: Hermes + DeepSeek (15 Menit)

Fondasi semua workflow. Sekali beres, tinggal pake.

## 1. Install Hermes Agent

Buka [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com),
klik Install, pilih sesuai OS (Desktop App macOS/Windows, atau terminal
untuk Linux).

## 2. Bikin akun DeepSeek Platform + top up

1. Buka [platform.deepseek.com](https://platform.deepseek.com)
   — **bukan** versi chat gratisnya.
2. Login → menu **Top up** → isi saldo.
   - **$5 cukup** untuk mulai (~Rp100rb, ≈ 1 bulan menurut praktisi)
   - Mau coba dulu? $2 juga bisa
3. Bayar via PayPal, kartu debit/kredit, atau Google Pay.

## 3. Generate API key

Menu **API keys** → **Create new API key** → beri nama (mis. "hermes")
→ Create → **langsung copy**.

> ⚠️ Key hanya keliatan sekali. Simpan aman. Jangan share, jangan
> muncul di screenshot/post — siapa pun yang pegang key bisa ngabisin
> saldo lo.

## 4. Colok DeepSeek ke Hermes

Hermes → **Settings → Providers → API keys** → cari **DeepSeek** →
paste key → Save.

## 5. Pilih model & level thinking

Di kolom chat, klik nama model → **Refresh Models** → pilih model →
set **Effort**:

| Mau ngapain | Model | Effort | Kenapa |
|-------------|-------|--------|--------|
| Setup & reporting | V4 Flash | Medium | paling murah, reporting ga butuh mikir berat |
| Konten harian | V4 Flash | Max/Ultra | masih murah, reasoning lebih bagus |
| Konten kualitas tinggi | V4 Pro | Max | hasil paling bagus, token paling mahal |

> Provider lain (OpenRouter, Anthropic, xAI, dll) juga bisa — playbook
> pakai DeepSeek karena murah + reasoning cukup.

## Selesai?

Kalau layar Hermes udah siap session baru, setup beres. Lanjut ke
`workflow-reporting.md`.
