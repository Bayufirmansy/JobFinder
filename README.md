# 🔍 JobFinder — Search Engine Loker Berbasis Web Crawler
> Dokumentasi lengkap dari nol sampai jalan — Mata Kuliah Temu Kembali Informasi

---

## 📌 Daftar Isi
1. [Gambaran Proyek](#gambaran-proyek)
2. [Kenapa Scraping di Indonesia Susah?](#kenapa-scraping-di-indonesia-susah)
3. [Konsep Dasar yang Harus Dipahami](#konsep-dasar)
4. [Arsitektur Sistem](#arsitektur-sistem)
5. [Struktur File](#struktur-file)
6. [Penjelasan Tiap File](#penjelasan-tiap-file)
7. [Alur Data](#alur-data)
8. [Evaluasi IR](#evaluasi-ir)
9. [Cara Menjalankan](#cara-menjalankan)
10. [Pelajaran & Refleksi](#pelajaran--refleksi)

---

## Gambaran Proyek

JobFinder adalah search engine sederhana yang:
- Mengambil data loker dari internet secara otomatis
- Mengindeks data menggunakan teknik Information Retrieval
- Menampilkan hasil pencarian yang relevan dengan ranking BM25/TF-IDF
- Bisa diakses lewat browser tanpa perlu install apapun

**Stack:**
```
Python → Requests/BeautifulSoup → SQLite/JSON → TF-IDF/BM25 → Streamlit
```

---

## Kenapa Scraping di Indonesia Susah?

Ini pelajaran paling penting dari proyek ini. Hampir semua situs loker Indonesia **aktif memblokir bot**. Berikut penjelasan teknisnya:

---

### 1. Cloudflare Protection 🛡️

**Apa itu Cloudflare?**
Cloudflare adalah layanan keamanan yang dipasang di depan server website. Tugasnya menyaring request yang masuk — mana dari manusia, mana dari bot.

**Cara kerjanya:**
```
Kamu (requests.get) → Cloudflare → Website
                          ↓
                    "Hmm, ini bot atau manusia?"
                          ↓
              Cek: User-Agent, IP, Cookies, JS Challenge
                          ↓
                    Bot? → Blokir (403/Challenge)
                    Manusia? → Lolos
```

**Kenapa requests.get gagal?**
Library `requests` hanya mengirim HTTP request biasa — tidak bisa menjalankan JavaScript, tidak punya cookies seperti browser asli. Cloudflare langsung tahu ini bot.

**Situs Indonesia yang pakai Cloudflare:**
- Loker.id ❌
- Glints.com ❌  
- Jobstreet.co.id ❌
- Indeed.co.id ❌

**Solusinya:**
- Pakai Selenium (simulasi browser asli)
- Pakai Playwright (lebih modern dari Selenium)
- Pakai API resmi kalau tersedia
- Cari sumber data alternatif

---

### 2. JavaScript Rendering ⚡

**Masalah:**
Banyak website modern pakai React/Vue/Angular — datanya tidak ada di HTML awal, tapi dimuat oleh JavaScript setelah halaman terbuka.

**Contoh nyata:**
```
Yang dikirim server:          Yang kamu lihat di browser:
<div id="app"></div>    →     <div id="app">
                                <div class="job-card">
                                  Frontend Engineer
                                </div>
                              </div>
```

BeautifulSoup hanya bisa baca HTML dari server — bukan hasil render JavaScript. Makanya hasilnya kosong atau tidak ada data loker.

**Situs yang pakai JS rendering:**
- Kalibrr.com ❌ (React)
- Ekrut.com ❌ (React)
- Jobplanet (sebagian) ⚠️

**Solusinya:**
```python
# Pakai Selenium
from selenium import webdriver
driver = webdriver.Chrome()
driver.get("https://kalibrr.com/jobs")
html = driver.page_source  # HTML SETELAH JavaScript jalan
```

---

### 3. robots.txt — Aturan untuk Bot 🤖

**Apa itu robots.txt?**
File teks yang disimpan di root website, berisi aturan untuk crawler/bot.

**Contoh:**
```
# File: https://example.com/robots.txt

User-agent: *          # Berlaku untuk semua bot
Disallow: /admin/      # Larang akses /admin
Disallow: /private/    # Larang akses /private
Allow: /jobs/          # Izinkan akses /jobs
Crawl-delay: 5         # Tunggu 5 detik antar request
```

**Kenapa penting?**
- Melanggar robots.txt bisa bermasalah secara **hukum** (tergantung negara)
- IP kamu bisa di-**ban permanen**
- Data yang diambil mungkin tidak boleh digunakan secara komersial

**Yang kita lakukan di proyek ini:**
```python
def cek_robots(base_url):
    robots_url = base_url + "/robots.txt"
    response = requests.get(robots_url)
    # Cek apakah halaman yang mau di-scrape diizinkan
```

---

### 4. Rate Limiting ⏱️

Website membatasi jumlah request dari satu IP dalam waktu tertentu.

```
Request ke-1  → OK
Request ke-2  → OK
...
Request ke-100 → 429 Too Many Requests
Request ke-101 → IP di-ban sementara
```

**Solusi:**
```python
import time
for url in list_url:
    response = requests.get(url)
    time.sleep(2)  # Tunggu 2 detik antar request — jadi "sopan"
```

---

### 5. Kenapa Kita Pakai API? 💡

Setelah banyak yang gagal, kita pakai **RemoteOK API** dan **The Muse API** karena:

| Alasan | Penjelasan |
|--------|-----------|
| Legal | Mereka menyediakan API untuk umum |
| Stabil | Tidak kena block |
| Terstruktur | Data sudah dalam format JSON |
| Gratis | Tidak perlu bayar |

**Bedanya scraping vs API:**
```
Scraping:  Kita ambil data dari HTML yang tidak dirancang untuk kita
API:       Mereka sengaja menyediakan data untuk kita ambil
```

Dalam konteks akademik, **mengambil data dari API tetap valid** sebagai bentuk "crawling data dari internet" — bedanya hanya lebih sopan dan legal.

---

## Konsep Dasar

### HTTP Request & Response

```
Kamu                              Server
  |                                  |
  |--- GET /jobs HTTP/1.1 ---------> |
  |    Host: remoteok.com            |
  |    User-Agent: Mozilla/5.0       |
  |                                  |
  |<-- HTTP/1.1 200 OK ------------- |
  |    Content-Type: application/json|
  |    {"data": [...]}               |
```

**Status Code yang penting:**
- `200` → OK, data berhasil diambil
- `301` → Redirect ke URL lain
- `403` → Forbidden, akses ditolak
- `404` → Halaman tidak ditemukan
- `429` → Terlalu banyak request
- `503` → Server sedang down

---

### Inverted Index

Struktur data inti dari search engine. Kebalikan dari index biasa.

**Index biasa (forward index):**
```
Dokumen 1 → ["frontend", "engineer", "react", "remote"]
Dokumen 2 → ["data", "analyst", "python", "remote"]
Dokumen 3 → ["frontend", "developer", "vue", "jakarta"]
```

**Inverted index:**
```
"frontend"  → [Dokumen 1, Dokumen 3]
"engineer"  → [Dokumen 1]
"react"     → [Dokumen 1]
"remote"    → [Dokumen 1, Dokumen 2]
"data"      → [Dokumen 2]
"analyst"   → [Dokumen 2]
"developer" → [Dokumen 3]
"vue"       → [Dokumen 3]
"jakarta"   → [Dokumen 3]
```

**Kenapa inverted index lebih cepat?**
Kalau query "frontend", kita langsung tahu dokumen mana yang relevan tanpa perlu baca semua dokumen satu per satu.

---

### TF-IDF

**Term Frequency (TF):**
```
Seberapa sering kata muncul di satu dokumen

Dokumen: "python developer python expert python"
TF("python") = 3/5 = 0.6
```

**Inverse Document Frequency (IDF):**
```
Seberapa langka kata di seluruh koleksi

Total dokumen = 200
"python" muncul di 50 dokumen  → IDF rendah (umum)
"kubernetes" muncul di 3 dokumen → IDF tinggi (langka)

IDF = log(200/50) = log(4) = 0.60   ← "python"
IDF = log(200/3)  = log(67) = 1.82  ← "kubernetes"
```

**TF-IDF = TF × IDF:**
```
Kata yang sering muncul di dokumen ini TAPI jarang di dokumen lain
= kata yang paling "khas" untuk dokumen ini
= kata yang paling bermakna untuk pencarian
```

**Kelemahan TF-IDF:**
- Dokumen panjang cenderung dapat skor lebih tinggi (tidak adil)
- Kata yang muncul 100x vs 50x skornya beda besar padahal sama-sama "banyak"

---

### BM25 (Best Match 25)

Penyempurnaan TF-IDF dengan dua perbaikan:

**1. Saturasi frekuensi:**
```
TF-IDF: muncul 10x = 10x lebih baik dari muncul 1x
BM25:   muncul 10x ≈ muncul 7x (ada batasnya)

Analoginya: kalau kamu sebut nama seseorang 100x dalam 1 menit,
bukan berarti kamu 100x lebih suka dia dari yang menyebutnya 1x
```

**2. Normalisasi panjang dokumen:**
```
BM25 memberi "penalti" untuk dokumen yang terlalu panjang
karena wajar saja kata "python" muncul banyak di dokumen 10.000 kata
dibanding dokumen 100 kata
```

**Hasil evaluasi kita:**
```
BM25   → Precision: 64%, Recall: 53%, F1: 0.58  ✅
TF-IDF → Precision: 54%, Recall: 46%, F1: 0.50

Kesimpulan: BM25 lebih baik untuk kasus pencarian loker
```

---

### Cosine Similarity

Cara mengukur kemiripan antara query dan dokumen.

```
Query: "frontend engineer"
Doc 1: "frontend engineer react remote"   → Sudut kecil  → Similarity tinggi
Doc 2: "marketing manager sales"          → Sudut besar  → Similarity rendah

Nilai: 0.0 (tidak mirip sama sekali) sampai 1.0 (identik)
```

---

### Precision & Recall

```
Dari 10 hasil pencarian "frontend engineer":
✅ Frontend Engineer (CareerVillage)    → relevan
✅ Frontend Developer (Google)          → relevan
❌ Marketing Manager (Meta)             → tidak relevan
✅ Web Engineer (Amazon)                → relevan
❌ Sales Director (Nike)                → tidak relevan
✅ React Developer (Startup X)          → relevan
❌ HR Manager (Corp Y)                  → tidak relevan
✅ UI Engineer (Netflix)                → relevan
❌ Finance Analyst (Bank Z)             → tidak relevan
✅ Frontend Tech Lead (Shopee)          → relevan

Precision = 6/10 = 0.6    → 60% hasil yang muncul relevan
Recall    = 6/8  = 0.75   → dari 8 loker frontend yang ada, 6 berhasil ditemukan
F1-Score  = 2 × (0.6 × 0.75)/(0.6 + 0.75) = 0.67
```

**Tradeoff Precision vs Recall:**
```
Mau Recall tinggi?  → Tampilkan lebih banyak hasil (tapi banyak yang tidak relevan)
Mau Precision tinggi? → Tampilkan sedikit hasil (tapi semuanya relevan)
F1-Score = keseimbangan keduanya
```

---

## Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────┐
│                     JOBFINDER                           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────┐  │
│  │ scraper  │    │  prepro  │    │  search_engine   │  │
│  │  .py     │───>│  cesing  │───>│      .py         │  │
│  │          │    │  .py     │    │                  │  │
│  │RemoteOK  │    │Cleaning  │    │ Inverted Index   │  │
│  │TheMuse   │    │Tokenisasi│    │ TF-IDF           │  │
│  │          │    │Stopword  │    │ BM25             │  │
│  └──────────┘    └──────────┘    └────────┬─────────┘  │
│       │               │                   │            │
│       ▼               ▼                   ▼            │
│  data_loker      data_bersih         ┌─────────┐       │
│    .json           .json             │  app.py │       │
│                                      │Streamlit│       │
│                                      └────┬────┘       │
│                                           │            │
│                                      ┌────▼────┐       │
│                                      │tunnel.py│       │
│                                      │  ngrok  │       │
│                                      └─────────┘       │
│                                      https://xxx       │
└─────────────────────────────────────────────────────────┘
```

---

## Struktur File

```
jobfinder/
│
├── scraper.py          # Ambil data dari RemoteOK & TheMuse API
├── prepocesing.py      # Bersihkan & normalisasi teks
├── search_engine.py    # Implementasi TF-IDF & BM25
├── evaluasi.py         # Hitung Precision, Recall, F1-Score
├── app.py              # UI Streamlit
├── tunnel.py           # Ngrok tunnel untuk presentasi
│
├── data_loker.json     # Raw data hasil scraping
└── data_bersih.json    # Data setelah preprocessing
```

---

## Penjelasan Tiap File

### scraper.py
**Tugasnya:** Mengambil data loker dari internet

**Cara kerjanya:**
1. Kirim HTTP GET request ke API
2. Parse response JSON
3. Ekstrak field yang dibutuhkan (judul, perusahaan, lokasi, tags)
4. Simpan ke `data_loker.json`

**Kenapa 2 sumber?**
RemoteOK dibatasi 100 loker per request. Ditambah TheMuse untuk mencapai 200+ loker.

**Yang dipelajari:**
- HTTP requests dengan Python
- Parsing JSON response
- Penanganan error (try/except)
- Cara kerja API

---

### prepocesing.py
**Tugasnya:** Membersihkan teks mentah menjadi teks yang siap diindeks

**Pipeline preprocessing:**
```
Teks mentah: "<p>Looking for a <strong>Frontend Engineer</strong>!</p>"
     ↓ Strip HTML
"Looking for a Frontend Engineer!"
     ↓ Case folding
"looking for a frontend engineer!"
     ↓ Remove special chars
"looking for a frontend engineer"
     ↓ Tokenisasi
["looking", "for", "a", "frontend", "engineer"]
     ↓ Stopword removal (buang kata tidak bermakna)
["frontend", "engineer"]
     ↓ Gabung jadi teks bersih
"frontend engineer"
```

**Kenapa preprocessing penting?**
Tanpa preprocessing, "Frontend" dan "frontend" dianggap kata berbeda. "engineer!" dan "engineer" juga dianggap berbeda. Ini merusak akurasi pencarian.

---

### search_engine.py
**Tugasnya:** Implementasi inti IR — indexing dan retrieval

**Proses indexing:**
```python
# TF-IDF menggunakan scikit-learn
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(dokumen)
# Hasilnya: matriks (200 dokumen × N kata unik)
# Setiap sel berisi bobot TF-IDF kata itu di dokumen itu

# BM25 menggunakan rank_bm25
bm25 = BM25Okapi([doc.split() for doc in dokumen])
```

**Proses retrieval:**
```python
# Query masuk → preprocessing → hitung similarity → ranking
query = "frontend engineer"
skor = bm25.get_scores(query.split())
ranking = sorted(enumerate(skor), key=lambda x: x[1], reverse=True)
```

---

### evaluasi.py
**Tugasnya:** Mengukur kualitas sistem IR secara objektif

**Ground truth:**
Kita mendefinisikan manual dokumen mana yang "seharusnya relevan" untuk tiap query berdasarkan kata kunci.

**Kenapa evaluasi penting?**
Tanpa evaluasi, kita tidak tahu apakah sistem kita bagus atau jelek. Evaluasi adalah bukti ilmiah bahwa sistem kita bekerja.

---

### app.py
**Tugasnya:** Antarmuka pengguna berbasis web

**Komponen Streamlit yang dipakai:**
- `st.text_input()` → kotak pencarian
- `st.selectbox()` → pilih metode (BM25/TF-IDF)
- `st.markdown()` → tampilkan hasil dengan HTML custom
- `@st.cache_resource` → cache model supaya tidak load ulang setiap query

---

### tunnel.py
**Tugasnya:** Membuat link publik dari localhost

**Cara kerja ngrok:**
```
Laptop kamu          Ngrok Server          User lain
localhost:8501  ←──→  ngrok.io   ←──→   heat-xxx.ngrok-free.dev
```

Ngrok membuat "terowongan" antara laptop kamu dan server mereka, sehingga orang lain bisa mengakses localhost kamu dari luar.

---

## Alur Data

```
1. COLLECTION
   RemoteOK API  ──┐
                   ├──> data_loker.json (200 dokumen mentah)
   TheMuse API   ──┘

2. PREPROCESSING
   data_loker.json
        │
        ├── Strip HTML tags
        ├── Case folding (huruf kecil)
        ├── Remove special characters
        ├── Gabungkan field (judul + tags + lokasi)
        │
        └──> data_bersih.json (200 dokumen bersih)

3. INDEXING
   data_bersih.json
        │
        ├── TF-IDF Matrix (200 × N_kata)
        └── BM25 Index

4. RETRIEVAL
   Query user
        │
        ├── Preprocessing query (sama seperti dokumen)
        ├── Hitung skor (TF-IDF/BM25)
        └── Ranking → Top-K hasil

5. EVALUATION
   Ground truth + hasil retrieval
        │
        ├── Precision
        ├── Recall
        └── F1-Score
```

---

## Evaluasi IR

### Hasil Evaluasi Proyek Ini

| Query | BM25 Precision | BM25 Recall | TF-IDF Precision | TF-IDF Recall |
|-------|---------------|-------------|-----------------|---------------|
| frontend engineer | - | - | - | - |
| data analyst | - | - | - | - |
| software engineer | - | - | - | - |
| marketing manager | - | - | - | - |
| product manager | - | - | - | - |
| **Rata-rata** | **0.64** | **0.53** | **0.54** | **0.46** |

### Kesimpulan Evaluasi

BM25 lebih unggul dari TF-IDF di semua metrik untuk kasus pencarian loker ini. Hal ini sesuai dengan literatur IR bahwa BM25 umumnya lebih baik untuk short-text retrieval (judul + tags) karena normalisasi panjang dokumennya.

### Keterbatasan Evaluasi

1. **Ground truth subjektif** — relevansi ditentukan berdasarkan keyword matching, bukan penilaian manusia
2. **Dataset kecil** — 200 dokumen tergolong kecil untuk evaluasi IR yang representatif
3. **Bahasa Inggris** — data dari RemoteOK/TheMuse berbahasa Inggris, bukan Indonesia

---

## Cara Menjalankan

### Prasyarat
```bash
pip install requests beautifulsoup4 pandas streamlit rank_bm25 scikit-learn pyngrok
```

### Langkah-langkah

**1. Ambil data loker:**
```bash
python scraper.py
```

**2. Preprocessing:**
```bash
python prepocesing.py
```

**3. Test search engine (opsional):**
```bash
python search_engine.py
```

**4. Evaluasi IR (opsional):**
```bash
python evaluasi.py
```

**5. Jalankan aplikasi:**
```bash
streamlit run app.py
```

**6. Untuk presentasi (link publik):**
```bash
python tunnel.py
```

---

## Pelajaran & Refleksi

### Hal yang Dipelajari

**1. Dunia nyata lebih kompleks dari teori**
Di kuliah, scraping terdengar mudah. Kenyataannya hampir semua situs besar Indonesia aktif memblokir bot dengan Cloudflare, JavaScript rendering, dan rate limiting.

**2. Etika di atas segalanya**
Cek robots.txt bukan formalitas — ini tentang menghormati aturan pemilik website dan melindungi diri sendiri dari masalah hukum.

**3. API > Scraping untuk production**
Kalau ada API resmi, selalu pilih API. Lebih stabil, legal, dan terstruktur.

**4. BM25 terbukti lebih baik**
Tidak hanya di paper akademik — di proyek nyata pun BM25 menghasilkan ranking yang lebih relevan dari TF-IDF murni.

**5. Evaluasi adalah bukti**
Tanpa Precision & Recall, kita hanya bisa bilang "kayaknya sistem ini bagus". Dengan evaluasi, kita bisa bilang "sistem ini 64% akurat" — jauh lebih kuat untuk laporan.

---

### Roadmap Pengembangan

Kalau mau dikembangkan lebih lanjut:

- [ ] Tambah Selenium untuk scraping situs yang pakai JavaScript
- [ ] Implementasi stemming Bahasa Indonesia (PySastrawi) untuk data loker Indonesia
- [ ] Database SQLite menggantikan JSON (lebih skalabel)
- [ ] Filter by lokasi, tipe kerja, gaji
- [ ] Autocomplete di search bar
- [ ] Deploy ke cloud (Railway, Render) supaya tidak butuh laptop nyala

---

### Referensi

- Manning, C.D., Raghavan, P., Schütze, H. (2008). *Introduction to Information Retrieval*. Cambridge University Press.
- Robertson, S., Zaragoza, H. (2009). *The Probabilistic Relevance Framework: BM25 and Beyond*. Foundations and Trends in Information Retrieval.
- RemoteOK API: https://remoteok.com/api
- The Muse API: https://www.themuse.com/developers/api/v2

---

*Dibuat untuk Mata Kuliah Temu Kembali Informasi — Informatika UTM*  
*Kelompok: Ahmad Abid Romadhoni, Bayu Firmansyah, Wafa' Amatul Azizah*