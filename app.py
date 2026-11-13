import os
import io
import json
import re
from datetime import datetime, date
from collections import Counter

import streamlit as st
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

from scraper import (
    UniversalNewsScraper,
    KOMPAS_CATEGORIES,
    DETIK_CATEGORIES,
    sort_articles_by_date_descending,
    filter_articles_by_date_range,
    analyze_sentiment
)

st.set_page_config(
    page_title="Universal News Data Scraper & Analytics",
    page_icon=":material/folder_zip:",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Export Directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(PROJECT_ROOT, "data_exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

# Initialize Session State
if "articles" not in st.session_state:
    st.session_state.articles = []

if "scraper" not in st.session_state:
    st.session_state.scraper = UniversalNewsScraper()

INDONESIAN_STOPWORDS = set([
    'dan', 'di', 'ke', 'dari', 'ini', 'itu', 'yang', 'untuk', 'pada', 'dengan',
    'adalah', 'akan', 'juga', 'atau', 'oleh', 'karena', 'sebagai', 'hingga',
    'tersebut', 'saat', 'dalam', 'bisa', 'sudah', 'ada', 'tidak', 'para', 'terkait',
    'kembali', 'resmi', 'dapat', 'menjadi', 'dua', 'satu', 'secara', 'tak', 'jadi',
    'ia', 'kami', 'mereka', 'kita', 'olehnya', 'antara', 'saja', 'pun', 'paling',
    'banyak', 'serta', 'lalu', 'bila', 'jika', 'agar', 'namun', 'selain', 'baru',
    'com', 'https', 'http', 'riauterkini', 'detik', 'kompas', 'cnn', 'baca', 'juga',
    'yang', 'bukan', 'ia', 'kita', 'kami', 'mereka', 'nya', 'si', 'sang', 'pukul',
    'serta', 'oleh', 'pula', 'maka', 'yaitu', 'yakni', 'sehingga', 'melalui', 'telah',
    'tentang', 'bahkan', 'harus', 'dapat', 'satu', 'bisa', 'saat', 'bagi', 'kini', 'lain'
])

def extract_top_keywords(df, top_n=12):
    """Extract most frequent keywords from title and content."""
    text_corpus = ' '.join(df['title'].astype(str) + ' ' + df['content'].fillna('').astype(str))
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text_corpus.lower())
    filtered_words = [w.capitalize() for w in words if w.lower() not in INDONESIAN_STOPWORDS]
    return Counter(filtered_words).most_common(top_n)

def generate_wordcloud_figure(df):
    """Generate WordCloud matplotlib figure from dataframe titles and contents."""
    text_corpus = ' '.join(df['title'].astype(str) + ' ' + df['content'].fillna('').astype(str))

    words = re.findall(r'\b[a-zA-Z]{4,}\b', text_corpus.lower())
    clean_text = ' '.join([w.capitalize() for w in words if w.lower() not in INDONESIAN_STOPWORDS])

    if not clean_text.strip():
        clean_text = "Berita Informasi Publikasi Data"

    wc = WordCloud(
        width=800,
        height=400,
        background_color='white',
        colormap='viridis',
        min_font_size=10,
        max_words=80
    ).generate(clean_text)

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    plt.tight_layout(pad=0)
    return fig

def generate_sentiment_pie_chart(sentiment_counts):
    """Generate Pie Chart matplotlib figure for sentiment distribution."""
    color_map = {
        '🟢 Positif': '#28a745',
        '🔴 Negatif': '#dc3545',
        '⚪ Netral': '#ffffff'
    }

    labels = sentiment_counts.index.tolist()
    counts = sentiment_counts.values.tolist()
    colors = [color_map.get(lbl, '#e0e0e0') for lbl in labels]
    clean_labels = [lbl.replace('🟢 ', '').replace('🔴 ', '').replace('⚪ ', '') for lbl in labels]

    fig, ax = plt.subplots(figsize=(6, 4.5))
    wedges, texts, autotexts = ax.pie(
        counts,
        labels=clean_labels,
        autopct=lambda pct: f"{int(round(float(pct)*sum(counts)/100))} ({float(pct):.1f}%)" if float(pct) > 0 else "",
        startangle=140,
        colors=colors,
        wedgeprops={'edgecolor': '#333333', 'linewidth': 1.5}
    )

    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_weight('bold')
        autotext.set_fontsize(10)

    ax.axis('equal')
    plt.tight_layout(pad=0.5)
    return fig

def save_scraped_data_to_exports(articles: list) -> dict:
    """Save scraped data into data_exports directory in CSV, Excel, and JSON formats."""
    if not articles:
        return {}

    timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    df = pd.DataFrame(articles)

    csv_name = f"news_scraping_{timestamp_str}.csv"
    excel_name = f"news_scraping_{timestamp_str}.xlsx"
    json_name = f"news_scraping_{timestamp_str}.json"

    csv_path = os.path.join(EXPORTS_DIR, csv_name)
    excel_path = os.path.join(EXPORTS_DIR, excel_name)
    json_path = os.path.join(EXPORTS_DIR, json_name)

    # Save CSV
    df.to_csv(csv_path, index=False, encoding='utf-8')

    # Save Excel
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Hasil_Scraping')

    # Save JSON
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)

    return {
        'csv_path': csv_path,
        'excel_path': excel_path,
        'json_path': json_path,
        'folder_path': EXPORTS_DIR
    }

