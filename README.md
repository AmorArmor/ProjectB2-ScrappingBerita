# 📰 NewsHarvest — Web News Article Scraper

NewsHarvest adalah aplikasi *desktop* berbasis antarmuka grafis (GUI) yang dirancang untuk mengekstrak (scraping) artikel berita dari berbagai situs web secara otomatis. Dibangun menggunakan Python dan PyQt5, aplikasi ini menyajikan data hasil *scraping* ke dalam tabel interaktif dan mendukung ekspor data ke format CSV maupun JSON.

## ✨ Fitur Utama

* **Antarmuka Grafis (GUI) Ramah Pengguna:** Tidak perlu berurusan dengan *command line* yang rumit, cukup masukkan URL dan klik tombol mulai.
* **Multithreading:** Proses *scraping* berjalan di *background* (menggunakan `QThread`), sehingga aplikasi tidak akan macet (*freeze*) saat sedang mengambil ratusan artikel.
* **Ekstraksi Data Cerdas:** Mengambil informasi penting seperti Judul Berita, Tanggal Publikasi, Cuplikan Isi (Snippet), dan URL asli artikel.
* **Pembersihan Data Otomatis:** Menghapus elemen HTML yang tidak perlu, menormalkan format tanggal, dan membersihkan teks dari *noise* (iklan, teks navigasi).
* **Ekspor Data Fleksibel:** Simpan hasil *scraping* ke dalam file berformat `.csv` (ramah Excel) atau `.json` hanya dengan satu klik.
* **Tabel Interaktif:** Klik URL di dalam tabel untuk langsung membuka artikel di *browser*, atau klik baris mana saja untuk melihat detail lengkap artikel di panel log.

## 🛠️ Prasyarat & Instalasi

Pastikan **Python 3.x** sudah terinstal di komputermu. Selanjutnya, instal pustaka (*libraries*) pihak ketiga yang dibutuhkan aplikasi ini.

Buka terminal atau *command prompt*, lalu jalankan perintah berikut:

```
pip install requests beautifulsoup4 PyQt5
```

## 🚀 Cara Penggunaan
1. Buka terminal di dalam folder proyek ini.
2. Jalankan aplikasi dengan perintah:
   ```
      python main.py
   ```
3. Masukkan URL Target: Ketik atau paste tautan halaman indeks berita atau kategori (contoh: https://www.detik.com/tag/teknologi atau https://tekno.kompas.com).
4. Tentukan Batas Maksimal: Atur jumlah maksimal artikel yang ingin diambil pada kolom angka (misal: 30 artikel).
5. Mulai Scraping: Klik tombol ▶ Mulai Scraping. Kamu bisa melihat progres dan log aktivitas di panel bagian bawah.
6. Ekspor: Setelah selesai, klik tombol ⬇ Export CSV atau ⬇ Export JSON untuk menyimpan data ke komputermu.

📂 Struktur Proyek (Modular)
Proyek ini dibangun dengan arsitektur modular agar mudah dikembangkan dan dirawat:
- main.py: Titik masuk aplikasi (entry point) dan Pengontrol Aplikasi (AppController) yang menjembatani semua modul.
- gui.py: Mengatur seluruh komponen visual dan layout antarmuka menggunakan PyQt5.
- scraper.py: Mengelola permintaan HTTP (requests) dan logika parsing HTML (BeautifulSoup4).
- cleaner.py: Bertanggung jawab menormalkan teks, membersihkan whitespace, dan merapikan format tanggal.
- storage.py: Mengelola fungsi penyimpanan data (export) ke file system lokal.

⚠️ Catatan Penting
- Keberhasilan Scraping: Struktur HTML setiap situs web berita berbeda-beda. Scraper ini menggunakan selector CSS umum, sehingga mungkin tidak bisa mendeteksi elemen pada situs web dengan struktur yang sangat unik atau berbasis JavaScript penuh (SPA).
- Kecepatan Scraping: Aplikasi memberikan jeda singkat (delay time.sleep()) setiap kali berpindah halaman untuk menghindari pemblokiran IP oleh peladen (server) situs web berita.
