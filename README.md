# 🌐 Universal Multi-Portal News Data Scraper & Sentiment Analytics

Aplikasi web modern berbasis **Python**, **Streamlit**, dan **BeautifulSoup** untuk melakukan *web scraping* berita otomatis dari berbagai portal berita Indonesia (seperti Kompas.com, Detik.com, CNN Indonesia, Riauterkini.com, Antara News, Liputan6, dsb.) serta situs berita kustom mana saja.

Aplikasi dilengkapi dengan **Dashboard Analytik**, **Pie Chart Analisis Sentimen (Positif, Negatif, Netral)**, **WordCloud Visualisasi Kata Kunci**, **Filter Waktu Rilis Berita (Hari Ini, Bulan Ini, Rentang Tanggal)**, dan **Ekspor Data Multi-Format (CSV, Excel, JSON)**.

---

## ✨ Fitur Utama

- 🗞️ **Multi-Portal & Custom URL Scraper**:
  - Pilihan portal berita utama (**Kompas.com**, **Detik.com**, **CNN Indonesia**).
  - Mode **Situs / Portal Kustom**: Memasukkan URL halaman utama atau indeks berita dari situs manapun.
  - Mode **URL Artikel Langsung**: Ekstraksi instan dari 1 URL berita spesifik.
- 🎭 **Analisis Sentimen Berita**:
  - Klasifikasi otomatis berita ke dalam kategori 🟢 **Positif**, 🔴 **Negatif**, dan ⚪ **Netral**.
  - **Pie Chart Sentimen** dengan persentase & warna kustom (Hijau, Merah, Putih).
- ☁️ **WordCloud & Topic Frequency Mining**:
  - Visualisasi kata kunci utama (*WordCloud*) yang paling sering dibahas di portal berita.
  - Pembersihan otomatis kata hubung bahasa Indonesia (*Stopwords*).
- 📅 **Filter Waktu Rilis & Urutan Berita Teratas**:
  - Filter waktu: *Berita Hari Ini*, *Berita Bulan Ini*, *Rentang Tanggal Kustom*, dan *Semua Berita*.
  - Otomatis mengurutkan berita dengan **berita terbaru dirilis di paling atas**.
- 📥 **Penyimpanan & Ekspor Data**:
  - Penyimpanan otomatis ke folder `data_exports/`.
  - Tombol unduh instan format **CSV**, **Excel (.xlsx)**, dan **JSON**.

---

## 🛠️ Instalasi & Cara Menjalankan

### 1. Clone Repositori
```bash
git clone https://github.com/ayat7779/scrippingportalberita.git
cd scrippingportalberita
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi Web Streamlit
```bash
streamlit run app.py
```

Aplikasi akan otomatis terbuka di browser pada alamat **`http://localhost:8501`**.

---

## 📂 Struktur Berkas

- `app.py`: Antarmuka dashboard web berbasis Streamlit.
- `scraper.py`: Engine scraper universal (`UniversalNewsScraper`) dengan parser Kompas, Detik, CNN, dan Kustom.
- `data_exports/`: Folder khusus tempat penyimpanan otomatis hasil scraping.
- `requirements.txt`: Daftar dependensi Python.
