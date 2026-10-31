# 🎬 PANDUAN DAN NASKAH VIDEO PRESENTASI YOUTUBE (5 - 7 MENIT)
## Proyek: Peramalan Jumlah Penumpang Maskapai Internasional Menggunakan Long Short-Term Memory (LSTM)

---

### **Ringkasan Teknis Video**
* **Durasi Total**: 06 Menit 30 Detik (Rentang target: 5 - 7 Menit)
* **Format Rekaman**: OBS Studio / Loom / Camtasia (Screen Recording 1080p 60fps + Facecam di pojok kanan bawah)
* **Target Audiens**: Dosen Pengampu, Asisten Praktikum Machine Learning, dan Komunitas Data Science
* **Platform Unggah**: YouTube (Unlisted atau Public)

---

## ⏱️ RUNDOWN & TIMELINE PRESENTASI

| Waktu | Segmen | Fokus Visual / Layar | Durasi |
| :--- | :--- | :--- | :--- |
| **00:00 - 00:45** | **1. Pembukaan & Latar Belakang** | Facecam + Slide Judul & Identitas | 45 detik |
| **00:45 - 01:45** | **2. Eksplorasi Data & Pola Musiman** | Jupyter Notebook (Grafik Time Series & Dekomposisi) | 60 detik |
| **01:45 - 03:00** | **3. Pra-Pemrosesan & Arsitektur LSTM** | Diagram Windowing + Kode Keras Arsitektur | 75 detik |
| **03:00 - 04:15** | **4. Hasil Pelatihan & Evaluasi Metrik** | Grafik Aktual vs Prediksi & Tabel Metrik (RMSE/MAPE) | 75 detik |
| **04:15 - 05:45** | **5. Demonstrasi Live Web App Flask** | Browser Layar Penuh (Dashboard & Simulasi Peramalan) | 90 detik |
| **05:45 - 06:30** | **6. Temuan Unik, Kesimpulan & Penutup** | Facecam + Slide Kesimpulan & Link GitHub | 45 detik |

---

## 🎙️ NASKAH LENGKAP KATA DEMI KATA (VERBATIM SCRIPT)

---

### **SEGMEN 1: PEMBUKAAN & LATAR BELAKANG (00:00 - 00:45)**
> **[VISUAL]**: *Kamera menampilkan wajah pembicara (Facecam) dengan latar belakang Slide Presentasi Judul: "AeroCast LSTM: Time Series Forecasting for Airline Passenger Demand".*

**Naskah:**
> *"Halo semuanya! Selamat pagi/siang kepada Bapak/Ibu dosen pengampu dan rekan-rekan sekalian. Perkenalkan, saya [Nama Mahasiswa], mahasiswa [Program Studi/Universitas].*  
> 
> *Pada kesempatan kali ini, saya akan mempresentasikan hasil pengerjaan Tugas TA-04 Machine Learning mengenai pemodelan data sekuensial dan peramalan deret waktu (time series forecasting).*  
> 
> *Studi kasus yang saya pilih berada di domain **transportasi udara**, yaitu **Peramalan Jumlah Penumpang Maskapai Penerbangan Internasional**. Mengapa domain ini krusial? Karena industri penerbangan beroperasi dengan biaya operasional yang sangat tinggi. Kesalahan dalam memprediksi permintaan penumpang dapat mengakibatkan inefisiensi alokasi armada dan awak kabin, atau bahkan kehilangan potensi pendapatan saat terjadi lonjakan musiman.*  
> 
> *Untuk menjawab tantangan ini, saya membangun sistem peramalan end-to-end berbasis Deep Learning menggunakan jaringan **Long Short-Term Memory (LSTM)** dan mendeploy-nya ke dalam aplikasi web interaktif berbasis Flask."*

---

### **SEGMEN 2: EKSPLORASI DATA & ANALISIS MUSIMAN (00:45 - 01:45)**
> **[VISUAL]**: *Beralih ke layar Jupyter Notebook / Visual Studio Code. Sorot grafik `eda_timeseries.png` dan `eda_decomposition.png`.*

