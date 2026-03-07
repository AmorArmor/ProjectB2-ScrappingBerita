import sys
from datetime import datetime

from PyQt5.QtWidgets import QApplication, QMessageBox, QFileDialog
from PyQt5.QtCore import QTimer

from gui.gui     import NewsScraperWindow
from scraper.scraper import ScraperWorker
from cleaner.cleaner import clean_article
from storage.storage import export_csv, export_json, suggest_filepath


class AppController:
    def __init__(self, window: NewsScraperWindow):
        self.window   = window
        self.worker   = None
        self.articles = []       
        self.page_count  = 0
        self.elapsed_sec = 0

        self._setup_timer()
        self._connect_signals()
        window.set_running(running=False, has_data=False)

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
        w.row_detail_requested = self._show_row_detail


    def start_scraping(self, url: str, max_articles: int):
        if not url:
            QMessageBox.warning(self.window, "URL Kosong",
                                "Masukkan URL halaman berita terlebih dahulu.")
            return

        self.articles    = []
        self.page_count  = 0
        self.elapsed_sec = 0
        self.window.reset_table()
        self.window.reset_stats()
        self.window.clear_log()
        self.window.set_running(running=True)
        self.worker = ScraperWorker(url, max_articles)
        self.worker.article_found.connect(self._on_article_found)
        self.worker.progress_updated.connect(self._on_progress)
        self.worker.log_message.connect(self._on_log)
        self.worker.finished_signal.connect(self._on_finished)
        self.worker.error_signal.connect(self._on_error)
        self.timer.start()
        self.worker.start()
        self.window.set_status(f"Scraping dimulai: {url}")

    def stop_scraping(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._on_log("Scraping dihentikan oleh pengguna.")
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

    def _on_article_found(self, raw_article: dict):
        """
        Terima artikel mentah dari scraper →
        bersihkan via cleaner →
        kirim ke gui.
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
            f"Selesai! {total} artikel berhasil diambil dalam {self.elapsed_sec} detik.",
            ts
        )
        self.window.set_status(f"Selesai — {total} artikel diambil.")

    def _on_error(self, msg: str):
        self.timer.stop()
        self.window.set_running(running=False, has_data=False)
        QMessageBox.warning(self.window, "Scraping Gagal", msg)
        self.window.set_status("Scraping gagal.")

    def _tick(self):
        self.elapsed_sec += 1
        self.window.set_elapsed(self.elapsed_sec)

    def _show_row_detail(self, row: int):
        if 0 <= row < len(self.articles):
            self.window.show_article_detail(self.articles[row])

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
            self.window.set_status(f"{msg}")
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
            self.window.set_status(f"{msg}")
            QMessageBox.information(self.window, "Export Berhasil",
                                    f"{msg}\n\nLokasi: {path}")
        else:
            QMessageBox.critical(self.window, "Gagal Export JSON", msg)

    def handle_close(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(3000)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NewsHarvest")

    window     = NewsScraperWindow()
    controller = AppController(window)

    original_close = window.closeEvent
    def close_event(event):
        controller.handle_close()
        original_close(event)
    window.closeEvent = close_event

    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()