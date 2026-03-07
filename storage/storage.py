"""
Modul 4 — storage.py
─────────────────────
Bertanggung-jawab atas export dan penyimpanan data hasil scraping.

Fitur:
- Export ke CSV dengan format konsisten sesuai tampilan tabel
- Export ke JSON
- Nama file otomatis dengan timestamp
"""

import csv
import json
import os
from datetime import datetime


# ──────────────────────────────────────────────────────────────
#  KONSTANTA
# ──────────────────────────────────────────────────────────────

# Kolom CSV sesuai urutan tampilan di tabel GUI
CSV_FIELDNAMES = ['no', 'title', 'date', 'snippet', 'url']

# Header yang ramah dibaca manusia (baris pertama CSV)
CSV_HEADERS = {
    'no':      '#',
    'title':   'JUDUL BERITA',
    'date':    'TANGGAL',
    'snippet': 'CUPLIKAN ISI',
    'url':     'URL',
}


# ──────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────

def _default_filename(extension: str) -> str:
    """Buat nama file default dengan timestamp."""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"berita_{ts}.{extension}"


def _prepare_row(article: dict) -> dict:
    """
    Siapkan satu baris data untuk CSV.
    Mapping field artikel → kolom CSV sesuai tampilan tabel.
    """
    return {
        'no':      article.get('no', ''),
        'title':   article.get('title', ''),
        'date':    article.get('date', '-'),
        'snippet': article.get('snippet', article.get('content', '')[:120] + '...'),
        'url':     article.get('url', ''),
    }


# ──────────────────────────────────────────────────────────────
#  EXPORT FUNCTIONS
# ──────────────────────────────────────────────────────────────

def export_csv(articles: list, filepath: str) -> tuple[bool, str]:
    """
    Export daftar artikel ke file CSV.

    Format CSV:
    - Encoding: UTF-8 with BOM (agar Excel Indonesia bisa baca)
    - Header: nama kolom human-readable
    - Kolom: #, JUDUL BERITA, TANGGAL, CUPLIKAN ISI, URL
    - Field yang mengandung koma/newline otomatis di-quote

    Args:
        articles: List dict artikel (sudah melalui cleaner).
        filepath: Path lengkap file .csv tujuan.

    Returns:
        (True, pesan_sukses) atau (False, pesan_error)
    """
    if not articles:
        return False, "Tidak ada data untuk diekspor."

    try:
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=CSV_FIELDNAMES,
                quoting=csv.QUOTE_ALL,       # semua field di-quote → aman untuk koma/newline
                extrasaction='ignore',
            )
            # tulis header dengan nama kolom yang ramah dibaca
            writer.writerow(CSV_HEADERS)

            for article in articles:
                writer.writerow(_prepare_row(article))

        count = len(articles)
        filename = os.path.basename(filepath)
        return True, f"{count} artikel berhasil diekspor ke '{filename}'"

    except PermissionError:
        return False, f"Tidak bisa menulis ke '{filepath}'. File mungkin sedang dibuka."
    except Exception as e:
        return False, f"Gagal export CSV: {e}"


def export_json(articles: list, filepath: str) -> tuple[bool, str]:
    """
    Export daftar artikel ke file JSON (semua field termasuk konten penuh).

    Args:
        articles: List dict artikel.
        filepath: Path lengkap file .json tujuan.

    Returns:
        (True, pesan_sukses) atau (False, pesan_error)
    """
    if not articles:
        return False, "Tidak ada data untuk diekspor."

    try:
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else '.', exist_ok=True)

        # untuk JSON, simpan semua field termasuk content penuh
        export_data = {
            'exported_at': datetime.now().isoformat(),
            'total':       len(articles),
            'articles':    articles,
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        count = len(articles)
        filename = os.path.basename(filepath)
        return True, f"{count} artikel berhasil diekspor ke '{filename}'"

    except Exception as e:
        return False, f"Gagal export JSON: {e}"


def suggest_filepath(extension: str = 'csv', directory: str = '') -> str:
    """
    Sarankan path file default untuk dialog save.

    Args:
        extension: 'csv' atau 'json'
        directory: direktori awal (opsional)

    Returns:
        Path file yang disarankan.
    """
    filename = _default_filename(extension)
    if directory:
        return os.path.join(directory, filename)
    return filename
