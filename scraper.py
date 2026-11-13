import requests
from bs4 import BeautifulSoup
import time
import re
import json
from datetime import datetime, date
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Any, Optional, Callable

DEFAULT_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

SUPPORTED_PORTALS = {
    "Kompas.com": "kompas",
    "Detik.com": "detik",
    "CNN Indonesia": "cnn",
    "🌐 Situs / Portal Kustom": "custom"
}

KOMPAS_CATEGORIES = {
    'Semua Kategori': 'all',
    'News / Berita Utama': 'news',
    'Ekonomi & Bisnis': 'ekonomi',
    'Teknologi (Tekno)': 'teknologi',
    'Otomotif': 'otomotif',
    'Olahraga (Bola)': 'bola',
    'Edukasi': 'edukasi',
    'Gaya Hidup (Lifestyle)': 'lifestyle',
    'Kesehatan': 'health',
    'Properti': 'properti'
}

DETIK_CATEGORIES = {
    'Detik News (Utama)': 'news',
    'Detik Finance (Ekonomi)': 'finance',
    'Detik Inet (Teknologi)': 'inet',
    'Detik Hot (Hiburan)': 'hot',
    'Detik Sport (Olahraga)': 'sport',
    'Detik Health (Kesehatan)': 'health',
    'Detik Oto (Otomotif)': 'oto'
}

NAV_KEYWORDS = [
    'home', 'redaksi', 'pedoman', 'kontak', 'about', 'privacy',
    'disclaimer', 'tentang', 'iklan', 'siber', 'syarat', 'bantuan',
    'hubungi', 'login', 'register', 'masuk', 'daftar', 'peta situs',
    'site map', 'facebook', 'twitter', 'instagram', 'youtube'
]

POSITIVE_WORDS = set([
    'berhasil', 'raih', 'penghargaan', 'apresiasi', 'sukses', 'prestasi', 'menang',
    'bantuan', 'tumbuh', 'naik', 'sehat', 'bangun', 'dukung', 'damai', 'solusi',
    'sinergi', 'resmi', 'terwujud', 'terbaik', 'semarak', 'aman', 'maju', 'bagus',
    'pembangunan', 'mulus', 'apresiasi', 'sinergitas', 'bersejarah', 'terobosan',
    'kelancaran', 'unggul', 'pulih', 'senang', 'bangga', 'resmi', 'penyegaran', 'inovasi'
])

NEGATIVE_WORDS = set([
    'kasus', 'narkoba', 'tewas', 'korban', 'kecelakaan', 'kemacetan', 'karhutla',
    'kebakaran', 'ditangkap', 'geledah', 'tersangka', 'dugaan', 'masalah', 'rugi',
    'rusak', 'bencana', 'tuntut', 'protes', 'kritik', 'krisis', 'sabu', 'bahaya',
    'maut', 'tersengat', 'listrik', 'macet', 'ancaman', 'kejahatan', 'menderita',
    'kecewa', 'buruk', 'gagal', 'pemakzulan', 'disorot', 'darurat', 'ancam', 'ditahan'
])

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

def parse_indonesian_datetime(item: Dict[str, Any]) -> datetime:
    """Helper to parse Indonesian date & time strings into a comparable datetime object."""
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
                hour = parts[0]
                minute = parts[1]
                if len(parts) > 2:
                    second = parts[2]
            return datetime(int(year), month, int(day), hour, minute, second)

        m_slash = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})(?:\s+(\d{1,2}:\d{2}))?', combined)
        if m_slash:
            day, month, year, time_part = m_slash.groups()
            hour, minute = 0, 0
            if time_part:
                parts = [int(p) for p in time_part.split(':')]
                hour, minute = parts[0], parts[1]
            return datetime(int(year), int(month), int(day), hour, minute)

    except Exception:
        pass

    return datetime.min

