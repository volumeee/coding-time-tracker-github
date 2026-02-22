# CodeStats API Pro Features TODO

- [x] **Step 1: Peningkatan Deteksi Framework & Tools**
  - [x] Tambahkan file pendeteksi baru seperti `next.config.js`, `tailwind.config.js`, `Dockerfile`, `docker-compose.yml`, `.github/workflows/`, `schema.prisma`.
  - [x] Update `config.py` dan `github_service.py` agar bisa mencari file-file tersebut.

- [ ] **Step 2: Mengabaikan Kode Eksternal & Auto-generated**
  - Buat mekanisme penyaringan di `get_languages` untuk mengurangi bobot bahasa jika repo tersebut dominan berisi file konfigurasi, _lock files_, statik build (seperti folder `dist`, `build`, `.next`).

- [ ] **Step 3: Memindai Forked Repositories Secara Akurat**
  - Ubah parameter pencarian repo untuk menyertakan `forks`.
  - Pastikan hanya _commit_ yang dilakukan oleh `username` yang kamu pasang yang dihitung waktunya (agar kode bawaan repo sumber tidak terhitung sebagai jam ngodingmu).

- [ ] **Step 4: Menghitung Pull Requests & Issues Baru**
  - Integrasikan endpoint `/search/issues?q=author:USERNAME+type:pr` dan `type:issue` di `github_service.py`.
  - Tambahkan output angka ini ke dalam _Stat Pills_ di desain SVG (misal: 🔀 **PRs: 15** • 🐞 **Issues: 4**).

- [ ] **Step 5: Deteksi Pola Jam Kerja (Night Owl vs Early Bird)**
  - Konversi semua _timestamp_ commit ke Local Timezone (berdasarkan mayoritas zona waktu atau default ke Waktu Lokal pengguna).
  - Tentukan apakah kamu **🦉 Night Owl** (jam 22:00 - 04:00), **☀️ Early Bird** (jam 05:00 - 10:00), atau **☕ Day Worker** (jam 11:00 - 18:00).
  - Tampilkan _badge_ gaya hidup ngoding ini secara visual di SVG!