# Custom Styling
st.markdown("""
<style>
    .stAppViewContainer {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1a202c;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.0rem;
        color: #4a5568;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="main-title">:material/folder_zip: Universal News Scraper & Data Exports</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ekstraksi berita otomatis, analisis sentimen, WordCloud visualisasi, serta penyimpanan otomatis ke folder data_exports.</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header(":material/tune: Konfigurasi Sumber & Filter Tanggal", divider="blue")

    scrape_mode = st.segmented_control(
        "Pilih Mode Scraping",
        options=["Indeks Portal Populer", "Pencarian Kata Kunci", "Portal / Situs Kustom", "URL Artikel Langsung"],
        default="Portal / Situs Kustom"
    )

    selected_portal = "Kompas.com"
    selected_category_code = "all"
    search_keyword = ""
    custom_portal_url = ""
    direct_article_url = ""
    fetch_details = True

    # DATE FILTERING OPTIONS
    st.markdown("#### 📅 Filter Waktu Rilis Berita")
    date_filter_option = st.selectbox(
        "Pilih Filter Waktu Berita",
        options=["Berita Hari Ini", "Berita Bulan Ini", "Rentang Tanggal Kustom", "Semua Berita (Tanpa Batas)"],
        index=3
    )

    custom_start_date = None
    custom_end_date = None

    if date_filter_option == "Rentang Tanggal Kustom":
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            custom_start_date = st.date_input("Tanggal Mulai", value=datetime.now().date())
        with col_d2:
            custom_end_date = st.date_input("Tanggal Akhir", value=datetime.now().date())

    st.markdown("---")

    # MODE SPECIFIC CONTROLS
    if scrape_mode == "Indeks Portal Populer":
        selected_portal = st.selectbox(
            "Pilih Portal Berita Utama",
            options=["Kompas.com", "Detik.com", "CNN Indonesia"],
            index=0
        )

        if selected_portal == "Kompas.com":
            cat_label = st.selectbox("Pilih Kategori Kompas", options=list(KOMPAS_CATEGORIES.keys()))
            selected_category_code = KOMPAS_CATEGORIES[cat_label]

        elif selected_portal == "Detik.com":
            cat_label = st.selectbox("Pilih Sub-Portal Detik", options=list(DETIK_CATEGORIES.keys()))
            selected_category_code = DETIK_CATEGORIES[cat_label]

        fetch_details = st.checkbox("Ambil Isi, Sentimen & View Count", value=True)

    elif scrape_mode == "Pencarian Kata Kunci":
        search_portal = st.selectbox("Cari di Portal", options=["Kompas.com", "Detik.com"])
        search_keyword = st.text_input("Kata Kunci Pencarian", value="teknologi", placeholder="Contoh: kecerdasan buatan, ekonomi")
        fetch_details = st.checkbox("Ambil Isi, Sentimen & View Count", value=True)

    elif scrape_mode == "Portal / Situs Kustom":
        st.info("💡 Masukkan URL halaman berita mana saja (misal: riauterkini.com, antaranews.com, liputan6.com, dll).")
        custom_portal_url = st.text_input(
            "URL Portal / Indeks Berita",
            value="https://riauterkini.com/index.php?com=sosial",
            placeholder="https://riauterkini.com/index.php?com=sosial"
        )
        fetch_details = st.checkbox("Ambil Isi, Sentimen & View Count", value=True)

    elif scrape_mode == "URL Artikel Langsung":
        st.info("💡 Masukkan 1 URL artikel berita spesifik dari portal manapun.")
        direct_article_url = st.text_input(
            "URL Artikel Berita",
            placeholder="https://riauterkini.com/index.php?com=isi&id_news=..."
        )

    st.markdown("---")
    start_button = st.button("Mulai Proses Scraping", icon=":material/play_arrow:", width="stretch", type="primary")

# Execute Scraping Logic
if start_button:
    scraper = st.session_state.scraper
    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(current, total, msg):
        progress_bar.progress(int((current / total) * 100))
        status_text.text(f"⏳ {msg}")

    with st.spinner("Proses scraping berjalan..."):
        results = []

        if scrape_mode == "Indeks Portal Populer":
            if selected_portal == "Kompas.com":
                results = scraper.scrape_kompas(
                    category_code=selected_category_code,
                    max_pages=3,
                    fetch_details=fetch_details,
                    progress_cb=update_progress
                )
            elif selected_portal == "Detik.com":
                results = scraper.scrape_detik(
                    subsite=selected_category_code,
                    max_pages=3,
                    fetch_details=fetch_details,
                    progress_cb=update_progress
                )
            elif selected_portal == "CNN Indonesia":
                results = scraper.scrape_cnn(
                    max_pages=3,
                    fetch_details=fetch_details,
                    progress_cb=update_progress
                )

        elif scrape_mode == "Pencarian Kata Kunci":
            if not search_keyword.strip():
                st.warning("Masukkan kata kunci pencarian terlebih dahulu.")
            else:
                portal_key = 'detik' if search_portal == 'Detik.com' else 'kompas'
                results = scraper.scrape_search(
                    keyword=search_keyword.strip(),
                    portal_target=portal_key,
                    max_pages=3,
                    fetch_details=fetch_details,
                    progress_cb=update_progress
                )

        elif scrape_mode == "Portal / Situs Kustom":
            if not custom_portal_url.strip():
                st.warning("Masukkan URL portal berita kustom.")
            else:
                results = scraper.scrape_custom_portal(
                    portal_url=custom_portal_url.strip(),
                    fetch_details=fetch_details,
                    progress_cb=update_progress
                )

        elif scrape_mode == "URL Artikel Langsung":
            if not direct_article_url.strip():
                st.warning("Masukkan URL artikel berita.")
            else:
                detail = scraper.scrape_article_detail(direct_article_url.strip())
                if detail:
                    results = [{
                        'source': 'URL Langsung',
                        'title': detail.get('title', 'Artikel Kustom'),
                        'url': direct_article_url.strip(),
                        'category': 'Direct',
                        'publish_date': detail.get('publish_date', 'N/A'),
                        'publish_time': detail.get('publish_time', 'N/A'),
                        'view_count': detail.get('view_count', 'Tidak Ditampilkan'),
                        'sentiment': detail.get('sentiment', analyze_sentiment(detail.get('title', ''))),
                        'image_url': detail.get('image_url', ''),
                        'author': detail.get('author', 'N/A'),
                        'content': detail.get('content', ''),
                        'paragraph_count': detail.get('paragraph_count', 0)
                    }]

        # 1. Apply Date Range Filtering
        date_filtered_results = filter_articles_by_date_range(
            results,
            filter_type=date_filter_option,
            start_date=custom_start_date,
            end_date=custom_end_date
        )

        # 2. Sort Descending (Newest articles at the top)
        final_articles = sort_articles_by_date_descending(date_filtered_results)

        # 3. Save automatically to data_exports directory
        if final_articles:
            save_scraped_data_to_exports(final_articles)

        st.session_state.articles = final_articles
        progress_bar.progress(100)
        status_text.empty()

    if final_articles:
        st.success(f"Berhasil mengumpulkan {len(final_articles)} artikel berita ({date_filter_option} - Terurut Terbaru ke Terlama)! Data otomatis tersimpan di folder 'data_exports/'.")
    else:
        st.warning(f"Tidak ditemukan artikel pada kriteria '{date_filter_option}'.")

# Display Scraped Results
articles = st.session_state.articles

if articles:
    df_raw = pd.DataFrame(articles)

    # Compute sentiment if missing
    if 'sentiment' not in df_raw.columns:
        df_raw['sentiment'] = df_raw.apply(lambda r: analyze_sentiment(f"{r['title']} {r.get('content', '')}"), axis=1)

    top_keywords_data = extract_top_keywords(df_raw, top_n=12)
    top_keyword_options = ["Semua Kata Kunci"] + [k[0] for k in top_keywords_data]

    # -------------------------------------------------------------
    # 📊 ANALYTICS, SENTIMENT PIE CHART & WORDCLOUD DASHBOARD
    # -------------------------------------------------------------
    st.subheader("📊 Dashboard Analytik, Pie Chart Sentimen & WordCloud", divider="blue")

    # DROPDOWN FILTERS ROW: KEYWORD & SENTIMENT
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        selected_keyword = st.selectbox(
            "🏷️ Filter Berdasarkan Kata Kunci Utama (Dropdown):",
            options=top_keyword_options,
            index=0
        )
    with f_col2:
        selected_sentiment = st.selectbox(
            "🎭 Filter Berdasarkan Sentimen Berita:",
            options=["Semua Sentimen", "🟢 Positif", "🔴 Negatif", "⚪ Netral"],
            index=0
        )

    # Filter dataframe based on dropdown selections
    df = df_raw.copy()
    if selected_keyword != "Semua Kata Kunci":
        mask_kw = df['title'].str.contains(selected_keyword, case=False, na=False) | \
                  df['content'].str.contains(selected_keyword, case=False, na=False)
        df = df[mask_kw]

    if selected_sentiment != "Semua Sentimen":
        df = df[df['sentiment'] == selected_sentiment]

    # 1. KPI CARDS
    total_articles = len(df)
    views_numeric = pd.to_numeric(df['view_count'], errors='coerce').fillna(0)
    total_views = int(views_numeric.sum())

    pos_count = len(df[df['sentiment'] == '🟢 Positif'])
    neg_count = len(df[df['sentiment'] == '🔴 Negatif'])
    neu_count = len(df[df['sentiment'] == '⚪ Netral'])

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    with kpi1:
        st.metric(label="Total Artikel Filtered", value=total_articles)
    with kpi2:
        st.metric(label="🟢 Berita Positif", value=f"{pos_count} ({int((pos_count/total_articles)*100) if total_articles>0 else 0}%)")
    with kpi3:
        st.metric(label="🔴 Berita Negatif", value=f"{neg_count} ({int((neg_count/total_articles)*100) if total_articles>0 else 0}%)")
    with kpi4:
        st.metric(label="⚪ Berita Netral", value=f"{neu_count} ({int((neu_count/total_articles)*100) if total_articles>0 else 0}%)")
    with kpi5:
        st.metric(label="Total Readership / Views", value=f"{total_views:,}" if total_views > 0 else "N/A")

    st.markdown("---")

    # 2. KEYWORD FREQUENCY & WORDCLOUD VISUALIZATION ROW
    col_chart, col_wc = st.columns(2)

    kw_df = pd.DataFrame(top_keywords_data, columns=["Kata Kunci", "Frekuensi"]).set_index("Kata Kunci")

    with col_chart:
        with st.container(border=True):
            st.markdown("#### 🔤 10 Kata / Topik Paling Banyak Dimuat")
            st.bar_chart(kw_df, width="stretch", color="#1f77b4")

    with col_wc:
        with st.container(border=True):
            st.markdown("#### ☁️ WordCloud Visualisasi Kata Kunci")
            wc_fig = generate_wordcloud_figure(df)
            st.pyplot(wc_fig, clear_figure=True, width="stretch")

    st.markdown("---")

    # 3. SENTIMENT PIE CHART & AI SUMMARY ROW
    col_senti_pie, col_summary = st.columns(2)
    sentiment_counts = df_raw['sentiment'].value_counts()

    with col_senti_pie:
        with st.container(border=True):
            st.markdown("#### 🍰 Pie Chart Distribusi Sentimen Berita")
            senti_pie_fig = generate_sentiment_pie_chart(sentiment_counts)
            st.pyplot(senti_pie_fig, clear_figure=True, width="stretch")

    with col_summary:
        with st.container(border=True):
            st.markdown("#### 💡 Analisis & Executive Insights")
            top_3_words = [k[0] for k in top_keywords_data[:3]] if len(top_keywords_data) >= 3 else ["Berita", "Informasi", "Publik"]
            dominant_sentiment = sentiment_counts.index[0] if not sentiment_counts.empty else "⚪ Netral"
            st.markdown(f"""
            - **Sentimen Dominan**: Nada pemberitaan didominasi oleh **{dominant_sentiment}**.
            - **Topik Utama Pembahasan**: Kata kunci terbanyak pada WordCloud didominasi oleh **{top_3_words[0]}**, **{top_3_words[1]}**, dan **{top_3_words[2]}**.
            - **Rincian Nilai Sentimen**:
              - 🟢 **Positif**: **{pos_count} artikel** ({int((pos_count/total_articles)*100) if total_articles>0 else 0}%)
              - 🔴 **Negatif**: **{neg_count} artikel** ({int((neg_count/total_articles)*100) if total_articles>0 else 0}%)
              - ⚪ **Netral**: **{neu_count} artikel** ({int((neu_count/total_articles)*100) if total_articles>0 else 0}%)
            - **Aktivitas Pembaca**: Total keterbacaan mencapai **{total_views:,} views**.
            """)

    st.markdown("---")

    # -------------------------------------------------------------
    # TABEL DATA ARTIKEL (PLACED BELOW ANALYTICS DASHBOARD)
    # -------------------------------------------------------------
    tab_table, tab_viewer, tab_export = st.tabs([
        "📋 Tabel Data Artikel & Sentimen (Terbaru di Atas)",
        "📰 Baca Artikel & Detail Waktu",
        "📥 Ekspor & Penyimpanan Folder Data"
    ])

    with tab_table:
        st.subheader(f"Tabel Data Artikel ({date_filter_option} - Terurut Berita Terakhir Paling Atas)")

        search_filter = st.text_input("Search Tambahan (Cari Judul / Penulis / Portal / Tanggal)", placeholder="Ketik kata kunci pencarian bebas...")

        filtered_df = df.copy()
        if search_filter:
            mask = filtered_df['title'].str.contains(search_filter, case=False, na=False) | \
                   filtered_df['source'].str.contains(search_filter, case=False, na=False) | \
                   filtered_df['publish_date'].str.contains(search_filter, case=False, na=False) | \
                   filtered_df['author'].str.contains(search_filter, case=False, na=False)
            filtered_df = filtered_df[mask]

        display_columns = ['sentiment', 'source', 'title', 'category', 'publish_date', 'publish_time', 'view_count', 'author', 'paragraph_count', 'url']
        available_cols = [c for c in display_columns if c in filtered_df.columns]

        st.dataframe(
            filtered_df[available_cols],
            column_config={
                "sentiment": st.column_config.TextColumn("Sentimen", width="small"),
                "source": st.column_config.TextColumn("Sumber Portal", width="small"),
                "title": st.column_config.TextColumn("Judul Artikel", width="large"),
                "category": st.column_config.TextColumn("Kategori", width="small"),
                "publish_date": st.column_config.TextColumn("Tanggal Rilis", width="medium"),
                "publish_time": st.column_config.TextColumn("Waktu Rilis", width="small"),
                "view_count": st.column_config.TextColumn("Jumlah View", width="small"),
                "author": st.column_config.TextColumn("Penulis", width="medium"),
                "paragraph_count": st.column_config.NumberColumn("Jumlah Paragraf", width="small"),
                "url": st.column_config.LinkColumn("Tautan Asli", width="medium"),
            },
            hide_index=True,
            width="stretch"
        )

    with tab_viewer:
        st.subheader("Detail & Isi Lengkap Artikel")

        selected_title = st.selectbox(
            "Pilih Artikel yang Ingin Dibaca (Terurut Terbaru ke Terlama):",
            options=df['title'].tolist()
        )

        selected_article = df[df['title'] == selected_title].iloc[0]

        with st.container(border=True):
            st.markdown(f"### {selected_article['title']}")

            m1, m2, m3, m4, m5, m6 = st.columns(6)
            with m1:
                st.caption(f"**Sentimen:** {selected_article.get('sentiment', '⚪ Netral')}")
            with m2:
                st.caption(f"**Sumber:** {selected_article.get('source', 'N/A')}")
            with m3:
                st.caption(f"**Tanggal Rilis:** {selected_article.get('publish_date', 'N/A')}")
            with m4:
                st.caption(f"**Waktu Rilis:** {selected_article.get('publish_time', 'N/A')}")
            with m5:
                st.caption(f"**Jumlah View:** {selected_article.get('view_count', 'N/A')}")
            with m6:
                st.caption(f"**Penulis:** {selected_article.get('author', 'N/A')}")

            if selected_article.get('image_url'):
                st.image(selected_article['image_url'], caption=selected_article['title'], alt=selected_article['title'])

            st.markdown("#### Isi Artikel:")
            content = selected_article.get('content', '')
            if content:
                st.write(content)
            else:
                st.info("Isi artikel lengkap belum diambil. Aktifkan centang 'Ambil Isi, Sentimen & View Count' sebelum melakukan scraping.")

            st.markdown(f"[🔗 Buka di Sumber Asli ({selected_article.get('source')})]({selected_article['url']})")

    with tab_export:
        st.subheader("Unduh Data & Lokasi Penyimpanan Berkas")

        with st.container(border=True):
            st.markdown("#### 📁 Folder Penyimpanan Otomatis")
            st.info(f"Seluruh berkas hasil scraping otomatis tersimpan di folder proyek:\n`{EXPORTS_DIR}`")

        st.markdown("#### 📥 Unduh Langsung Berkas Data:")
        col_exp1, col_exp2, col_exp3 = st.columns(3)

        with col_exp1:
            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Unduh Format CSV",
                data=csv_data,
                file_name=f"news_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                icon=":material/csv:",
                width="stretch"
            )

        with col_exp2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Hasil_Scraping')
            excel_data = excel_buffer.getvalue()

            st.download_button(
                label="Unduh Format Excel (XLSX)",
                data=excel_data,
                file_name=f"news_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                icon=":material/table_chart:",
                width="stretch"
            )

        with col_exp3:
            json_data = json.dumps(articles, indent=4, ensure_ascii=False)
            st.download_button(
                label="Unduh Format JSON",
                data=json_data,
                file_name=f"news_scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                icon=":material/code:",
                width="stretch"
            )

else:
    with st.container(border=True):
        st.info("ℹ️ Belum ada data artikel. Pilih portal & mode scraping di panel sebelah kiri lalu klik **Mulai Proses Scraping**.")
