Log-to-Playbook
Ringkasan
log-to-playbook adalah tool open-source untuk mengubah error log, stack trace, output terminal, atau pesan gagal deploy menjadi checklist diagnosis yang jelas.

Tujuan utamanya bukan menggantikan engineer, tetapi mempercepat langkah awal saat seseorang bingung membaca error.

Contoh sederhana:

Input:
SQLSTATE[HY000]: General error: 1364 Field 'name' doesn't have a default value

Output:
- Kemungkinan penyebab: field required tidak dikirim ke database.
- Cek payload request.
- Cek fillable model.
- Cek migration/default value.
- Jalankan ulang test.
Tool ini bisa berjalan tanpa AI menggunakan pattern-based playbook, dan bisa ditingkatkan dengan AI untuk penjelasan yang lebih natural.

Masalah Yang Diselesaikan
Banyak developer, sysadmin, mahasiswa, dan tim support sering menghadapi error seperti:

Laravel queue failed
Docker container crash
Nginx 502
MySQL field/default error
Node package conflict
Python dependency error
Disk penuh
Permission denied
SSL/certbot gagal
Masalahnya, error log sering panjang dan tidak langsung memberi tahu langkah diagnosis yang aman.

log-to-playbook membantu mengubah log menjadi:

ringkasan masalah
kemungkinan penyebab
checklist diagnosis
command yang bisa dijalankan
tingkat risiko
referensi playbook
Target Pengguna
Developer junior yang belum terbiasa membaca stack trace.
Developer solo yang sering deploy sendiri.
Sysadmin yang ingin diagnosis cepat dari log server.
Tim support teknis yang perlu jawaban standar.
Mahasiswa yang sedang belajar debugging.
AI coding agent yang butuh konteks diagnosis lebih terstruktur.
Prinsip Produk
Local-first: log tidak perlu dikirim ke server.
Pattern-first: fitur dasar tetap jalan tanpa AI.
AI-optional: AI hanya menambah penjelasan dan generalisasi.
Safe by default: jangan langsung menyarankan destructive command.
Reusable: setiap diagnosis bisa disimpan menjadi playbook.
Transparent: user bisa melihat pattern mana yang cocok.
Core Flow
User paste log
  -> tool normalisasi teks
  -> tool cocokkan pattern
  -> pilih playbook paling relevan
  -> tampilkan ringkasan dan checklist
  -> user jalankan diagnosis
  -> user bisa simpan hasil sebagai report
Mode Penggunaan
1. CLI Mode
log2playbook analyze error.log
Output:

Detected: Laravel database insert error
Confidence: 0.91
Risk: Low

Likely cause:
Required database field has no value and no default.

Checklist:
1. Inspect request payload.
2. Check model fillable/guarded properties.
3. Check migration for nullable/default value.
4. Re-run failing job or test.
2. Web Mode
User membuka web lokal:

log2playbook serve
Lalu paste log di browser.

Fitur web:

paste log
upload file log
lihat hasil diagnosis
copy checklist
export Markdown
simpan playbook baru
3. GitHub Action Mode
Untuk CI/CD:

name: Analyze Failure Logs

on:
  workflow_run:
    workflows: ["Test"]
    types:
      - completed

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: log-to-playbook/action@v1
        with:
          log-path: ./logs/test-output.log
Output bisa menjadi komentar PR:

Possible cause:
Test failed because database migration is missing.

Suggested next steps:
1. Run migration locally.
2. Check test database setup.
3. Verify CI env variables.
MVP
MVP cukup fokus pada 5 kategori error:

Laravel/PHP
Docker
Node.js/npm
Python/pip
Linux server basics
Fitur MVP:

CLI analyze file/stdin
30 sampai 50 built-in playbooks
output text dan Markdown
confidence score
risk label
command suggestion
redact secret sederhana
optional AI explain mode
Contoh Input dan Output
Contoh 1: Docker Port Conflict
Input:

Error starting userland proxy: listen tcp4 0.0.0.0:80: bind: address already in use
Output:

## Diagnosis

Docker gagal start karena port 80 sudah digunakan proses lain.

## Kemungkinan Penyebab

- Nginx/Apache sudah berjalan di host.
- Container lain sudah memakai port 80.
- Service lama belum berhenti.

## Checklist

1. Cek proses yang memakai port:
   `sudo lsof -i :80`
2. Cek container aktif:
   `docker ps`
3. Jika port dipakai container lain, ubah mapping port.
4. Jika port dipakai web server host, hentikan service atau pakai port lain.

## Risiko

Medium. Menghentikan service host dapat memutus trafik production.
Contoh 2: Laravel Queue Failed
Input:

Illuminate\Queue\MaxAttemptsExceededException: App\Jobs\GenerateReport has been attempted too many times
Output:

## Diagnosis

Job Laravel gagal berulang kali sampai melewati batas percobaan.

## Kemungkinan Penyebab

- Logic job error.
- Dependency eksternal timeout.
- Payload queue tidak valid.
- Worker memakai konfigurasi lama.

## Checklist

1. Jalankan `php artisan queue:failed`.
2. Inspect payload job yang gagal.
3. Buka stack trace exception pertama.
4. Cek `.env` queue connection.
5. Restart worker setelah deploy:
   `php artisan queue:restart`
6. Retry job setelah penyebab diperbaiki.

## Risiko

Low untuk diagnosis. Medium untuk retry massal karena bisa memproses ulang data.
Contoh 3: Python Dependency Error
Input:

ModuleNotFoundError: No module named 'pandas'
Output:

## Diagnosis

Runtime Python tidak menemukan package `pandas`.

## Kemungkinan Penyebab