def sort_articles_by_date_descending(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Sort list of article dictionaries descending (newest articles at the top)."""
    return sorted(articles, key=parse_indonesian_datetime, reverse=True)

def filter_articles_by_date_range(
    articles: List[Dict[str, Any]],
    filter_type: str = "Semua Berita (Tanpa Batas)",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """Filter articles based on release date criteria."""
    if not articles or filter_type == "Semua Berita (Tanpa Batas)":
        return articles

    filtered = []
    now = datetime.now()
    today_date = now.date()
    current_year, current_month = now.year, now.month

    for art in articles:
        dt = parse_indonesian_datetime(art)
        if dt == datetime.min:
            filtered.append(art)
            continue

        art_date = dt.date()

        if filter_type == "Berita Hari Ini":
            if art_date == today_date:
                filtered.append(art)

        elif filter_type == "Berita Bulan Ini":
            if dt.year == current_year and dt.month == current_month:
                filtered.append(art)

        elif filter_type == "Rentang Tanggal Kustom":
            if start_date and end_date:
                if start_date <= art_date <= end_date:
                    filtered.append(art)
            elif start_date:
                if art_date >= start_date:
                    filtered.append(art)
            elif end_date:
                if art_date <= end_date:
                    filtered.append(art)
            else:
                filtered.append(art)

    return filtered

def is_probable_article_url(full_url: str, title: str, portal_url: str) -> bool:
    """Helper to validate if a link is an actual news article page."""
    u_lower = full_url.lower()
    t_lower = title.lower()

    root_domain = urlparse(portal_url).scheme + '://' + urlparse(portal_url).netloc
    if full_url.rstrip('/') in [portal_url.rstrip('/'), root_domain.rstrip('/'), root_domain + '/index.php']:
        return False

    if any(nav in t_lower for nav in NAV_KEYWORDS):
        return False

    if 'riauterkini.com' in u_lower:
        return 'id_news=' in u_lower or 'com=isi' in u_lower

    return True

class UniversalNewsScraper:
    def __init__(self, headers: Optional[Dict[str, str]] = None, delay: float = 0.5):
        self.headers = headers or DEFAULT_HEADERS
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    # -------------------------------------------------------------
    # 1. KOMPAS.COM SCRAPER
    # -------------------------------------------------------------
    def scrape_kompas(
        self,
        category_code: str = 'all',
        date_str: Optional[str] = None,
        max_pages: int = 3,
        fetch_details: bool = True,
        progress_cb: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        articles = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            url = f"https://indeks.kompas.com/?site={category_code}&page={page}"
            if date_str:
                url += f"&date={date_str}"

            if progress_cb:
                progress_cb(page, max_pages, f"[Kompas.com] Mengambil indeks halaman {page}/{max_pages}...")

            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200:
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.find_all('div', class_='articleItem')
                if not items:
                    break

                for item in items:
                    link_el = item.find('a', class_='article-link') or item.find('a')
                    if not link_el:
                        continue
                    link = link_el.get('href', '').strip()
                    if not link or not link.startswith('http'):
                        continue

                    title_el = item.find('h2', class_='articleTitle') or item.find('h3', class_='articleTitle') or item.find('h2') or item.find('h3') or link_el
                    title = title_el.text.strip() if title_el else ''

                    cat_el = item.find('div', class_='articlePost-subtitle') or item.find('div', class_='articleCategory')
                    category = cat_el.text.strip() if cat_el else 'Umum'

                    date_el = item.find('div', class_='articlePost-date') or item.find('div', class_='articleDate')
                    date_str_val = date_el.text.strip() if date_el else ''

                    img_el = item.find('img')
                    img_url = (img_el.get('src') or img_el.get('data-src') or '') if img_el else ''

                    if link not in seen_urls and title:
                        seen_urls.add(link)
                        articles.append({
                            'source': 'Kompas.com',
                            'title': title,
                            'url': link,
                            'category': category,
                            'publish_date': date_str_val,
                            'publish_time': 'Belum Diambil',
                            'view_count': 'Tidak Ditampilkan',
                            'sentiment': analyze_sentiment(title),
                            'image_url': img_url,
                            'author': 'Belum Diambil',
                            'content': '',
                            'paragraph_count': 0
                        })
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error scraping Kompas: {e}")
                break

        if fetch_details and articles:
            self._fetch_batch_details(articles, progress_cb)

        return sort_articles_by_date_descending(articles)

    # -------------------------------------------------------------
    # 2. DETIK.COM SCRAPER
    # -------------------------------------------------------------
    def scrape_detik(
        self,
        subsite: str = 'news',
        max_pages: int = 3,
        fetch_details: bool = True,
        progress_cb: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        articles = []
        seen_urls = set()

        base_sub = subsite if subsite != 'news' else 'news'

        for page in range(1, max_pages + 1):
            if page == 1:
                url = f"https://{base_sub}.detik.com/indeks"
            else:
                url = f"https://{base_sub}.detik.com/indeks?page={page}"

            if progress_cb:
                progress_cb(page, max_pages, f"[Detik.com] Mengambil indeks halaman {page}/{max_pages}...")

            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200:
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('article, .list-content__item, .media, .media_link')
                if not items:
                    break

                for item in items:
                    title_el = item.find('h3') or item.find('h2') or item.find('a')
                    link_el = item.find('a')
                    if not title_el or not link_el:
                        continue

                    link = link_el.get('href', '').strip()
                    title = title_el.text.strip()
                    if not link or not title or len(title) < 10:
                        continue

                    img_el = item.find('img')
                    img_url = (img_el.get('src') or img_el.get('data-src') or '') if img_el else ''

                    date_el = item.find('span', class_='date') or item.find('div', class_='media__date')
                    date_val = date_el.text.strip() if date_el else ''

                    if link not in seen_urls:
                        seen_urls.add(link)
                        articles.append({
                            'source': 'Detik.com',
                            'title': title,
                            'url': link,
                            'category': subsite.upper(),
                            'publish_date': date_val,
                            'publish_time': 'Belum Diambil',
                            'view_count': 'Tidak Ditampilkan',
                            'sentiment': analyze_sentiment(title),
                            'image_url': img_url,
                            'author': 'Belum Diambil',
                            'content': '',
                            'paragraph_count': 0
                        })
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error scraping Detik: {e}")
                break

        if fetch_details and articles:
            self._fetch_batch_details(articles, progress_cb)

        return sort_articles_by_date_descending(articles)

    # -------------------------------------------------------------
    # 3. CNN INDONESIA SCRAPER
    # -------------------------------------------------------------
    def scrape_cnn(
        self,
        max_pages: int = 3,
        fetch_details: bool = True,
        progress_cb: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        articles = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            if page == 1:
                url = "https://www.cnnindonesia.com/indeks"
            else:
                url = f"https://www.cnnindonesia.com/indeks?page={page}"

            if progress_cb:
                progress_cb(page, max_pages, f"[CNN Indonesia] Mengambil indeks halaman {page}/{max_pages}...")

            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200:
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.find_all('article')
                if not items:
                    break

                for item in items:
                    link_el = item.find('a')
                    title_el = item.find('h2') or item.find('h3') or link_el
                    if not link_el or not title_el:
                        continue

                    link = link_el.get('href', '').strip()
                    title = title_el.text.strip()
                    if not link or not title or len(title) < 10:
                        continue

                    img_el = item.find('img')
                    img_url = (img_el.get('src') or img_el.get('data-src') or '') if img_el else ''

                    if link not in seen_urls:
                        seen_urls.add(link)
                        articles.append({
                            'source': 'CNN Indonesia',
                            'title': title,
                            'url': link,
                            'category': 'CNN News',
                            'publish_date': '',
                            'publish_time': 'Belum Diambil',
                            'view_count': 'Tidak Ditampilkan',
                            'sentiment': analyze_sentiment(title),
                            'image_url': img_url,
                            'author': 'Belum Diambil',
                            'content': '',
                            'paragraph_count': 0
                        })
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error scraping CNN: {e}")
                break

        if fetch_details and articles:
            self._fetch_batch_details(articles, progress_cb)

        return sort_articles_by_date_descending(articles)

    # -------------------------------------------------------------
    # 4. UNIVERSAL / CUSTOM PORTAL SCRAPER (Handles any news site!)
    # -------------------------------------------------------------
    def scrape_custom_portal(
        self,
        portal_url: str,
        fetch_details: bool = True,
        progress_cb: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        """Scrape all articles available on ANY user-provided news portal URL."""
        articles = []
        seen_urls = set()

        if progress_cb:
            progress_cb(1, 1, f"Mengunduh & menganalisis struktur portal: {portal_url}...")

        try:
            resp = self.session.get(portal_url, timeout=10)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, 'html.parser')
            site_name = urlparse(portal_url).netloc.replace('www.', '')

            # Strategy 1: Container search
            candidates = soup.select('article, .article, .post, .news-item, .card, .list-item, .media, .item')
            for cand in candidates:
                title_el = cand.find(['h1', 'h2', 'h3', 'h4', 'b', 'strong']) or cand.find('a')
                link_el = cand if cand.name == 'a' else cand.find('a')
                if not title_el or not link_el:
                    continue

                title = title_el.text.strip()
                link = link_el.get('href', '').strip()
                if not link or not title or len(title) < 15:
                    continue

                full_url = urljoin(portal_url, link)
                if full_url in seen_urls or not full_url.startswith('http'):
                    continue

                if not is_probable_article_url(full_url, title, portal_url):
                    continue

                seen_urls.add(full_url)
                img_el = cand.find('img')
                img_url = urljoin(portal_url, (img_el.get('src') or img_el.get('data-src') or '')) if img_el else ''

                articles.append({
                    'source': site_name,
                    'title': title,
                    'url': full_url,
                    'category': 'Kustom',
                    'publish_date': '',
                    'publish_time': 'Belum Diambil',
                    'view_count': 'Tidak Ditampilkan',
                    'sentiment': analyze_sentiment(title),
                    'image_url': img_url,
                    'author': 'Belum Diambil',
                    'content': '',
                    'paragraph_count': 0
                })

            # Strategy 2: Scan all <a> links
            for a in soup.find_all('a'):
                href = a.get('href', '').strip()
                title = a.text.strip()

                if not href or not title or len(title) < 15:
                    continue

                full_url = urljoin(portal_url, href)
                if full_url in seen_urls or not full_url.startswith('http'):
                    continue

                if not is_probable_article_url(full_url, title, portal_url):
                    continue

                seen_urls.add(full_url)
                img_el = a.find('img') or (a.parent.find('img') if a.parent else None)
                img_url = urljoin(portal_url, (img_el.get('src') or img_el.get('data-src') or '')) if img_el else ''

                articles.append({
                    'source': site_name,
                    'title': title,
                    'url': full_url,
                    'category': 'Kustom',
                    'publish_date': '',
                    'publish_time': 'Belum Diambil',
                    'view_count': 'Tidak Ditampilkan',
                    'sentiment': analyze_sentiment(title),
                    'image_url': img_url,
                    'author': 'Belum Diambil',
                    'content': '',
                    'paragraph_count': 0
                })

        except Exception as e:
            print(f"Error scraping custom portal {portal_url}: {e}")

        if fetch_details and articles:
            self._fetch_batch_details(articles, progress_cb)

        return sort_articles_by_date_descending(articles)

    # -------------------------------------------------------------
    # 5. SEARCH ENGINE SCRAPER
    # -------------------------------------------------------------
    def scrape_search(
        self,
        keyword: str,
        portal_target: str = 'kompas',
        max_pages: int = 2,
        fetch_details: bool = True,
        progress_cb: Optional[Callable] = None
    ) -> List[Dict[str, Any]]:
        articles = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            if portal_target == 'detik':
                url = f"https://www.detik.com/search/searchall?query={keyword}&page={page}"
            else:
                url = f"https://search.kompas.com/search/?q={keyword}&page={page}"

            if progress_cb:
                progress_cb(page, max_pages, f"Mencari kata kunci '{keyword}' di {portal_target.capitalize()} (Hal {page}/{max_pages})...")

            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200:
                    break

                soup = BeautifulSoup(resp.text, 'html.parser')
                items = soup.select('article, .articleItem, .gsc-result, .list-content__item')
                if not items:
                    break

                for item in items:
                    title_el = item.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    link_el = item.find('a') if item.name != 'a' else item
                    if not title_el or not link_el:
                        continue

                    link = link_el.get('href', '').strip()
                    title = title_el.text.strip()
                    if not link or not title or len(title) < 10:
                        continue

                    if link not in seen_urls:
                        seen_urls.add(link)
                        articles.append({
                            'source': portal_target.capitalize(),
                            'title': title,
                            'url': link,
                            'category': 'Search Result',
                            'publish_date': '',
                            'publish_time': 'Belum Diambil',
                            'view_count': 'Tidak Ditampilkan',
                            'sentiment': analyze_sentiment(title),
                            'image_url': '',
                            'author': 'Belum Diambil',
                            'content': '',
                            'paragraph_count': 0
                        })
                time.sleep(self.delay)
            except Exception as e:
                print(f"Error searching: {e}")
                break

        if fetch_details and articles:
            self._fetch_batch_details(articles, progress_cb)

        return sort_articles_by_date_descending(articles)

    # -------------------------------------------------------------
    # 6. UNIVERSAL DETAIL SCRAPER
    # -------------------------------------------------------------
    def scrape_article_detail(self, url: str) -> Dict[str, Any]:
        """Universal Extractor for any news article URL."""
        target_url = url
        if 'kompas.com' in url and '?page=all' not in url:
            target_url = url.split('?')[0] + '?page=all'
        elif 'detik.com' in url and '?single=1' not in url:
            target_url = url.split('?')[0] + '?single=1'

        try:
            resp = self.session.get(target_url, timeout=10)
            if resp.status_code != 200:
                return {}

            soup = BeautifulSoup(resp.text, 'html.parser')

            title, author, raw_date_str, image = '', '', '', ''
            view_count = 'Tidak Ditampilkan'
            publish_date = ''
            publish_time = ''

            # Method A: Parse JSON-LD / Schema.org metadata
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    data = json.loads(script.string or '{}')
                    if isinstance(data, list):
                        data = data[0] if data else {}
                    if isinstance(data, dict):
                        graph = data.get('@graph', [data])
                        for item in graph:
                            if item.get('@type') in ['NewsArticle', 'Article', 'BlogPosting']:
                                title = title or item.get('headline') or item.get('name')
                                raw_date_str = raw_date_str or item.get('datePublished') or item.get('dateCreated')
                                if isinstance(item.get('author'), dict):
                                    author = author or item['author'].get('name')
                                elif isinstance(item.get('author'), str):
                                    author = author or item['author']
                                if isinstance(item.get('image'), dict):
                                    image = image or item['image'].get('url')
                                elif isinstance(item.get('image'), str):
                                    image = image or item['image']
                                elif isinstance(item.get('image'), list) and item['image']:
                                    image = image or (item['image'][0].get('url') if isinstance(item['image'][0], dict) else item['image'][0])
                except Exception:
                    pass

            # Extract View Count and Raw Date Text
            for el in soup.find_all(['div', 'span', 'p', 'small', 'td', 'font']):
                txt = el.text.strip()
                if not txt:
                    continue

                if view_count == 'Tidak Ditampilkan':
                    v_match = re.search(r'(?:view|dibaca|dilihat|views)\s*:\s*([\d\.,]+)', txt, re.I) or re.search(r'([\d\.,]+)\s*(?:kali dibaca|views|x dibaca)', txt, re.I)
                    if v_match:
                        view_count = v_match.group(1).replace('.', '').replace(',', '')

                if ('202' in txt or '201' in txt or 'WIB' in txt or 'Pukul' in txt or 'View' in txt) and len(txt) < 150:
                    if not raw_date_str or 'View' in txt or 'Pukul' in txt or 'WIB' in txt:
                        raw_date_str = txt

            # Parse publish_date & publish_time from raw_date_str
            if raw_date_str:
                time_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?\s*(?:WIB|WITA|WIT)?)', raw_date_str, re.I) or re.search(r'pukul\s*(\d{1,2}:\d{2}(?::\d{2})?)', raw_date_str, re.I)
                if time_match:
                    publish_time = time_match.group(1).strip()

                date_match = re.search(r'([A-Za-z]+,\s*\d{1,2}\s+[A-Za-z]+\s+\d{4})', raw_date_str) or re.search(r'(\d{1,2}\s+[A-Za-z/]+\s+\d{4})', raw_date_str) or re.search(r'(\d{1,2}/\d{1,2}/\d{4})', raw_date_str)
                if date_match:
                    publish_date = date_match.group(1).strip()
                else:
                    publish_date = raw_date_str.split('Pukul')[0].split('View')[0].strip()

            # Method B: Title Fallbacks
            if not title:
                og_t = soup.find('meta', attrs={'property': 'og:title'}) or soup.find('meta', attrs={'name': 'title'})
                if og_t and og_t.get('content'):
                    title = og_t['content']

            if not title:
                h_tag = soup.find(['h1', 'h2'])
                if h_tag:
                    title = h_tag.text.strip()

            if not title:
                for b in soup.find_all(['b', 'strong']):
                    t = b.text.strip()
                    if len(t) > 20 and not any(k in t.lower() for k in ['copyright', 'reserved', 'baca juga', 'update']):
                        title = t
                        break

            if not title and soup.title:
                title = soup.title.text.split('-')[0].split('|')[0].strip()

            # Metadata: Author
            if not author:
                auth_el = soup.find('div', class_=re.compile(r'author|byline|read__author', re.I)) or soup.find('meta', attrs={'name': 'author'})
                if auth_el:
                    author = auth_el.get('content') if auth_el.name == 'meta' else auth_el.text.strip()

            # Metadata: Image
            if not image:
                og_img = soup.find('meta', attrs={'property': 'og:image'})
                if og_img and og_img.get('content'):
                    image = og_img['content']
                else:
                    img_el = soup.find('img')
                    if img_el:
                        image = img_el.get('src') or img_el.get('data-src') or ''

            if image and not image.startswith('http'):
                image = urljoin(url, image)

            # Method C: Extract Paragraph Content
            body = (
                soup.find('div', class_=re.compile(r'read__content|detail__body-text|itp_bodycontent|post-content|article-content|entry-content', re.I))
                or soup.find('article')
                or soup.find('main')
            )

            paragraphs = []
            if body:
                for p in body.find_all('p'):
                    txt = p.text.strip()
                    if len(txt) > 20 and not txt.startswith('Baca juga') and not txt.startswith('Dapatkan update'):
                        paragraphs.append(txt)

            if not paragraphs:
                for p in soup.find_all('p'):
                    txt = p.text.strip()
                    if len(txt) > 25 and not txt.startswith('Baca juga'):
                        paragraphs.append(txt)

            if not paragraphs:
                # Fallback for classic table-based HTML sites (e.g. riauterkini)
                for td in soup.find_all(['td', 'div']):
                    txt = td.text.strip()
                    if len(txt) > 200:
                        lines = [l.strip() for l in txt.split('\n') if len(l.strip()) > 35]
                        if len(lines) >= 2:
                            paragraphs.extend(lines[:15])
                            break

            full_text = "\n\n".join(paragraphs)

            # Cleanup string whitespace
            author = re.sub(r'\s+', ' ', author) if author else 'Tidak Diketahui'
            title = re.sub(r'\s+', ' ', title) if title else 'Artikel News'

            # Re-evaluate sentiment with full text
            sentiment = analyze_sentiment(f"{title} {full_text}")

            res = {
                'title': title,
                'author': author,
                'publish_date': publish_date if publish_date else 'N/A',
                'publish_time': publish_time if publish_time else 'N/A',
                'view_count': view_count,
                'sentiment': sentiment,
                'content': full_text,
                'paragraph_count': len(paragraphs)
            }
            if image:
                res['image_url'] = image

            return res

        except Exception as e:
            print(f"Error extracting detail for {url}: {e}")
            return {}

    def _fetch_batch_details(self, articles: List[Dict[str, Any]], progress_cb: Optional[Callable]):
        total_det = len(articles)
        for idx, art in enumerate(articles, start=1):
            if progress_cb:
                progress_cb(idx, total_det, f"Mengambil isi artikel {idx}/{total_det}: {art['title'][:35]}...")
            detail = self.scrape_article_detail(art['url'])
            if detail:
                art.update(detail)
            time.sleep(self.delay)
