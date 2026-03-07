"""
Modul 1 — gui.py
─────────────────
Seluruh komponen tampilan PyQt5.
Tidak berisi logika scraping maupun business logic — hanya UI.

Kelas yang diekspor:
- NewsScraperWindow  : jendela utama aplikasi
- StatCard           : widget kartu statistik
"""

import webbrowser

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QTextEdit, QSplitter, QFrame,
    QStatusBar, QAbstractItemView, QSpinBox, QGroupBox,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QCursor, QFont

# ──────────────────────────────────────────────────────────────
#  TEMA WARNA
# ──────────────────────────────────────────────────────────────

DARK_BG      = "#0d1117"
PANEL_BG     = "#161b22"
ACCENT       = "#58a6ff"
ACCENT2      = "#3fb950"
BORDER       = "#30363d"
TEXT_PRIMARY = "#e6edf3"
TEXT_MUTED   = "#8b949e"
RED_ERR      = "#f85149"

STYLE = f"""
QMainWindow, QWidget {{
    background-color: {DARK_BG};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
}}
QGroupBox {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 8px;
    font-size: 12px;
    color: {TEXT_MUTED};
    font-weight: 600;
    letter-spacing: 0.8px;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}
QLineEdit {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 8px 12px;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}
QLineEdit:focus {{ border-color: {ACCENT}; }}

QPushButton {{
    border-radius: 6px;
    padding: 8px 20px;
    font-size: 13px;
    font-weight: 600;
    border: none;
}}
QPushButton#btn_scrape {{
    background-color: {ACCENT}; color: #0d1117; min-width: 130px;
}}
QPushButton#btn_scrape:hover {{ background-color: #79c0ff; }}
QPushButton#btn_scrape:disabled {{ background-color: #1f6feb; color: #666; }}

QPushButton#btn_stop {{
    background-color: {RED_ERR}; color: white; min-width: 90px;
}}
QPushButton#btn_stop:hover {{ background-color: #ff7b72; }}
QPushButton#btn_stop:disabled {{ background-color: #3d1a1a; color: #666; }}

QPushButton#btn_clear {{
    background-color: {PANEL_BG}; color: {TEXT_MUTED};
    border: 1px solid {BORDER}; min-width: 90px;
}}
QPushButton#btn_clear:hover {{ color: {TEXT_PRIMARY}; border-color: {TEXT_MUTED}; }}

QPushButton#btn_export_csv {{
    background-color: {PANEL_BG}; color: {ACCENT2};
    border: 1px solid {ACCENT2}; min-width: 110px;
}}
QPushButton#btn_export_csv:hover {{ background-color: #1a2e1a; }}

QPushButton#btn_export_json {{
    background-color: {PANEL_BG}; color: #d29922;
    border: 1px solid #d29922; min-width: 110px;
}}
QPushButton#btn_export_json:hover {{ background-color: #2a2000; }}

QTableWidget {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    gridline-color: {BORDER};
    color: {TEXT_PRIMARY};
    font-size: 12px;
    selection-background-color: #1f3250;
    outline: none;
}}
QTableWidget::item {{
    padding: 6px 10px;
    border-bottom: 1px solid {BORDER};
}}
QTableWidget::item:selected {{
    background-color: #1f3250;
    color: {TEXT_PRIMARY};
}}
QHeaderView::section {{
    background-color: #1c2128;
    color: {TEXT_MUTED};
    border: none;
    border-bottom: 2px solid {ACCENT};
    border-right: 1px solid {BORDER};
    padding: 8px 10px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}}
QProgressBar {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 4px;
    height: 8px;
    text-align: center;
    font-size: 10px;
}}
QProgressBar::chunk {{ background-color: {ACCENT}; border-radius: 4px; }}

QTextEdit {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    color: {TEXT_MUTED};
    font-family: 'JetBrains Mono', 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    padding: 8px;
}}
QSplitter::handle {{ background-color: {BORDER}; width: 2px; }}
QScrollBar:vertical {{ background: {DARK_BG}; width: 8px; border-radius: 4px; }}
QScrollBar::handle:vertical {{
    background: #30363d; border-radius: 4px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QStatusBar {{
    background-color: {PANEL_BG}; color: {TEXT_MUTED};
    border-top: 1px solid {BORDER}; font-size: 11px; padding: 2px 10px;
}}
QSpinBox {{
    background-color: {PANEL_BG}; border: 1px solid {BORDER};
    border-radius: 6px; padding: 6px 8px;
    color: {TEXT_PRIMARY}; font-size: 13px;
}}
QSpinBox:focus {{ border-color: {ACCENT}; }}
QSpinBox::up-button, QSpinBox::down-button {{
    background-color: {BORDER}; border: none; border-radius: 3px; width: 16px;
}}
QLabel#header_title {{
    font-size: 22px; font-weight: 800;
    color: {TEXT_PRIMARY}; letter-spacing: -0.5px;
}}
QLabel#header_sub {{ font-size: 12px; color: {TEXT_MUTED}; }}
QLabel#stat_value {{ font-size: 22px; font-weight: 800; color: {ACCENT}; }}
QLabel#stat_label {{ font-size: 10px; color: {TEXT_MUTED}; letter-spacing: 0.8px; }}
"""