- Package belum di-install.
- Virtual environment salah.
- Dependency tidak masuk `requirements.txt`.
- Script dijalankan dengan Python interpreter berbeda.

## Checklist

1. Cek interpreter:
   `which python`
2. Cek environment aktif:
   `python -m pip list`
3. Install dependency:
   `python -m pip install pandas`
4. Simpan dependency:
   `python -m pip freeze > requirements.txt`
5. Jalankan ulang script.

## Risiko

Low.
Playbook Format
Setiap playbook ditulis sebagai YAML agar mudah ditambah contributor.

id: docker-port-conflict
title: Docker port conflict
category: docker
severity: medium
risk: medium

patterns:
  - "bind: address already in use"
  - "port is already allocated"
  - "Error starting userland proxy"

summary: >
  Docker gagal start karena port host sudah digunakan proses lain.

causes:
  - Web server host sudah memakai port.
  - Container lain memakai port yang sama.
  - Service lama belum berhenti.

checks:
  - label: Cek proses pemakai port
    command: "sudo lsof -i :80"
    risk: low
  - label: Cek container aktif
    command: "docker ps"
    risk: low
  - label: Ubah port mapping jika konflik
    command: "docker run -p 8080:80 image-name"
    risk: low

avoid:
  - "Jangan kill proses production sebelum tahu service apa yang memakai port."
  - "Jangan mengubah firewall sebagai langkah pertama."

references:
  - "https://docs.docker.com/"
Arsitektur Teknis
packages/
  core/
    matcher
    normalizer
    scorer
    redactor
    renderer

  cli/
    analyze command
    export command

  web/
    local web UI

playbooks/
  docker/
  laravel/
  node/
  python/
  linux/

examples/
  logs/
  reports/
Matching Logic
Versi awal:

score = pattern_match_score
      + keyword_score
      + category_hint_score
      - ambiguity_penalty
Contoh:

exact phrase match: +50
regex match: +30
keyword match: +10
multiple categories matched: -10
AI Mode
AI tidak wajib. Jika user punya API key, AI bisa dipakai untuk:

menjelaskan error dengan bahasa sederhana
menambahkan kemungkinan penyebab
mengubah report menjadi Bahasa Indonesia atau Inggris
membuat playbook baru dari log yang belum dikenal
menyarankan command diagnosis
AI mode harus tetap dibatasi:

command destructive diberi warning
secret harus di-redact sebelum dikirim
output AI harus ditandai sebagai suggestion
user tetap melihat playbook pattern yang dipakai
Contoh:

log2playbook analyze error.log --ai
Redaction
Sebelum log dianalisis atau dikirim ke AI, tool harus menyamarkan:

API key
token
password
private key
database URL
email jika user memilih privacy mode
Contoh:

OPENAI_API_KEY=sk-abc123
Menjadi:

OPENAI_API_KEY=[REDACTED]
Output Format
Output Markdown:

# Log Diagnosis Report

## Summary

...

## Detected Pattern

...

## Likely Causes

...

## Checklist

...

## Commands

...

## Risk Notes

...
Output JSON:

{
  "detected": "docker-port-conflict",
  "confidence": 0.92,
  "risk": "medium",
  "summary": "Docker failed because port 80 is already in use.",
  "checks": [
    {
      "label": "Check process using port",
      "command": "sudo lsof -i :80",
      "risk": "low"
    }
  ]
}
Roadmap
Phase 1: CLI MVP
Core matcher
YAML playbook loader
Markdown renderer
50 initial playbooks
redact secrets
examples
Phase 2: Web UI
Paste log
Upload log
Export report
Filter by category
Save custom playbook
Phase 3: AI Assist
AI explanation
AI-generated draft playbook
AI translation
AI summarization for long logs
Phase 4: Integrations
GitHub Action
Docker image
VS Code extension
Slack/Discord bot
CI failure comment
Repository Positioning
Short description:

Turn logs and stack traces into practical debugging playbooks.
README headline:

Paste an error. Get a checklist.
Value proposition:

Debug faster with local-first, reusable, pattern-based playbooks.
AI optional. Secrets redacted. Markdown-ready.
Acceptance Criteria
MVP dianggap berhasil jika:

user bisa menjalankan CLI dari terminal
minimal 50 error umum bisa dikenali
output diagnosis dapat diekspor sebagai Markdown
secret dasar bisa di-redact
contributor bisa menambah playbook YAML tanpa mengubah core code
tool tetap berguna tanpa AI
Contoh Command
log2playbook analyze ./error.log
log2playbook analyze ./error.log --format markdown
log2playbook analyze ./error.log --category docker
log2playbook analyze ./error.log --ai
log2playbook new-playbook
log2playbook validate-playbooks
Risiko Produk
Playbook bisa terlalu generik.

Solusi: tampilkan confidence dan matched pattern.
User bisa menjalankan command berbahaya.

Solusi: risk label dan warning untuk destructive command.
AI bisa hallucinate.

Solusi: AI hanya sebagai explanation layer, bukan sumber kebenaran utama.
Log bisa mengandung secret.

Solusi: redaction wajib sebelum AI mode.
Terlalu banyak kategori sejak awal.

Solusi: mulai dari 5 kategori populer.
Nama Alternatif
log-to-playbook
log2playbook
error-to-checklist
stacktrace-helper
debug-playbooks
paste-error
Kesimpulan
log-to-playbook cocok menjadi repo open-source yang membantu banyak orang karena masalahnya universal: semua developer pernah bingung membaca error.

Versi awal mudah dibuat karena cukup menggunakan pattern matching dan YAML playbook. AI bisa ditambahkan belakangan sebagai fitur peningkatan, bukan fondasi utama.