**Naskah:**
> *"Mari kita masuk ke tahap eksplorasi data. Dataset yang digunakan adalah data historis bulanan penumpang maskapai dari tahun 1949 hingga 1960, dengan total 144 observasi tanpa nilai kosong.*  
> 
> *Ketika kita plot datanya ke dalam grafik waktu, kita dapat mengidentifikasi dua pola utama:*  
> 1. *Pertama, **Tren Sekuler Kenaikan Non-Linier**, di mana jumlah penumpang terus meningkat secara eksponensial seiring bertambahnya tahun.*  
> 2. *Kedua, **Pola Musiman Tahunan (Annual Seasonality)** yang sangat kuat. Melalui dekomposisi deret waktu, kita menemukan bahwa puncak lonjakan penumpang secara konsisten terjadi pada bulan **Juli dan Agustus**, bertepatan dengan musim liburan musim panas internasional, dengan peningkatan hingga 80 ribu penumpang di atas rata-rata tren.*  
> 
> *Pola musiman multiplicative dengan variasi amplitudo yang membesar inilah yang membuat model statistik klasik sulit beradaptasi, dan menjadi alasan utama mengapa arsitektur Recurrent Neural Network seperti LSTM sangat ideal diterapkan."*

---

### **SEGMEN 3: PRA-PEMROSESAN & ARSITEKTUR LSTM (01:45 - 03:00)**
> **[VISUAL]**: *Tampilkan sel kode normalisasi `MinMaxScaler`, fungsi `create_sequences`, dan diagram arsitektur model di Notebook.*

**Naskah:**
> *"Selanjutnya adalah alur pra-pemrosesan data deep learning:*  
> 1. *Pertama, **Normalisasi Skala**: Fitur target diskalakan ke rentang 0 sampai 1 menggunakan `MinMaxScaler` dari Scikit-Learn agar proses backpropagation stabil dan fungsi aktivasi hyperbolic tangent (tanh) bekerja optimal.*  
> 2. *Kedua, **Windowing Temporal**: Kita mentransformasikan deret univariat menjadi supervised learning dengan panjang jendela *look-back* sebesar **12 bulan**. Artinya, model menggunakan data 12 bulan terakhir untuk memprediksi nilai penumpang pada bulan ke-13.*  
> 3. *Ketiga, **Pemisahan Data Kronologis**: Kami membagi data secara time-based: 80% pertama (105 sekuens) sebagai Data Latih, dan 20% terakhir (27 sekuens) sebagai Data Uji out-of-sample.*  
> 4. *Keempat, **Reshaping Tensor**: Data di-reshape ke bentuk tensor 3D: `(samples, 12, 1)`.*  
> 
> *Arsitektur model yang kami bangun bertipe **Sequential**, terdiri dari:*  
> * Lapisan LSTM pertama: **64 unit** dengan `return_sequences=True`.*  
> * Lapisan **Dropout 0.20** untuk mencegah overfitting.*  
> * Lapisan LSTM kedua: **32 unit**.*  
> * Lapisan **Dropout 0.20** kembali.*  
> * Lapisan **Dense 16 neuron** dengan aktivasi ReLU, dan lapisan output linier 1 neuron.*  
> 
> *Model dikompilasi dengan optimizer **Adam** dan fungsi loss **Mean Squared Error (MSE)**, serta dilengkapi callback **EarlyStopping** dan **ReduceLROnPlateau**."*

---

### **SEGMEN 4: HASIL PELATIHAN & EVALUASI KINERJA (03:00 - 04:15)**
> **[VISUAL]**: *Tampilkan kurva loss pelatihan (`training_loss.png`) dan plot garis pengujian aktual vs prediksi (`model_prediction_test.png`). Tunjukkan tabel metrik evaluasi.*

**Naskah:**
> *"Sekarang mari kita tinjau performa pelatihan dan evaluasi model:*  
> * Pada kurva loss, pelatihan konvergen secara mulus dan mekanisme EarlyStopping berhenti pada epoch ke-103 dengan memulihkan bobot terbaik dari epoch ke-73.*  
> * Setelah memprediksi data uji, nilai prediksi dikembalikan ke skala aslinya menggunakan `inverse_transform`.*  
> 
> *Hasil evaluasi kuantitatif pada data uji menunjukkan:*  
> * **RMSE (Root Mean Squared Error)** sebesar **34.835**.*  
> * **MAE (Mean Absolute Error)** sebesar **28.141**.*  
> * **MAPE (Mean Absolute Percentage Error)** mencapai **6.592%**! Berdasarkan literatur forecasting, nilai MAPE di bawah 10% tergolong dalam kategori **Sangat Akurat** (Highly Accurate).*  
> * Dan skor **$R^2$ (Koefisien Determinasi)** sebesar **0.8090**, yang berarti model berhasil menjelaskan hampir 81% variabilitas pada data uji yang belum pernah dilihat sebelumnya.*  
> 
> *Seperti yang terlihat pada plot perbandingan garis merah (prediksi LSTM) dan garis hitam (aktual), model mampu meniru lonjakan tajam musim panas dan penurunan di akhir tahun dengan sangat presisi."*

