"""
Modul 5 — main.py
──────────────────
AppController: jembatan antara GUI, Scraper, Cleaner, dan Storage.
Tidak berisi logika scraping maupun UI langsung — hanya koordinasi.

Cara menjalankan:
    python main.py
"""

import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QTimer

# ── import modul internal ──
from gui.gui     import NewsScraperWindow
from scraper.scraper import ScraperWorker
from cleaner.cleaner import clean_article
from storage.storage import export_csv, export_json, suggest_filepath


# ──────────────────────────────────────────────────────────────
#  APP CONTROLLER
# ──────────────────────────────────────────────────────────────

class AppController:
    """
    Mengatur alur kerja aplikasi:
    1. Menerima aksi dari GUI (via sinyal)
    2. Menginstruksikan ScraperWorker untuk mulai/berhenti
    3. Meneruskan data artikel ke Cleaner lalu ke GUI
    4. Menginstruksikan Storage untuk export data
    """

    def __init__(self, window: NewsScraperWindow):
        self.window   = window
        self.worker   = None
        self.articles = []        # list artikel bersih
        self.page_count  = 0
        self.elapsed_sec = 0

        self._setup_timer()
        self._connect_signals()
        window.set_running(running=False, has_data=False)

    # ── setup ─────────────────────────────────────────────────

    def _setup_timer(self):
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)

    def _connect_signals(self):
        w = self.window
        w.scrape_requested.connect(self.start_scraping)
        w.stop_requested.connect(self.stop_scraping)
        w.clear_requested.connect(self.clear_all)
        w.export_csv_requested.connect(self.do_export_csv)
        w.export_json_requested.connect(self.do_export_json)

        # override row_detail_requested untuk tampilkan detail artikel
        w.row_detail_requested = self._show_row_detail

    # ── scraping lifecycle ────────────────────────────────────

    def start_scraping(self, url: str, max_articles: int):
        if not url:
            QMessageBox.warning(self.window, "URL Kosong",
                                "Masukkan URL halaman berita terlebih dahulu.")
            return

        # reset state
        self.articles    = []
        self.page_count  = 0
        self.elapsed_sec = 0
        self.window.reset_table()
        self.window.reset_stats()
        self.window.clear_log()
        self.window.set_running(running=True)

        # buat dan jalankan worker
        self.worker = ScraperWorker(url, max_articles)
        self.worker.article_found.connect(self._on_article_found)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.error_signal.connect(self._on_error)

        self.timer.start()
        self.worker.start()
        self.window.set_status(f"⏳ Scraping dimulai: {url}")

    def stop_scraping(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._on_log("🛑 Scraping dihentikan oleh pengguna.")
        self.timer.stop()
        self.window.set_running(running=False, has_data=bool(self.articles))
        self.window.set_status("Scraping dihentikan.")

    def clear_all(self):
        self.articles = []
        self.window.reset_table()
        self.window.reset_stats()
        self.window.clear_log()
        self.window.set_running(running=False, has_data=False)
        self.window.set_status("Data dibersihkan.")

    # ── slots dari ScraperWorker ──────────────────────────────

    def _on_article_found(self, raw_article: dict):
        """
        Terima artikel mentah dari scraper →
        bersihkan via cleaner →
        kirim ke GUI.
        """
        clean = clean_article(raw_article)
        self.articles.append(clean)
        self.window.add_article(clean)
        self.window.set_done_count(len(self.articles))

    def _on_progress(self, current: int, total: int):
        self.window.set_progress(current, total)

    def _on_log(self, msg: str):
        if "Halaman" in msg and "📄" in msg:
            self.page_count += 1
            self.window.set_page_count(self.page_count)
        ts = datetime.now().strftime("%H:%M:%S")
        self.window.append_log(msg, ts)

    def _on_finished(self, total: int):
        self.timer.stop()
        self.window.set_done_count(total)
        self.window.set_running(running=False, has_data=bool(self.articles))
        ts = datetime.now().strftime("%H:%M:%S")
        self.window.append_log(
            f"✅ Selesai! {total} artikel berhasil diambil dalam {self.elapsed_sec} detik.",
            ts
        )
        self.window.set_status(f"✅ Selesai — {total} artikel diambil.")

    def _on_error(self, msg: str):
        self.timer.stop()
        self.window.set_running(running=False, has_data=False)
        QMessageBox.warning(self.window, "Scraping Gagal", msg)
        self.window.set_status("❌ Scraping gagal.")

    def _tick(self):
        self.elapsed_sec += 1
        self.window.set_elapsed(self.elapsed_sec)

    # ── detail artikel ────────────────────────────────────────

    def _show_row_detail(self, row: int):
        if 0 <= row < len(self.articles):
            self.window.show_article_detail(self.articles[row])

    # ── export ────────────────────────────────────────────────

    def do_export_csv(self):
        if not self.articles:
            QMessageBox.information(self.window, "Tidak Ada Data",
                                    "Belum ada data untuk diekspor.")
            return

        default = suggest_filepath('csv')
        path, _ = QFileDialog.getSaveFileName(
            self.window, "Simpan CSV", default, "CSV Files (*.csv)"
        )
        if not path:
            return

        ok, msg = export_csv(self.articles, path)
        if ok:
            self.window.set_status(f"✅ {msg}")
            QMessageBox.information(self.window, "Export Berhasil",
                                    f"{msg}\n\nLokasi: {path}")
        else:
            QMessageBox.critical(self.window, "Gagal Export CSV", msg)

    def do_export_json(self):
        if not self.articles:
            QMessageBox.information(self.window, "Tidak Ada Data",
                                    "Belum ada data untuk diekspor.")
            return

        default = suggest_filepath('json')
        path, _ = QFileDialog.getSaveFileName(
            self.window, "Simpan JSON", default, "JSON Files (*.json)"
        )
        if not path:
            return

        ok, msg = export_json(self.articles, path)
        if ok:
            self.window.set_status(f"✅ {msg}")
            QMessageBox.information(self.window, "Export Berhasil",
                                    f"{msg}\n\nLokasi: {path}")
        else:
            QMessageBox.critical(self.window, "Gagal Export JSON", msg)

    # ── window close ──────────────────────────────────────────

    def handle_close(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)


# ──────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NewsHarvest")

    window     = NewsScraperWindow()
    controller = AppController(window)

    # teruskan closeEvent ke controller
    original_close = window.closeEvent
    def close_event(event):
        controller.handle_close()
        original_close(event)
    window.closeEvent = close_event

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()