# ──────────────────────────────────────────────────────────────
#  WIDGET KUSTOM
# ──────────────────────────────────────────────────────────────

class StatCard(QFrame):
    """Kartu kecil untuk menampilkan satu angka statistik."""

    def __init__(self, label: str, value: str = "0", parent=None):
        super().__init__(parent)
        self.setObjectName("statCard")
        self.setStyleSheet(f"""
            QFrame#statCard {{
                background-color: {PANEL_BG};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(14, 10, 14, 10)

        self.value_lbl = QLabel(value)
        self.value_lbl.setObjectName("stat_value")
        lbl = QLabel(label)
        lbl.setObjectName("stat_label")
        layout.addWidget(self.value_lbl)
        layout.addWidget(lbl)

    def set_value(self, val):
        self.value_lbl.setText(str(val))


class LinkTableItem(QTableWidgetItem):
    """Item tabel khusus untuk kolom URL — bergaya link biru dan bisa diklik."""

    def __init__(self, url: str):
        super().__init__(url)
        self.url = url
        self.setForeground(QColor(ACCENT))
        font = QFont()
        font.setUnderline(True)
        self.setFont(font)
        self.setToolTip(f"Klik untuk membuka: {url}")


# ──────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ──────────────────────────────────────────────────────────────

class NewsScraperWindow(QMainWindow):
    """
    Jendela utama aplikasi NewsHarvest.

    Sinyal yang diterima dari AppController (main.py):
    - Memanggil metode publik: add_article(), set_progress(),
      append_log(), on_finished(), on_error(), reset_ui()
    """

    # sinyal ke controller
    scrape_requested = pyqtSignal(str, int)   # (url, max_articles)
    stop_requested   = pyqtSignal()
    clear_requested  = pyqtSignal()
    export_csv_requested  = pyqtSignal()
    export_json_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NewsHarvest — Web News Scraper")
        self.setMinimumSize(1280, 800)
        self.setStyleSheet(STYLE)
        self._build_ui()
        self._connect_internal()

    # ── build UI ──────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(20, 16, 20, 8)
        root.setSpacing(14)

        root.addLayout(self._build_header())
        root.addLayout(self._build_input_row())
        root.addLayout(self._build_stat_row())
        root.addWidget(self._build_progress_row())
        root.addWidget(self._build_splitter(), stretch=1)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Siap. Masukkan URL dan klik Mulai Scraping.")

    def _build_header(self):
        h = QHBoxLayout()
        dot = QLabel("◉")
        dot.setStyleSheet(f"font-size:28px; color:{ACCENT}; margin-right:6px;")
        title = QLabel("NewsHarvest")
        title.setObjectName("header_title")
        sub = QLabel("Web News Article Scraper  ·  Python + PyQt5  ·  v2.0 Modular")
        sub.setObjectName("header_sub")
        v = QVBoxLayout()
        v.setSpacing(1)
        v.addWidget(title)
        v.addWidget(sub)
        h.addWidget(dot)
        h.addLayout(v)
        h.addStretch()
        return h

    def _build_input_row(self):
        grp = QGroupBox("URL Target")
        layout = QHBoxLayout(grp)
        layout.setContentsMargins(12, 18, 12, 12)
        layout.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Contoh: https://www.detik.com/tag/teknologi  atau  https://tekno.kompas.com"
        )
        layout.addWidget(self.url_input, stretch=1)

        max_lbl = QLabel("Maks.:")
        max_lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px;")
        self.max_spin = QSpinBox()
        self.max_spin.setRange(5, 500)
        self.max_spin.setValue(30)
        self.max_spin.setSuffix("  artikel")
        layout.addWidget(max_lbl)
        layout.addWidget(self.max_spin)

        self.btn_scrape      = QPushButton("▶  Mulai Scraping")
        self.btn_stop        = QPushButton("■  Stop")
        self.btn_clear       = QPushButton("🗑  Bersihkan")
        self.btn_export_csv  = QPushButton("⬇  Export CSV")
        self.btn_export_json = QPushButton("⬇  Export JSON")

        self.btn_scrape.setObjectName("btn_scrape")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_clear.setObjectName("btn_clear")
        self.btn_export_csv.setObjectName("btn_export_csv")
        self.btn_export_json.setObjectName("btn_export_json")

        for btn in (self.btn_scrape, self.btn_stop, self.btn_clear,
                    self.btn_export_csv, self.btn_export_json):
            layout.addWidget(btn)

        outer = QVBoxLayout()
        outer.addWidget(grp)
        return outer

    def _build_stat_row(self):
        h = QHBoxLayout()
        h.setSpacing(12)
        self.card_total   = StatCard("ARTIKEL DITEMUKAN")
        self.card_done    = StatCard("BERHASIL DIAMBIL")
        self.card_pages   = StatCard("HALAMAN DIKUNJUNGI")
        self.card_elapsed = StatCard("WAKTU BERJALAN", "0s")
        for c in (self.card_total, self.card_done, self.card_pages, self.card_elapsed):
            h.addWidget(c)
        return h

    def _build_progress_row(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        lbl = QLabel("Progress:")
        lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px; min-width:60px;")
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress_lbl = QLabel("0 / 0")
        self.progress_lbl.setStyleSheet(f"color:{TEXT_MUTED}; font-size:12px; min-width:60px;")
        layout.addWidget(lbl)
        layout.addWidget(self.progress, stretch=1)
        layout.addWidget(self.progress_lbl)
        return frame

    def _build_splitter(self):
        splitter = QSplitter(Qt.Vertical)

        # ── tabel utama ──
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["#", "JUDUL BERITA", "TANGGAL", "CUPLIKAN ISI", "URL"]
        )
        hh = self.table.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(1, QHeaderView.Stretch)
        hh.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hh.setSectionResizeMode(3, QHeaderView.Stretch)
        hh.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet(
            self.table.styleSheet() +
            f"QTableWidget {{alternate-background-color: #0d1117;}}"
        )
        # ubah cursor jadi pointer ketika hover kolom URL
        self.table.viewport().setCursor(QCursor(Qt.ArrowCursor))
        splitter.addWidget(self.table)

        # ── panel log / detail ──
        log_grp = QGroupBox("Log Aktivitas  —  klik baris untuk detail artikel")
        log_layout = QVBoxLayout(log_grp)
        log_layout.setContentsMargins(8, 14, 8, 8)
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(200)
        log_layout.addWidget(self.log_area)
        splitter.addWidget(log_grp)

        splitter.setSizes([560, 200])
        return splitter

    # ── sinyal internal ───────────────────────────────────────

    def _connect_internal(self):
        """Hubungkan widget ke sinyal yang diteruskan ke controller."""
        self.btn_scrape.clicked.connect(self._emit_scrape)
        self.btn_stop.clicked.connect(self.stop_requested)
        self.btn_clear.clicked.connect(self.clear_requested)
        self.btn_export_csv.clicked.connect(self.export_csv_requested)
        self.btn_export_json.clicked.connect(self.export_json_requested)
        self.url_input.returnPressed.connect(self._emit_scrape)

        # klik sel tabel — buka URL jika kolom 4, tampilkan detail jika kolom lain
        self.table.cellClicked.connect(self._on_cell_clicked)

    def _emit_scrape(self):
        url = self.url_input.text().strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            self.url_input.setText(url)
        self.scrape_requested.emit(url, self.max_spin.value())

    # ── slot tabel ────────────────────────────────────────────

    def _on_cell_clicked(self, row: int, col: int):
        """
        Kolom 4 (URL): buka browser.
        Kolom lain   : tampilkan detail di log panel.
        """
        item = self.table.item(row, col)
        if not item:
            return

        if col == 4:
            # ── buka URL di browser ──
            url = item.text()
            if url.startswith('http'):
                webbrowser.open(url)
                self.statusbar.showMessage(f"🌐 Membuka browser: {url[:80]}…")
        else:
            # ── tampilkan detail di log panel ──
            self.row_detail_requested(row)

    def row_detail_requested(self, row: int):
        """Dipanggil oleh controller untuk menampilkan detail artikel."""
        # controller akan override ini via connect; default: tidak ada aksi
        pass

    # ── metode publik (dipanggil oleh AppController) ──────────

    def add_article(self, article: dict):
        """Tambahkan satu baris artikel ke tabel."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # kolom 0 — nomor
        no_item = QTableWidgetItem(str(article.get('no', row + 1)))
        no_item.setTextAlignment(Qt.AlignCenter)
        no_item.setForeground(QColor(TEXT_MUTED))
        self.table.setItem(row, 0, no_item)

        # kolom 1 — judul
        title_item = QTableWidgetItem(article.get('title', ''))
        self.table.setItem(row, 1, title_item)

        # kolom 2 — tanggal
        date_item = QTableWidgetItem(article.get('date', '-'))
        date_val = article.get('date', '-')
        if date_val != '-':
            date_item.setForeground(QColor(ACCENT2))
        else:
            date_item.setForeground(QColor(TEXT_MUTED))
        self.table.setItem(row, 2, date_item)

        # kolom 3 — cuplikan isi
        snippet_item = QTableWidgetItem(article.get('snippet', ''))
        snippet_item.setForeground(QColor(TEXT_MUTED))
        self.table.setItem(row, 3, snippet_item)

        # kolom 4 — URL (pakai LinkTableItem khusus, bisa diklik)
        url_item = LinkTableItem(article.get('url', ''))
        self.table.setItem(row, 4, url_item)

        self.table.scrollToBottom()

    def show_article_detail(self, article: dict):
        """Tampilkan detail artikel di panel log."""
        self.log_area.setHtml(
            f"<b style='color:{ACCENT}'>{article.get('title','')}</b><br>"
            f"<span style='color:{ACCENT2}'>📅 {article.get('date','-')}</span>"
            f"&nbsp;&nbsp;"
            f"<a href='{article.get('url','')}' "
            f"   style='color:{ACCENT}; text-decoration:underline;'>"
            f"🔗 Buka Artikel</a><br><br>"
            f"<span style='color:{TEXT_PRIMARY}'>"
            f"{article.get('content','')[:600].replace(chr(10),'<br>')}"
            f"…</span>"
        )

    def set_progress(self, current: int, total: int):
        self.progress.setMaximum(total)
        self.progress.setValue(current)
        self.progress_lbl.setText(f"{current} / {total}")
        self.card_total.set_value(total)

    def set_done_count(self, count: int):
        self.card_done.set_value(count)

    def set_page_count(self, count: int):
        self.card_pages.set_value(count)

    def set_elapsed(self, seconds: int):
        if seconds < 60:
            self.card_elapsed.set_value(f"{seconds}s")
        else:
            m, s = divmod(seconds, 60)
            self.card_elapsed.set_value(f"{m}m {s}s")

    def append_log(self, msg: str, timestamp: str = ''):
        self.log_area.append(
            f"<span style='color:{TEXT_MUTED}'>[{timestamp}]</span> {msg}"
        )
        self.statusbar.showMessage(msg[:110])

    def set_status(self, msg: str):
        self.statusbar.showMessage(msg)

    def set_running(self, running: bool, has_data: bool = False):
        """Update state semua tombol sesuai apakah scraping sedang berjalan."""
        self.btn_scrape.setEnabled(not running)
        self.btn_stop.setEnabled(running)
        self.btn_clear.setEnabled(not running)
        self.btn_export_csv.setEnabled(not running and has_data)
        self.btn_export_json.setEnabled(not running and has_data)

    def reset_table(self):
        self.table.setRowCount(0)

    def reset_stats(self):
        self.card_total.set_value(0)
        self.card_done.set_value(0)
        self.card_pages.set_value(0)
        self.card_elapsed.set_value("0s")
        self.progress.setValue(0)
        self.progress_lbl.setText("0 / 0")

    def clear_log(self):
        self.log_area.clear()