---

### **SEGMEN 5: DEMONSTRASI LIVE APLIKASI WEB FLASK (04:15 - 05:45)**
> **[VISUAL]**: *Buka web browser layar penuh menampilkan aplikasi web AeroCast LSTM (localhost:5000 / URL Cloud).*

**Naskah:**
> *"Untuk menghadirkan model ini ke pengguna akhir, saya mengembangkan aplikasi web interaktif menggunakan kerangka kerja **Flask**, **Bootstrap 5**, dan **Chart.js**.*  
> 
> *Mari kita lakukan tur aplikasi:*  
> 1. *Halaman pertama adalah **Dashboard**. Di sini pengguna disajikan ringkasan KPI eksekutif, seperti total observasi (144 bulan), volume penumpang terakhir, rekor tertinggi historis, serta grafik interaktif pertumbuhan data.*  
> 2. *Halaman kedua adalah **Eksplorasi Data**, yang menyajikan ringkasan statistik deskriptif dan visualisasi dekomposisi deret waktu.*  
> 3. *Halaman ketiga adalah **Evaluasi Model**, menampilkan scorecard metrik akurasi, perbandingan data uji, kurva konvergensi, dan analisis residual.*  
> 4. *Dan ini adalah fitur unggulan utama kami: **Simulasi Peramalan Interaktif**.*  
>    * Di sini, pengguna dapat memilih horizon peramalan: misalnya 6 bulan, 12 bulan, atau 24 bulan ke depan.*  
>    * Pengguna juga dapat memilih skenario pasar, seperti Standar, Optimis, atau Konservatif, bahkan memasukkan 12 angka kustom sendiri.*  
>    * Ketika kita klik tombol 'Jalankan Simulasi Peramalan', model LSTM di backend Flask akan mengeksekusi algoritma *autoregressive recursive forecast*.*  
>    * Hasilnya ditampilkan seketika dalam grafik Chart.js yang dinamis dengan pita batas toleransi kesalahan (confidence intervals), serta tabel rincian bulanan yang siap diunduh.*  
> 5. *Selain antarmuka web, kami juga menyediakan endpoint REST API pada rute `/api/forecast` sehingga model ini dapat diintegrasikan ke sistem enterprise lainnya."*

---

### **SEGMEN 6: TEMUAN UNIK, KESIMPULAN & PENUTUP (05:45 - 06:30)**
> **[VISUAL]**: *Facecam pembicara + Slide Kesimpulan yang memuat tautan Repositori GitHub & Dokumen Laporan.*

**Naskah:**
> *"Sebagai penutup, ada beberapa temuan unik dari proyek ini:*  
> * Pertama, pemilihan window size **12 bulan** terbukti sangat krusial; jika menggunakan jendela lebih pendek (misalnya 6 bulan), model kehilangan referensi musiman tahunan dan performa turun signifikan.*  
> * Kedua, penerapan Dropout 0.20 dan normalisasi skala fit-transform terbukti menjaga generalisasi model sehingga tidak terjadi overfitting meskipun ukuran dataset relatif kecil.*  
> 
> *Seluruh artefak proyek — mulai dari notebook eksperimen, kode sumber aplikasi Flask, file model `.keras` dan `.h5`, file scaler, laporan lengkap berformat DOCX dan PDF sesuai template, serta petunjuk deployment — telah tersedia secara rapi di repositori GitHub kami.*  
> 
> *Terima kasih banyak atas perhatian Bapak/Ibu dosen dan rekan-rekan sekalian. Semoga presentasi ini bermanfaat. Sampai jumpa!"*

---

## 💡 TIPS PENGAMBILAN REKAMAN (RECORDING CHECKLIST)
1. **Pencahayaan & Audio**: Gunakan mikrofon eksternal (clip-on / headset) agar suara jernih dan bebas gaung.
2. **Kualitas Layar**: Set resolusi monitor ke 1920x1080 (1080p).
3. **Persiapan Browser**: Buka tab web aplikasi Flask (`http://localhost:5000`) dan siapkan grafik evaluasi sebelum mulai merekam.
4. **Deskripsi YouTube**: Sertakan tautan GitHub, tautan web app live (Render/Railway), dan ringkasan metrik di kolom deskripsi video.

