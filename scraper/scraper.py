import re
import time
import requests
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from PyQt5.QtCore import QThread, pyqtSignal


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
}

ARTICLE_CONTENT_SELECTORS = [
    "article", ".article-content", ".post-content", ".entry-content",
    ".content-body", ".article-body", ".news-content", ".detail-content",
    "[itemprop='articleBody']", ".story-body", ".td-post-content",
    ".single-post-content", ".text-content", ".body-text",
]

TITLE_SELECTORS = [
    "h1.article-title", "h1.post-title", "h1.entry-title",
    "h1[itemprop='headline']", ".article-title h1", ".post-title h1",
    "h1", "h2.title",
]

DATE_SELECTORS = [
    "time[datetime]", "time", "[itemprop='datePublished']",
    "[itemprop='dateModified']", ".publish-date", ".post-date",
    ".article-date", ".date", ".published", ".timestamp",
    "span.date", "div.date", ".entry-date", ".news-date",
]

LINK_FILTERS = [
    r'\.(jpg|jpeg|png|gif|svg|webp|mp4|mp3|pdf|zip)$',
    r'/(tag|tags|kategori|category|author|penulis|search|cari)/',
    r'#', r'javascript:', r'mailto:',
]

def _is_article_link(href: str, base_domain: str) -> bool:
    if not href or len(href) < 10:
        return False
    for pattern in LINK_FILTERS:
        if re.search(pattern, href, re.IGNORECASE):
            return False
    parsed = urlparse(href)
    if parsed.netloc and parsed.netloc != base_domain:
        return False
    path = parsed.path.rstrip('/')
    segments = [s for s in path.split('/') if s]
    return len(segments) >= 2


def _extract_links(soup: BeautifulSoup, base_url: str) -> set:
    base_domain = urlparse(base_url).netloc
    links = set()
    for a in soup.find_all('a', href=True):
        href = urljoin(base_url, a['href'].strip())
        if _is_article_link(href, base_domain):
            clean = urlparse(href)._replace(query='', fragment='').geturl()
            links.add(clean)
    return links


def _find_next_page(soup: BeautifulSoup, current_url: str):
    patterns = [
        'a[rel="next"]', 'a.next', 'a.next-page', 'a.pagination-next',
        'li.next a', '.pagination a[aria-label*="Next"]',
        '.pagination a[aria-label*="next"]',
    ]
    for sel in patterns:
        el = soup.select_one(sel)
        if el and el.get('href'):
            return urljoin(current_url, el['href'])
    for a in soup.find_all('a'):
        text = a.get_text(strip=True).lower()
        if text in ('next', '›', '»', 'selanjutnya', 'berikutnya', '→'):
            href = a.get('href', '')
            if href:
                return urljoin(current_url, href)
    return None


def _extract_title(soup: BeautifulSoup) -> str:
    for sel in TITLE_SELECTORS:
        el = soup.select_one(sel)
        if el:
            return el.get_text(strip=True)
    og = soup.find('meta', property='og:title')
    if og:
        return og.get('content', '').strip()
    if soup.title:
        return soup.title.get_text(strip=True)
    return '(Judul tidak ditemukan)'


def _extract_date(soup: BeautifulSoup) -> str:
    for sel in DATE_SELECTORS:
        el = soup.select_one(sel)
        if el:
            dt = el.get('datetime') or el.get('content') or el.get_text(strip=True)
            if dt:
                try:
                    parsed = datetime.fromisoformat(dt[:19])
                    return parsed.strftime('%d %b %Y %H:%M') + ' WIB'
                except Exception:
                    return dt[:50]
    for name in ('article:published_time', 'datePublished'):
        m = (soup.find('meta', attrs={'property': name}) or
             soup.find('meta', attrs={'name': name}))
        if m:
            val = m.get('content', '')[:19]
            try:
                return datetime.fromisoformat(val).strftime('%d %b %Y %H:%M') + ' WIB'
            except Exception:
                return val
    return '-'


def _extract_content(soup: BeautifulSoup) -> str:
    for sel in ARTICLE_CONTENT_SELECTORS:
        el = soup.select_one(sel)
        if el:
            for tag in el(['script', 'style', 'aside', 'figure',
                           'figcaption', 'nav', 'form', 'iframe', 'ins']):
                tag.decompose()
            text = el.get_text(separator='\n', strip=True)
            if len(text) > 200:
                return text[:5000]
    paragraphs = soup.find_all('p')
    text = '\n'.join(
        p.get_text(strip=True) for p in paragraphs
        if len(p.get_text(strip=True)) > 50
    )
    return text[:5000] if text else '(Konten tidak ditemukan)'


class ScraperWorker(QThread):
    article_found    = pyqtSignal(dict)   
    progress_updated = pyqtSignal(int, int)  
    log_message      = pyqtSignal(str)
    finished_signal  = pyqtSignal(int)    
    error_signal     = pyqtSignal(str)

    def __init__(self, url: str, max_articles: int = 50):
        super().__init__()
        self.start_url    = url
        self.max_articles = max_articles
        self._running     = True
        self.session      = requests.Session()
        self.session.headers.update(HEADERS)

    def stop(self):
        self._running = False

    def _get(self, url: str, timeout: int = 15):
        try:
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            resp.raise_for_status()
            return resp
        except Exception as e:
            self.log_message.emit(f"⚠  Gagal ambil {url[:60]}…: {e}")
            return None

    def run(self):
        self.log_message.emit(f"🔍 Mulai scraping: {self.start_url}")

        all_links   = set()
        current_page = self.start_url
        page_num     = 1

        while current_page and self._running:
            self.log_message.emit(f"📄 Halaman {page_num}: {current_page}")
            resp = self._get(current_page)
            if not resp:
                break

            soup = BeautifulSoup(resp.text, 'html.parser')
            new_links = _extract_links(soup, current_page)
            all_links.update(new_links)
            self.log_message.emit(
                f"   ✓ Ditemukan {len(new_links)} link ({len(all_links)} total unik)"
            )

            if len(all_links) >= self.max_articles:
                break

            next_page = _find_next_page(soup, current_page)
            if not next_page or next_page == current_page:
                break
            current_page = next_page
            page_num += 1
            time.sleep(0.5)

        article_links = list(all_links)[:self.max_articles]
        total = len(article_links)
        self.log_message.emit(f"📰 Total artikel ditemukan: {total}")

        if total == 0:
            self.error_signal.emit(
                "Tidak ada artikel yang ditemukan.\n\n"
                "Kemungkinan penyebab:\n"
                "• Halaman menggunakan JavaScript (SPA/React/Vue)\n"
                "• Struktur link tidak dikenali\n"
                "• Situs memblokir bot\n\n"
                "Coba URL halaman kategori atau halaman indeks berita."
            )
            return

        scraped = 0
        for i, url in enumerate(article_links):
            if not self._running:
                break

            self.progress_updated.emit(i + 1, total)
            self.log_message.emit(f"📖 [{i+1}/{total}] {url}")

            resp = self._get(url)
            if not resp:
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            article = {
                'no':      i + 1,
                'title':   _extract_title(soup),
                'date':    _extract_date(soup),
                'content': _extract_content(soup),
                'url':     url,
            }
            self.article_found.emit(article)
            scraped += 1
            time.sleep(0.3)

        self.finished_signal.emit(scraped)
