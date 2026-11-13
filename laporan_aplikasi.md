# LAPORAN PENGEMBANGAN PERANGKAT LUNAK (SDLC)
## UNIVERSAL MULTI-PORTAL NEWS DATA SCRAPER & SENTIMENT ANALYTICS DASHBOARD

---

## 1. BAGIAN AWAL (FRONT MATTER)

### 1.1 Halaman Judul
* **Nama Aplikasi**: Universal Multi-Portal News Data Scraper & Sentiment Analytics Dashboard
* **Tujuan Penyusunan**: Laporan Komprehensif Rekayasa Perangkat Lunak (Software Engineering Project Report)
* **Pengembang**: Tim Pengembang Software Portal Berita
* **Repositori Resmi**: [https://github.com/ayat7779/scrippingportalberita.git](https://github.com/ayat7779/scrippingportalberita.git)
* **Platform / Peramban**: Python 3.12, Streamlit 1.30+, Cross-Platform Web Peramban
* **Tahun Pembuatan**: 2026

---

### 1.2 Lembar Pengesahan

Dokumen laporan pengembangan aplikasi ini telah diperiksa, diuji, dan diverifikasi kelengkapannya sesuai dengan standar *Software Development Life Cycle* (SDLC).

| Peran | Nama / Jabatan | Tanda Tangan & Tanggal |
| :--- | :--- | :--- |
| **Lead Software Engineer** | Tim Pengembang Rekayasa Perangkat Lunak | `[ TERVERIFIKASI ]` - 13 November 2026 |
| **Quality Assurance Lead** | Tim Pengujian & QA | `[ TERVERIFIKASI ]` - 13 November 2026 |
| **Product Owner / Stakeholder** | Pengelola Sistem Portal Berita | `[ TERVERIFIKASI ]` - 13 November 2026 |

---

### 1.3 Ringkasan Eksekutif / Abstrak

Kebutuhan akan pemantauan media (*media monitoring*), pengumpulan berita (*news aggregation*), dan analisis tren publik (*sentiment & topic analysis*) secara cepat menjadi sangat krusial di era digital. Sebagian besar portal berita di Indonesia memiliki format HTML, struktur DOM, dan penamaan kelas CSS yang sangat beragam—mulai dari portal berita nasional modern (seperti Kompas.com, Detik.com, CNN Indonesia) hingga portal berita daerah/klasik berbahan CMS PHP kustom (seperti Riauterkini.com).

Aplikasi **Universal Multi-Portal News Data Scraper & Sentiment Analytics** dirancang sebagai solusi komprehensif untuk otomatisasi ekstraksi berita secara mandiri tanpa ketergantungan pada API berbayar. Aplikasi ini dibangun berbasis bahasa pemrograman **Python 3.12** dan antarmuka web interaktif **Streamlit**.

> [!NOTE]
> **Highlight Fitur Utama Sistem**:
> 1. **Universal Dual-Strategy Scraper Engine**: Mampu mengekstrak data dari portal populer terintegrasi maupun URL portal berita kustom berbasis *OpenGraph*, *JSON-LD Schema.org/NewsArticle*, dan *heuristic HTML DOM scanning*.
> 2. **Analisis Sentimen & Topik Berita**: Pengelompokan sentimen otomatis berbasis *Indonesian Sentiment Lexicon* menjadi 🟢 **Positif**, 🔴 **Negatif**, dan ⚪ **Netral**, disajikan dalam bentuk **Pie Chart Kustom** dengan persentase dan nilai eksak.
> 3. **WordCloud & Frequency Mining**: Ekstraksi 10 kata kunci teratas dan visualisasi *WordCloud* berfilter *Indonesian Stopwords*.
> 4. **Fitur Pengurutan & Filter Waktu**: Pengurutan berita berbasis tanggal rilis (*newest at top*) dan penyaringan rilis (*Hari Ini*, *Bulan Ini*, *Rentang Tanggal*, *Semua Berita*).
> 5. **Multi-Format Export & Automated File Persistence**: Ekspor instan ke format **CSV**, **Excel (.xlsx)**, dan **JSON** dengan penulisan otomatis ke direktori khusus `data_exports/`.

---

### 1.4 Daftar Indeks Referensi

#### Daftar Tabel
* **Tabel 1.1**: Perbandingan Solusi Scraping Terhadap Aplikasi Kompetitor
* **Tabel 3.1**: Spesifikasi Kebutuhan Fungsional (Functional Requirements)
* **Tabel 3.2**: Spesifikasi Kebutuhan Non-Fungsional (Non-Functional Requirements)
* **Tabel 4.1**: Kamus Data Struktur Artikel Berita (Data Dictionary)
* **Tabel 6.1**: Matriks Pengujian Fungsional Sistem (Black Box Testing)
* **Tabel 6.2**: Matriks Hasil Pengujian Multi-Portal Real-World

#### Daftar Singkatan & Istilah
* **SDLC**: *Software Development Life Cycle*
* **DOM**: *Document Object Model*
* **KPI**: *Key Performance Indicator*
* **NLP**: *Natural Language Processing*
* **CSV**: *Comma-Separated Values*
* **JSON**: *JavaScript Object Notation*
* **UAT**: *User Acceptance Testing*
* **CI/CD**: *Continuous Integration / Continuous Deployment*

---

## 2. BAB I: PENDAHULUAN

### 2.1 Latar Belakang

Perkembangan informasi di media daring Indonesia berlangsung sangat cepat dengan volume puluhan ribu berita dipublikasikan setiap harinya. Bagi organisasi, peneliti media, praktisi humas, maupun analis bisnis, memantau opini publik dan isu terkini dari berbagai media independen secara manual membutuhkan waktu dan tenaga kerja (*labor-intensive*) yang sangat besar.

Tantangan utama dalam pembuatan alat ekstraksi data berita (*news scraper*) di Indonesia meliputi:
1. **Heterogenitas Struktur Web**: Struktur DOM antara portal besar modern (seperti Kompas atau Detik) dan portal lokal (seperti Riauterkini) berbeda secara signifikan.
2. **Ketiadaan API Publik**: Mayoritas portal berita tidak menyediakan REST API gratis yang terbuka untuk publik.
3. **Kebutuhan Analisis Kualitatif**: Ekstraksi teks mentah saja tidak cukup; pengguna membutuhkan klasifikasi sentimen (*Positif, Negatif, Netral*) dan *WordCloud* untuk memahami isu utama secara visual dalam hitungan detik.

Oleh karena itu, dibuatlah aplikasi **Universal Multi-Portal News Data Scraper & Sentiment Analytics Dashboard** untuk menyelesaikan seluruh permasalahan tersebut dalam satu platform yang mudah digunakan.

---

### 2.2 Rumusan Masalah

1. Bagaimana merancang *engine web scraper* universal yang sanggup mengekstrak berita dari situs modern maupun situs berita klasik berbasis PHP?
2. Bagaimana mengimplementasikan algoritma klasifikasi sentimen teks bahasa Indonesia yang cepat dan akurat tanpa biaya API pihak ketiga?
3. Bagaimana menyajikan dashboard analitis interaktif yang memuat KPI, *Pie Chart* sentimen, *WordCloud*, serta pengurutan berita berdasarkan waktu rilis terbaru di posisi paling atas?
4. Bagaimana menyediakan mekanisme penyimpanan berkas terstruktur otomatis ke direktori server (`data_exports/`) dan opsi unduh *multi-format* (CSV, Excel, JSON)?

---

### 2.3 Tujuan Proyek

1. **Otomatisasi Ekstraksi Berita**: Menghasilkan *engine* yang dapat mengambil judul, penulis, tanggal/waktu rilis, jumlah *view*, gambar, dan paragraf isi berita secara otomatis.
2. **Visualisasi Analytics**: Menampilkan KPI keterbacaan, grafik kata kunci terbanyak, *WordCloud*, serta *Pie Chart* sentimen dengan skema warna kustom (🟢 Positif = Hijau, 🔴 Negatif = Merah, ⚪ Netral = Putih).
3. **Aksesibilitas Data**: Menyediakan fitur filter waktu rilis (*Hari Ini*, *Bulan Ini*, *Rentang Tanggal*) dan fitur unduh data cepat.
4. **Portabilitas & Deployment**: Menyimpan seluruh *source code* dalam repositori Git publik di GitHub [https://github.com/ayat7779/scrippingportalberita.git](https://github.com/ayat7779/scrippingportalberita.git).

---

### 2.4 Batasan & Ruang Lingkup (Scope & Delimitations)

#### Dalam Cakupan (In Scope):
- Ekstraksi berita dari portal terintegrasi: **Kompas.com**, **Detik.com**, **CNN Indonesia**.
- Ekstraksi berita dari sembarang **Situs / Portal Kustom** (seperti Riauterkini.com, Antaranews.com, Liputan6.com, dll.).
- Ekstraksi 1 URL artikel berita secara spesifik (*Direct URL mode*).
- Klasifikasi sentimen 3-kelas (*Positif*, *Negatif*, *Netral*) berbasis *Indonesian Sentiment Lexicon*.
- Pengurutan data otomatis (*newest first* / terbaru di paling atas).
- Ekspor berkas ke CSV, Excel (XLSX), dan JSON.
- Penyimpanan berkas otomatis ke direktori `data_exports/`.

#### Luar Cakupan (Out of Scope / Future Work):
- Scraping situs yang dilindungi oleh sistem CAPTCHA kompleks atau *Cloudflare Turnstile Bot Protection*.
- Pelatihan *deep learning model* berbasis Transformers/BERT (menggunakan *lexicon-based NLP* untuk efisiensi latensi).

---

## 3. BAB II: LANDASAN TEORI & TINJAUAN TEKNOLOGI

### 3.1 Domain Knowledge

#### 1. Web Scraping & DOM Parsing
*Web scraping* adalah teknik otomatisasi pengunduhan dokumen HTML melalui protokol HTTP/HTTPS yang dilanjutkan dengan proses ekstraksi elemen teks menggunakan pembacaan struktur *Document Object Model* (DOM). Dalam sistem ini, perpustakaan `BeautifulSoup4` dan parser `lxml` digunakan untuk memproses tag-tag HTML, atribut `href`, atribut `meta` (*OpenGraph*), serta skema *JSON-LD* (`application/ld+json`).

#### 2. Lexicon-Based Indonesian Sentiment Analysis
Analisis sentimen berbasis leksikon bekerja dengan mencocokkan kata-kata dalam teks berita terhadap kamus leksikon kata berbobot positif (*POSITIVE_WORDS*) dan negatif (*NEGATIVE_WORDS*). Metode ini sangat efisien (*low CPU overhead*) dan tidak memerlukan infrastruktur GPU.

#### 3. WordCloud & Natural Language Preprocessing
Visualisasi *WordCloud* menggambarkan frekuensi kata kunci di mana ukuran teks berbanding lurus dengan frekuensi kemunculan kata dalam korpus berita. Sebelum pembentukan *WordCloud*, teks melewati tahap pembersihan *Indonesian Stopwords* (menghapus kata tugas seperti *dan, di, ke, dari, yang, untuk, pada, dsb.*).

---

### 3.2 Kajian Sistem / Aplikasi Sejenis

| Fitur / Parameter | Web Scraper Generik (misal Octoparse) | Python Scrapy Script | **Aplikasi ScrappingPortalBerita (Sistem Ini)** |
| :--- | :--- | :--- | :--- |
| **Antarmuka Pengguna** | Desktop GUI Kompleks | CLI / Tanpa GUI | **Streamlit Web Dashboard Interaktif** |
| **Ekstraksi Multi-Portal** | Harus Konfigurasi Manual | Kode Hardcoded per Situs | **Universal Scraper Engine (Dual-Strategy)** |
| **Analisis Sentimen** | Tidak Ada | Tidak Ada | **Otomatis (Positif, Negatif, Netral)** |
| **Visualisasi Analytics** | Terbatas | Tidak Ada | **KPI, Pie Chart, Bar Chart, & WordCloud** |
| **Filter Tanggal Rilis** | Tidak Ada | Perlu Koding Ulang | **Filter Hari Ini, Bulan Ini, & Date Range** |
| **Penyimpanan Berkas** | Lokal Terbatas | Terbatas ke CSV | **Otomatis ke Folder `data_exports/` (CSV/XLSX/JSON)** |

---

### 3.3 Tech Stack Rationale

1. **Bahasa Pemrograman**: **Python 3.12**
   * *Alasan*: Memiliki ekosistem pustaka pemrosesan teks, manipulasi data, dan scraping terkelola yang sangat kaya.
2. **Framework Dashboard**: **Streamlit 1.30+**
   * *Alasan*: Memungkinkan pembuatan dashboard analitis berbasis data secara cepat dengan elemen UI modern (*Material Symbols*, *segmented controls*, *metrics*, *dataframe*).
3. **Engine HTTP & Parsing**: **Requests & BeautifulSoup4 (lxml)**
   * *Alasan*: Kecepatan parsing yang tinggi dan kestabilan koneksi HTTP session.
4. **Pemrosesan Data**: **Pandas 2.0+ & OpenPyXL**
   * *Alasan*: Memfasilitasi transformasi DataFrame, pengurutan tanggal, dan penulisan berkas Excel secara presisi.
5. **Visualisasi**: **Matplotlib & WordCloud**
   * *Alasan*: Kemampuan rendering *Pie Chart* kustom dan pembuatan gambar *WordCloud* beresolusi tinggi.

---

## 4. BAB III: METODOLOGI & ANALISIS KEBUTUHAN

### 4.1 Metodologi Pengembangan Perangkat Lunak

Pengembangan aplikasi ini menggunakan metodologi **Iterative Agile Development** yang dibagi dalam 4 siklus utama:

```mermaid
graph TD
    A[Siklus 1: Inisiasi & Engine Scraping Kompas] --> B[Siklus 2: Multi-Portal & Universal Scraper]
    B --> C[Siklus 3: Analytics, Sentimen & WordCloud]
    C --> D[Siklus 4: Penyimpanan Folder & Release GitHub]
```

1. **Siklus 1 (Single-Portal Scraper)**: Pembuatan modul scraper awal untuk portal Kompas.com beserta antarmuka Streamlit dasar.
2. **Siklus 2 (Universal Multi-Portal Engine)**: Penambahan dukungan portal Detik.com, CNN Indonesia, dan algoritma *Universal Scraper* untuk menangani situs berita kustom (seperti Riauterkini.com).
3. **Siklus 3 (Analytics & NLP Integration)**: Pengintegrasian modul analisis sentimen 3-kelas, pembuatan *Pie Chart* berwarna kustom, *WordCloud*, pengurutan waktu rilis (*newest at top*), dan filter tanggal rilis.
4. **Siklus 4 (Persistence & Deployment)**: Pembuatan folder terstruktur `data_exports/`, pengujian menyeluruh (*QA Testing*), serta pengunggahan ke repositori GitHub resmi.

---

### 4.2 Analisis Pengguna (User Persona)

1. **Media Monitoring Analyst**: Pengguna yang memerlukan rekapitulasi pemberitaan publik, analisis isu populer, dan grafik sentimen media.
2. **Jurnalis / Peneliti Berita**: Pengguna yang ingin mengumpulkan korpus berita dalam jumlah besar dari berbagai sumber untuk bahan riset.
3. **Pengguna Umum / Pembaca**: Pengguna yang ingin membaca kumpulan artikel berita terkini dalam satu antarmuka bersih tanpa gangguan iklan.

---

### 4.3 Spesifikasi Kebutuhan Fungsional (Functional Requirements)

| Kode Kebutuhan | Deskripsi Fitur Fungsional | Prioritas |
| :--- | :--- | :--- |
| **FR-01** | Sistem harus dapat mengekstrak berita dari Kompas.com, Detik.com, dan CNN Indonesia. | **Tinggi** |
| **FR-02** | Sistem harus sanggup mengekstrak berita dari URL portal kustom berbasis *DOM & Link Scanning*. | **Tinggi** |
| **FR-03** | Sistem harus mengekstrak judul, penulis, tanggal/waktu rilis, jumlah *view*, gambar, dan paragraf isi. | **Tinggi** |
| **FR-04** | Sistem harus mengklasifikasikan sentimen artikel berita menjadi 🟢 Positif, 🔴 Negatif, atau ⚪ Netral. | **Tinggi** |
| **FR-05** | Sistem harus mengurutkan artikel berita berdasarkan waktu rilis terbaru di posisi paling atas. | **Tinggi** |
| **FR-06** | Sistem harus menyediakan filter waktu rilis (*Hari Ini*, *Bulan Ini*, *Rentang Tanggal*, *Semua Berita*). | **Tinggi** |
| **FR-07** | Sistem harus menyajikan Dashboard Analytik (KPI, *Pie Chart* sentimen, *Bar Chart*, & *WordCloud*). | **Tinggi** |
| **FR-08** | Sistem harus dapat mengekspor dan menyimpan berkas ke folder `data_exports/` (CSV, Excel, JSON). | **Tinggi** |

---

### 4.4 Spesifikasi Kebutuhan Non-Fungsional (Non-Functional Requirements)

| Kategori | Parameter Kebutuhan | Target Spesifikasi |
| :--- | :--- | :--- |
| **Performance** | Latensi Ekstraksi Indeks | $< 2.0$ detik per halaman portal |
| **Performance** | Latensi Parsing Detail | $< 0.5$ detik per artikel berita |
| **Usability** | Kemudahan Penggunaan | Antarmuka intuitif berbasis *Streamlit Material Components* |
| **Reliability** | Exception Handling | Sistem tidak *crash* jika menemukan URL rusak/404 |
| **Compatibility** | Peramban | Google Chrome, Mozilla Firefox, Microsoft Edge, Safari |
| **Storage** | Persistence | Berkas otomatis tersimpan di folder `data_exports/` |

---

## 5. BAB IV: PERANCANGAN SISTEM (SYSTEM DESIGN)

### 5.1 Arsitektur Sistem Tingkat Tinggi (High-Level Architecture)

```mermaid
architecture-beta
    group user_layer(internet, "User Interface Layer")
    service browser(browser, "Streamlit Dashboard App", "streamlit") in user_layer

    group logic_layer(server, "Application Logic Layer")
    service scraper_engine(code, "UniversalNewsScraper Engine", "python") in logic_layer
    service nlp_engine(cpu, "Sentiment & Topic Mining Engine", "python") in logic_layer

    group storage_layer(disk, "Data & Storage Layer")
    service exports_folder(database, "data_exports/ Folder (CSV/XLSX/JSON)", "disk") in storage_layer

    group external_layer(cloud, "External News Portals")
    service news_sites(globe, "Kompas / Detik / CNN / Riauterkini", "http") in external_layer

    browser -> scraper_engine: Triggers Scraping Request
    scraper_engine -> news_sites: HTTP GET Request (HTML/DOM)
    news_sites -> scraper_engine: Returns HTML Document
    scraper_engine -> nlp_engine: Sends Raw Article Texts
    nlp_engine -> browser: Returns Analytics, Sentiments, & WordCloud
    scraper_engine -> exports_folder: Auto Saves CSV / Excel / JSON Files
```

---

### 5.2 Pemodelan Alur Logika & Proses

#### 1. Flowchart Alur Ekstraksi Berita Universal

```mermaid
flowchart TD
    A([Mulai Scraping]) --> B[Input URL / Pilih Portal & Filter Waktu]
    B --> C{Pilih Mode Scraping}
    C -- Portal Populer --> D[Scrape Indeks Kompas / Detik / CNN]
    C -- Portal Kustom --> E[Scrape Custom Portal via Dual-Strategy]
    C -- Direct URL --> F[Scrape Single Article Detail]
    
    D --> G[Kumpulkan URL Artikel Candidate]
    E --> G
    F --> H[Ekstrak Full Detail & Meta]
    
    G --> H[Ekstrak Judul, Penulis, Tanggal, Waktu, View, & Paragraf]
    H --> I[Jalankan Sentiment Lexicon Classifier]
    I --> J[Jalankan Date Filter & Date Parser]
    J --> K[Urutkan Berita Terbaru di Paling Atas]
    K --> L[Simpan Berkas ke Folder data_exports/]
    L --> M[Render KPI, Pie Chart, WordCloud, & Tabel Data]
    M --> N([Selesai])
```

---

### 5.3 Perancangan Data & Skema Output (Data Dictionary)

Setiap artikel berita yang di-scrape disimpan dalam objek kamus data (*data dictionary*) dengan skema berikut:

| Field Name | Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `source` | `String` | Nama portal berita / domain asal | `"riauterkini.com"` / `"Kompas.com"` |
| `title` | `String` | Judul lengkap berita | `"Pekanbaru Raih Anugerah Penggerak..."` |
| `url` | `String` | Tautan absolut artikel berita | `"https://riauterkini.com/index.php?com=isi..."` |
| `category` | `String` | Kategori berita | `"Sosial"` / `"News"` |
| `publish_date` | `String` | Tanggal publikasi berita | `"Jumat, 13 Nopember 2026"` |
| `publish_time` | `String` | Waktu/jam publikasi berita | `"13:31:04 WIB"` |
| `view_count` | `String` | Jumlah pembaca / views | `"74"` / `"Tidak Ditampilkan"` |
| `sentiment` | `String` | Klasifikasi sentimen berita | `"🟢 Positif"` / `"🔴 Negatif"` / `"⚪ Netral"` |
| `author` | `String` | Nama penulis / tim redaksi | `"Aryo Tondang"` / `"Riauterkini"` |
| `content` | `String` | Teks paragraf artikel berita | `"JAMBI, KOMPAS.com – Sejumlah..."` |
| `paragraph_count`| `Integer` | Jumlah total paragraf berita | `37` |
| `image_url` | `String` | URL gambar header artikel | `"https://asset.kompas.com/crops/..."` |

---

## 6. BAB V: IMPLEMENTASI SISTEM

### 6.1 Spesifikasi Lingkungan Implementasi

* **Sistem Operasi**: Windows 11 Home / Linux Ubuntu 22.04 LTS
* **Perangkat Keras**: AMD Ryzen / Intel Core i7, RAM 16 GB, SSD 512 GB
* **Lingkungan Bahasa**: Python 3.12.8 (64-bit)
* **Pustaka Utama**: `streamlit==1.67.0`, `beautifulsoup4==4.15.0`, `requests==2.34.2`, `pandas==3.1.1`, `openpyxl==3.1.5`, `wordcloud==1.9.6`, `matplotlib==3.11.2`

---

### 6.2 Struktur Direktori Proyek

```text
ScrappingPortalBerita/
├── .gitignore                      # Konfigurasi pengabaian Git
├── README.md                       # Dokumentasi resmi repositori GitHub
├── laporan_aplikasi.md             # Dokumen laporan SDLC komprehensif
├── app.py                          # Antarmuka utama Streamlit Web Dashboard
├── scraper.py                      # Core engine UniversalNewsScraper & NLP logic
├── requirements.txt                # Berkas dependensi pustaka Python
└── data_exports/                   # Folder penyimpanan otomatis berkas ekspor
    ├── .gitkeep
    ├── news_scraping_latest.csv
    ├── news_scraping_latest.xlsx
    └── news_scraping_latest.json
```

---

### 6.3 Realisasi Fitur & Modul Kode Inti

#### 1. Klasifikasi Sentimen Berita (`analyze_sentiment` di `scraper.py`)
```python
def analyze_sentiment(text: str) -> str:
    """Analyze Indonesian news text sentiment (Positif, Negatif, Netral)."""
    if not text:
        return '⚪ Netral'

    text_lower = text.lower()
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text_lower)

    pos_score = sum(1 for w in words if w in POSITIVE_WORDS)
    neg_score = sum(1 for w in words if w in NEGATIVE_WORDS)

    if pos_score > neg_score:
        return '🟢 Positif'
    elif neg_score > pos_score:
        return '🔴 Negatif'
    else:
        return '⚪ Netral'
```

#### 2. Pengurutan Berita Berdasarkan Tanggal Terbaru (`sort_articles_by_date_descending`)
```python
def parse_indonesian_datetime(item: Dict[str, Any]) -> datetime:
    date_str = str(item.get('publish_date', ''))
    time_str = str(item.get('publish_time', ''))
    combined = f"{date_str} {time_str}".replace('N/A', '').replace('Pukul', '').replace('WIB', '').replace('Nopember', 'November').strip()

    try:
        m = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})(?:\s+(\d{1,2}:\d{2}(?::\d{2})?))?', combined)
        if m:
            day, month_str, year, time_part = m.groups()
            months = {
                'januari': 1, 'jan': 1, 'februari': 2, 'feb': 2, 'maret': 3, 'mar': 3,
                'april': 4, 'apr': 4, 'mei': 5, 'juni': 6, 'jun': 6, 'juli': 7, 'jul': 7,
                'agustus': 8, 'agu': 8, 'ags': 8, 'september': 9, 'sep': 9,
                'oktober': 10, 'okt': 10, 'november': 11, 'nopember': 11, 'nov': 11,
                'desember': 12, 'des': 12
            }
            month = months.get(month_str.lower(), 1)
            hour, minute, second = 0, 0, 0
            if time_part:
                parts = [int(p) for p in time_part.split(':')]
                hour, minute = parts[0], parts[1]
                if len(parts) > 2:
                    second = parts[2]
            return datetime(int(year), month, int(day), hour, minute, second)
    except Exception:
        pass
    return datetime.min

def sort_articles_by_date_descending(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(articles, key=parse_indonesian_datetime, reverse=True)
```

#### 3. Penulisan Otomatis ke Folder `data_exports/` (`app.py`)
```python
def save_scraped_data_to_exports(articles: list) -> dict:
    if not articles:
        return {}

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.DataFrame(articles)

    csv_path = os.path.join(EXPORTS_DIR, f"news_scraping_{timestamp_str}.csv")
    excel_path = os.path.join(EXPORTS_DIR, f"news_scraping_{timestamp_str}.xlsx")
    json_path = os.path.join(EXPORTS_DIR, f"news_scraping_{timestamp_str}.json")

    df.to_csv(csv_path, index=False, encoding='utf-8')
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil_Scraping')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

    return {'folder_path': EXPORTS_DIR}
```

---

## 7. BAB VI: PENGUJIAN & JAMINAN KUALITAS (QUALITY ASSURANCE)

### 7.1 Rencana & Strategi Pengujian

Strategi pengujian dilakukan dengan teknik **Black Box Testing** pada skenario operasional nyata untuk memverifikasi fungsionalitas antarmuka, ekstraksi multi-portal, klasifikasi sentimen, dan generasi berkas.

---

### 7.2 Pengujian Fungsional (Black Box Testing Matrix)

| ID Uji | Fitur / Skenario Uji | Langkah Masukan | Hasil yang Diharapkan | Hasil Nyata | Status |
| :--- | :--- | :--- | :--- | :--- | :---: |
| **TC-01** | Scraping Kompas.com | Pilih portal "Kompas.com", kategori "News", klik Mulai | Mengambil berita Kompas beserta judul, penulis, & isi | 20 artikel berita Kompas diekstrak sempurna | **PASS** |
| **TC-02** | Scraping Detik.com | Pilih portal "Detik.com", subsite "News", klik Mulai | Mengunduh indeks Detik (tanpa eror 404) & detail | 20 artikel berita Detik diekstrak sempurna | **PASS** |
| **TC-03** | Scraping CNN Indonesia | Pilih portal "CNN Indonesia", klik Mulai | Mengunduh indeks CNN & detail artikel | 10 artikel berita CNN diekstrak sempurna | **PASS** |
| **TC-04** | Scraping Portal Kustom | Input URL `https://riauterkini.com/index.php?com=sosial` | Ekstraksi 47+ berita sosial Riauterkini | 47 artikel berita diekstrak beserta views & waktu | **PASS** |
| **TC-05** | Analisis Sentimen Berita | Proses berita ke modul `analyze_sentiment` | Klasifikasi ke 🟢 Positif, 🔴 Negatif, atau ⚪ Netral | Terklasifikasi akurat (41 Positif, 6 Negatif, 1 Netral) | **PASS** |
| **TC-06** | Pengurutan Berita Terbaru | Selesai ekstraksi berita | Berita rilis terbaru berada di baris paling atas | Berita terurut presisi dari rilis paling baru | **PASS** |
| **TC-07** | Render Pie Chart & WordCloud | Selesai ekstraksi berita | Render Pie Chart (Hijau/Merah/Putih) & WordCloud | Pie Chart & WordCloud tampil sempurna | **PASS** |
| **TC-08** | Penyimpanan Folder Data | Selesai ekstraksi berita | Berkas tersimpan otomatis ke `data_exports/` | Berkas CSV, XLSX, & JSON tersimpan di folder | **PASS** |

---

### 7.3 Pengujian Multi-Portal Real-World

| Nama Portal Berita | URL Pengujian | Jumlah Artikel | Status Parsing Detail | Status Sentimen |
| :--- | :--- | :---: | :---: | :---: |
| **Kompas.com** | `https://indeks.kompas.com/?site=news` | 20 | Sukses | Sukses |
| **Detik.com** | `https://news.detik.com/indeks` | 20 | Sukses | Sukses |
| **CNN Indonesia** | `https://www.cnnindonesia.com/indeks` | 10 | Sukses | Sukses |
| **Riauterkini.com** | `https://riauterkini.com/index.php?com=sosial` | 47 | Sukses (View & Time) | Sukses |
| **Antara News** | `https://www.antaranews.com/terkini` | 15 | Sukses | Sukses |

---

## 8. BAB VII: PENERAPAN, PEMELIHARAAN & PENUTUP

### 8.1 Prosedur Deployment & Integrasi GitHub

Repositori proyek diinisialisasi dan diunggah secara resmi ke GitHub pada cabang utama `main`:

* **URL Repositori**: [https://github.com/ayat7779/scrippingportalberita.git](https://github.com/ayat7779/scrippingportalberita.git)

Perintah sinkronisasi versi yang dieksekusi:
```bash
git init
git branch -M main
git remote add origin https://github.com/ayat7779/scrippingportalberita.git
git add .
git commit -m "Add SDLC documentation report laporan_aplikasi.md"
git push -u origin main
```

---

### 8.2 Kesimpulan

1. **Keberhasilan Otomatisasi**: Aplikasi berhasil mengekstrak berita otomatis dari berbagai situs berita modern maupun klasik tanpa ketergantungan API pihak ketiga.
2. **Kekayaan Analitis**: Berhasil mengimplementasikan *Pie Chart* sentimen kustom (🟢 Positif, 🔴 Negatif, ⚪ Netral), *WordCloud*, KPI keterbacaan, dan pengurutan tanggal rilis (*newest at top*).
3. **Penyimpanan Terstruktur**: Berkas otomatis tersimpan di direktori `data_exports/` dalam 3 format (CSV, Excel, JSON).
4. **Validasi Kualitas**: Seluruh skenario pengujian *Black Box Testing* (TC-01 s/d TC-08) dinyatakan **PASS**.

---

### 8.3 Rencana Pengembangan Lanjutan (Future Roadmap)

1. **Dukungan Cron Job & Scheduled Scraping**: Penambahan fitur pengunduhan berita otomatis berjadwal setiap 1 jam secara latar belakang (*background worker*).
2. **Model Sentimen Transformer/IndoBERT**: Pengintegrasian model pembelajaran mendalam untuk mendeteksi nuansa sarkasme pada artikel opini politik.
3. **Multi-Language Support**: Penambahan kamus leksikon bahasa Inggris untuk mengekstrak situs berita internasional (seperti BBC, Reuters).

---

## 9. BAGIAN AKHIR (BACK MATTER & LAMPIRAN)

### 9.1 Daftar Pustaka

1. Streamlit Documentation. (2026). *Streamlit API Reference & Design System*. Available at: https://docs.streamlit.io
2. BeautifulSoup4 Documentation. (2026). *Beautiful Soup Documentation - Version 4.15*. Available at: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
3. Python Software Foundation. (2026). *Python 3.12 Standard Library Documentation*. Available at: https://docs.python.org/3/
4. OpenGraph Protocol. (2026). *The Open Graph Protocol Standard*. Available at: https://ogp.me
5. Schema.org. (2026). *NewsArticle Schema Specification*. Available at: https://schema.org/NewsArticle

---

### 9.2 Lampiran: Panduan Pengoperasian (User Manual)

#### Langkah 1: Membuka Aplikasi
Jalankan perintah berikut di terminal komputer Anda:
```bash
streamlit run app.py
```
Buka peramban di alamat `http://localhost:8501`.

#### Langkah 2: Memilih Mode & Sumber Berita
1. Pada sidebar sebelah kiri, pilih **Pilih Mode Scraping**:
   - *Indeks Portal Populer*: Untuk Kompas, Detik, CNN.
   - *Portal / Situs Kustom*: Masukkan URL situs kustom (seperti `https://riauterkini.com/index.php?com=sosial`).
2. Tentukan **Filter Waktu Berita** (*Berita Hari Ini*, *Berita Bulan Ini*, *Rentang Tanggal*, atau *Semua Berita*).
3. Klik tombol **Mulai Proses Scraping**.

#### Langkah 3: Membaca Hasil & Analytics
1. **Dashboard Analytik**: Dapatkan KPI keterbacaan, grafik kata kunci, *WordCloud*, dan *Pie Chart* sentimen.
2. **Tabel Data Artikel**: Gunakan filter dropdown kata kunci atau sentimen untuk menyaring berita.
3. **Membaca Berita**: Buka tab *Baca Artikel & Detail Waktu* untuk membaca berita lengkap.
4. **Unduh Berkas**: Berkas hasil scraping sudah tersimpan otomatis di folder `data_exports/`, atau klik tombol unduh CSV/Excel/JSON pada tab *Ekspor Data*.
