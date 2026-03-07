from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QLineEdit, QTableWidget, QTableWidgetItem,
    QProgressBar, QLabel, QFileDialog, QSpinBox
)

#from utils.worker import ScraperWorker
#from scraper.scraper import NewsScraper
#from cleaner.data_cleaner import DataCleaner
#from storage.exporter import Exporter


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("News Scraper")
        self.resize(900,600)

        self.data = []

        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Input News Homepage URL")

        self.limit_input = QSpinBox()
        self.limit_input.setMaximum(500)
        self.limit_input.setValue(20)

        self.start_btn = QPushButton("Start Scraping")
        self.export_btn = QPushButton("Export CSV")

        self.progress = QProgressBar()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels([
            "Title","Date","Content"
        ])

        layout.addWidget(QLabel("URL"))
        layout.addWidget(self.url_input)

        layout.addWidget(QLabel("Limit Article"))
        layout.addWidget(self.limit_input)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.progress)
        layout.addWidget(self.table)
        layout.addWidget(self.export_btn)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.start_btn.clicked.connect(self.start_scraping)
        self.export_btn.clicked.connect(self.export_csv)

    def start_scraping(self):

        url = self.url_input.text()
        limit = self.limit_input.value()

        self.table.setRowCount(0)
        self.data.clear()

#        scraper = NewsScraper(url, limit)

 #       self.worker = ScraperWorker(scraper)

        self.worker.progress.connect(self.update_progress)
        self.worker.result.connect(self.add_table_row)

        self.worker.start()

    def update_progress(self,value):
        self.progress.setValue(value)

    def add_table_row(self,article):

#        article = DataCleaner.clean_article(article)

        row = self.table.rowCount()
        self.table.insertRow(row)

        self.table.setItem(row,0,QTableWidgetItem(article["title"]))
        self.table.setItem(row,1,QTableWidgetItem(article["date"]))
        self.table.setItem(row,2,QTableWidgetItem(article["content"][:200]))

        self.data.append(article)

    def export_csv(self):

        filename,_ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            "",
            "CSV Files (*.csv)"
        )

#        if filename:
            #Exporter.export_csv(self.data,filename)