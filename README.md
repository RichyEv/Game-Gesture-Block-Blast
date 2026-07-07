
🎮 Gesture Block Blast - IoT & Computer Vision Project
Selamat datang di Gesture Block Blast, sebuah game berbasis Computer Vision dan Edge Processing yang dikendalikan sepenuhnya menggunakan gerakan tangan (hand gestures) secara real-time. Projek ini mengintegrasikan pemrosesan visual lokal menggunakan kamera (Webcam) dengan sistem notifikasi cloud melalui Telegram Bot API.
Projek ini dibuat untuk memenuhi tugas praktikum pada kelas TI 24P IoTN.

KELOMPOK 6
    • Anggota: Faradilla Rizki Fitri Nadia Shifa Adibah Richy Iza Janura
    • Kelas: TI 24P IoTN
    • Fokus Projek: Internet of Things (IoT), Computer Vision, & Network Integration

🚀 Fitur Utama
    1. Hand Tracking Control: Menggunakan Google MediaPipe (21 Landmark koordinat tangan) untuk mendeteksi posisi kursor dan gesture mengepal tangan (fist) untuk memegang/menjatuhkan blok.
    2. Dynamic Leveling System: Menggunakan arsitektur Configuration-Driven Design dengan tingkatan level berbasis skor (dari Pemula Cilik hingga Legenda Abadi).
    3. Telegram Bot Integration: Fitur pairing akun menggunakan token aktivasi acak dan pengiriman log hasil kuis/game over secara otomatis ke Telegram.
    4. Interactive Quiz System: Fitur mini-kuis interaktif di dalam game jika pemain salah meletakkan blok atau mendeteksi kondisi kritis tertentu.
    5. Memory-Optimized Buffer: Menggunakan NumPy Array untuk manajemen memori matriks papan game (board frame) dan manipulasi piksel secara cepat (60 FPS).
    6. Smart Automated Screenshot: Otomatis mengambil tangkapan layar menggunakan OpenCV ketika pemain memecahkan New Highscore atau mendapatkan nilai kuis sempurna (>95%).

🛠️ Persyaratan Sistem (Prerequisites)
Sebelum menjalankan program, pastikan perangkat Anda memenuhi spesifikasi berikut:
    • OS: Linux (Ubuntu/Debian/Arch dengan Fish/Bash shell) atau Windows 10/11.
    • Python Version: Python 3.11.x (Direkomendasikan menggunakan Virtual Environment).
    • Hardware: Webcam/Kamera bawaan yang berfungsi dengan baik.
    • Koneksi Internet: Dibutuhkan untuk sinkronisasi dengan Telegram Bot API.

📦 Langkah Instalasi & Persiapan Environment
Ikuti langkah-langkah di bawah ini untuk menyiapkan environment dan memasang semua library pendukung:

1. Masuk ke Folder Project & Buat Virtual Environment
Buka terminal Anda, lalu jalankan perintah berikut:
# Masuk ke direktori project
cd path/to/your/gesture-blockblast

# Membuat virtual environment baru bernama 'env_game'
python3 -m venv env_gam
e
2. Aktivasi Virtual Environment
    • Untuk Pengguna Terminal Fish (Linux):
      source env_game/bin/activate.fish
    • Untuk Pengguna Terminal Bash/Zsh (Linux):
      source env_game/bin/activate
      
3. Install Semua Dependency / Library
Setelah environment aktif (ditandai dengan munculnya nama (env_game) di awal baris terminal), install library yang dibutuhkan:
pip install opencv-python mediapipe pygame numpy requests

4. Konfigurasi Token Telegram (PENTING)
Demi alasan keamanan jaringan (Security Best Practice), token asli pada repository publik ini sengaja disembunyikan. Sebelum menjalankan game:
    1. Buka file GameGBB.py.
    2. Cari variabel TELE_TOKEN.
    3. Masukkan token bot Telegram Anda sendiri:

TELE_TOKEN = "MASUKKAN_TOKEN_BOT_TELEGRAM_ANDA_DISINI"

🎮 Cara Menjalankan & Memainkan Game
Setelah semua pustaka terinstall dan token telah dikonfigurasi, jalankan game menggunakan perintah:
python GameGBB.py

Panduan Bermain:

    1. Pairing Telegram: Saat game pertama kali dibuka, sistem akan menampilkan kode token aktivasi 4-digit di layar. Kirimkan kode tersebut ke Bot Telegram @BBgesture_Bot untuk menghubungkan akun permainan.
    
    2. Kontrol Navigasi: Arahkan telapak tangan Anda di depan kamera. Kursor di layar game akan bergerak mengikuti pergerakan tangan Anda secara halus (smoothed position).
    
    3. Mengambil & Meletakkan Blok: * Kepalkan tangan Anda di atas blok pilihan untuk mengambil/mengunci posisi blok (dragging).
        ◦ Buka kepalan tangan Anda (telapak tangan terbuka) untuk menjatuhkan blok tersebut ke dalam area papan 8x8.
        
    4. Sistem Kuis: Jika kuis muncul di layar, jawab pertanyaan dengan benar untuk menyelamatkan permainan dari kondisi Game Over.
    
    5. Penyimpanan Data: 
    • Skor tertinggi (Highscore) akan otomatis disimpan secara lokal di direktori ~ dalam bentuk file teks. 
    • Hasil dokumentasi screenshot (.jpg) akan disimpan di folder yang sama dengan file game.
