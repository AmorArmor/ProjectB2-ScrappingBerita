"""
Modul 3 — cleaner.py
─────────────────────
Modul untuk menormalisasi dan membersihkan data artikel
sebelum ditampilkan di tabel maupun diekspor.
"""

import re
import html
from datetime import datetime


#  TEXT CLEANING

def clean_whitespace(text: str) -> str:
    if not text:
        return ''
    text = html.unescape(text)                    
    text = re.sub(r'\r\n|\r', '\n', text)        
    text = re.sub(r'[ \t]+', ' ', text)           
    text = re.sub(r'\n{3,}', '\n\n', text)        
    return text.strip()


def clean_title(title: str) -> str:
    if not title:
        return '(Judul tidak ditemukan)'
    title = clean_whitespace(title)
    title = re.sub(r'\s*[|\-–—]\s*[\w\s\.]+$', '', title).strip()
    title = title.strip('"\'""''')
    return title if title else '(Judul tidak ditemukan)'


def clean_date(date_str: str) -> str:
    if not date_str or date_str.strip() in ('-', '', 'None'):
        return '-'

    date_str = date_str.strip()

    if re.match(r'\d{2} \w+ \d{4}', date_str):
        return date_str

    iso_patterns = [
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})',   
        r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})',    
        r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2})',           
        r'(\d{4}-\d{2}-\d{2})',                        
    ]
    for pattern in iso_patterns:
        m = re.search(pattern, date_str)
        if m:
            raw = m.group(1)
            fmts = [
                '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M', '%Y-%m-%d',
            ]
            for fmt in fmts:
                try:
                    dt = datetime.strptime(raw, fmt)
                    return dt.strftime('%d %b %Y %H:%M') + ' WIB'
                except ValueError:
                    continue

    return date_str[:50]


def clean_content(content: str) -> str:
    if not content:
        return '(Konten tidak ditemukan)'

    content = clean_whitespace(content)

    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if len(stripped) < 8 and not stripped[-1].isalnum():
            continue
        noise_patterns = [
            r'^(baca juga|lihat juga|advertisement|iklan|sponsored|artikel terkait)',
            r'^(share|tweet|copy link|whatsapp|facebook|twitter)',
            r'^(loading|please wait|tunggu)',
        ]
        is_noise = any(
            re.match(p, stripped.lower()) for p in noise_patterns
        )
        if not is_noise:
            cleaned_lines.append(stripped)

    return '\n'.join(cleaned_lines)


def make_snippet(content: str, max_chars: int = 120) -> str:
    if not content or content == '(Konten tidak ditemukan)':
        return '(Konten tidak ditemukan)...'
    for line in content.split('\n'):
        line = line.strip()
        if len(line) >= 30:
            snippet = line[:max_chars]
            return snippet + ('...' if len(line) > max_chars else '')
    return content[:max_chars] + '...'


#  ARTICLE CLEANING (entry point)

def clean_article(article: dict) -> dict:
    return {
        'no':      article.get('no', 0),
        'title':   clean_title(article.get('title', '')),
        'date':    clean_date(article.get('date', '')),
        'content': clean_content(article.get('content', '')),
        'snippet': make_snippet(clean_content(article.get('content', ''))),
        'url':     article.get('url', '').strip(),
    }


def clean_articles_batch(articles: list) -> list:
    return [clean_article(a) for a in articles]