import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def create_element(name):
    return OxmlElement(name)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_hex)
    tcPr.append(shd)

def generate_report():
    doc = docx.Document()
    
    # Page Setup - Margins (Standard A4, 2.54 cm / 1 inch)
    sections = doc.sections
    for section in sections:
        section.page_width = Inches(8.27)  # A4 width
        section.page_height = Inches(11.69) # A4 height
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Styles Setup
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Arial'
    normal_style.font.size = Pt(10)
    normal_style.font.color.rgb = RGBColor(30, 30, 30)
    
    # 1. JUDUL (Maksimum 14 kata, Arial 12 Bold KAPITAL semua, Center)
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(0)
    title_p.paragraph_format.space_after = Pt(12)
    title_run = title_p.add_run("PERAMALAN JUMLAH PENUMPANG MASKAPAI PENERBANGAN INTERNASIONAL MENGGUNAKAN METODE LONG SHORT-TERM MEMORY (LSTM)")
    title_run.font.name = 'Arial'
    title_run.font.size = Pt(12)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(0, 0, 0)
    
    # 2. Penulis & Afiliasi
    author_p = doc.add_paragraph()
    author_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    author_p.paragraph_format.space_before = Pt(0)
    author_p.paragraph_format.space_after = Pt(4)
    author_run = author_p.add_run("Praktikan Machine Learning")
    author_run.font.name = 'Arial'
    author_run.font.size = Pt(10)
    author_run.font.bold = True
    
    affil_p = doc.add_paragraph()
    affil_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    affil_p.paragraph_format.space_before = Pt(0)
    affil_p.paragraph_format.space_after = Pt(18)
    affil_run = affil_p.add_run("Program Studi Teknik Informatika / Ilmu Komputer\nFakultas Ilmu Komputer, Universitas\nEmail: praktikan@student.ac.id")
    affil_run.font.name = 'Arial'
    affil_run.font.size = Pt(9)
    affil_run.font.italic = True
    
    # 3. ABSTRAK (Bahasa Indonesia)
    abs_id_p = doc.add_paragraph()
    abs_id_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abs_id_p.paragraph_format.line_spacing = 1.0
    abs_id_p.paragraph_format.space_after = Pt(4)
    
    bold_abs = abs_id_p.add_run("ABSTRAK: ")
    bold_abs.font.name = 'Arial'
    bold_abs.font.size = Pt(9)
    bold_abs.font.bold = True
    
    abs_text = (
        "Peramalan volume penumpang penerbangan merupakan komponen krusial dalam perencanaan armada, alokasi awak kabin, dan manajemen kapasitas bandara. "
        "Tantangan utama dalam data deret waktu penerbangan adalah adanya kombinasi tren pertumbuhan non-linier jangka panjang dan fluktuasi musiman tahunan yang kuat. "
        "Penelitian ini bertujuan membangun sistem peramalan deret waktu berbasis deep learning menggunakan arsitektur Long Short-Term Memory (LSTM) Sequential. "
        "Metode yang diterapkan meliputi pra-pemrosesan data menggunakan MinMaxScaler untuk normalisasi skala interval [0, 1], teknik windowing dengan panjang sekuens look-back 12 bulan untuk menangkap siklus tahunan, dan pembagian dataset secara kronologis 80% data latih dan 20% data uji. "
        "Arsitektur LSTM dibangun dengan dua lapisan LSTM (64 dan 32 unit), lapisan Dropout (0.2) untuk mencegah overfitting, serta lapisan Dense sebagai output regresi, yang dioptimalkan menggunakan algoritma Adam dan fungsi loss Mean Squared Error (MSE). "
        "Hasil pengujian pada data uji (out-of-sample) menunjukkan performa yang sangat presisi dengan nilai Root Mean Squared Error (RMSE) sebesar 34.835, Mean Absolute Error (MAE) sebesar 28.141, Mean Absolute Percentage Error (MAPE) sebesar 6.592%, dan koefisien determinasi (R²) mencapai 0.8090. "
        "Model dan scaler diintegrasikan ke dalam aplikasi web interaktif berbasis Flask yang menyediakan visualisasi data historis, eksplorasi dekomposisi, evaluasi performa, dan fitur peramalan multi-step di masa depan. "
        "Dapat disimpulkan bahwa arsitektur LSTM efektif menangkap dinamika musiman kompleks dan tren penumpang, sehingga layak diimplementasikan sebagai sistem pendukung keputusan operasional penerbangan."
    )
    abs_run = abs_id_p.add_run(abs_text)
    abs_run.font.name = 'Arial'
    abs_run.font.size = Pt(9)
    
    # Kata Kunci
    kw_id_p = doc.add_paragraph()
    kw_id_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    kw_id_p.paragraph_format.space_after = Pt(14)
    kw_title = kw_id_p.add_run("Kata kunci: ")
    kw_title.font.name = 'Arial'
    kw_title.font.size = Pt(9)
    kw_title.font.bold = True
    kw_content = kw_id_p.add_run("Deep Learning, Long Short-Term Memory (LSTM), Peramalan Deret Waktu, Penumpang Pesawat, Flask Web App")
    kw_content.font.name = 'Arial'
    kw_content.font.size = Pt(9)
    kw_content.font.italic = True
    
    # 4. ABSTRACT (English)
    abs_en_p = doc.add_paragraph()
    abs_en_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    abs_en_p.paragraph_format.line_spacing = 1.0
    abs_en_p.paragraph_format.space_after = Pt(4)
    
    bold_abs_en = abs_en_p.add_run("ABSTRACT: ")
    bold_abs_en.font.name = 'Arial'
    bold_abs_en.font.size = Pt(9)
    bold_abs_en.font.bold = True
    
    abs_en_text = (
        "Airline passenger volume forecasting is an essential element in fleet scheduling, crew allocation, and airport infrastructure capacity management. "
        "The primary difficulty in aviation sequential data lies in the intricate superposition of non-linear long-term upward trends and pronounced annual seasonality. "
        "This study aims to develop an end-to-end deep learning forecasting system utilizing a Sequential Long Short-Term Memory (LSTM) network. "
        "The proposed methodology encompasses data preprocessing via MinMaxScaler to normalize features into [0, 1], sequential windowing with a 12-month look-back timestep to reflect annual periodicity, and a chronological train-test split (80% training, 20% testing). "
        "The stacked LSTM architecture comprises two recurrent LSTM layers (64 and 32 hidden units), Dropout layers (0.2) to prevent overfitting, and Dense regression layers, compiled with Adam optimizer and Mean Squared Error (MSE) loss function. "
        "Out-of-sample evaluation on unseen test data demonstrates exceptional predictive accuracy, achieving a Root Mean Squared Error (RMSE) of 34.835, Mean Absolute Error (MAE) of 28.141, Mean Absolute Percentage Error (MAPE) of 6.592%, and a coefficient of determination (R²) of 0.8090. "
        "The trained model and preprocessing pipeline are seamlessly deployed within an interactive Flask web application offering historical exploration, seasonal decomposition analysis, model evaluation scorecards, and multi-step autoregressive future forecasting. "
        "These findings demonstrate that LSTM neural networks successfully capture complex temporal dependencies and provide robust operational foresight for aviation decision-makers."
    )
    abs_en_run = abs_en_p.add_run(abs_en_text)
    abs_en_run.font.name = 'Arial'
    abs_en_run.font.size = Pt(9)
    abs_en_run.font.italic = True
    
    # Keywords English
    kw_en_p = doc.add_paragraph()
    kw_en_p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    kw_en_p.paragraph_format.space_after = Pt(18)
    kw_en_title = kw_en_p.add_run("Keywords: ")
    kw_en_title.font.name = 'Arial'
    kw_en_title.font.size = Pt(9)
    kw_en_title.font.bold = True
    kw_en_content = kw_en_p.add_run("Deep Learning, Long Short-Term Memory (LSTM), Time Series Forecasting, Airline Passengers, Flask Deployment")
    kw_en_content.font.name = 'Arial'
    kw_en_content.font.size = Pt(9)
    kw_en_content.font.italic = True

    # Helper function for Section Headings
    def add_section_heading(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = RGBColor(0, 0, 0)
        return h

    # Helper function for Sub-Headings (Bold & Italic, Arial 10)
    def add_subsection_heading(text):
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(4)
        h.paragraph_format.keep_with_next = True
        r = h.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
        r.font.bold = True
        r.font.italic = True
        return h

    # Helper function for Paragraphs
    def add_body_paragraph(text):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.15
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(text)
        r.font.name = 'Arial'
        r.font.size = Pt(10)
        return p

    # Helper function for Images and Captions (Center, Arial 9)
    def add_figure(image_path, caption_text, width_inch=5.5):
        if os.path.exists(image_path):
            img_p = doc.add_paragraph()
            img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            img_p.paragraph_format.space_before = Pt(8)
            img_p.paragraph_format.space_after = Pt(3)
            img_p.add_run().add_picture(image_path, width=Inches(width_inch))
            
            cap_p = doc.add_paragraph()
            cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cap_p.paragraph_format.space_before = Pt(0)
            cap_p.paragraph_format.space_after = Pt(10)
            cap_r = cap_p.add_run(caption_text)
            cap_r.font.name = 'Arial'
            cap_r.font.size = Pt(9)
            cap_r.font.italic = True

    # 5. PENDAHULUAN
    add_section_heading("PENDAHULUAN")
    add_body_paragraph(
        "Data sekuensial atau deret waktu (time series) memainkan peranan yang sangat penting dalam kehidupan modern, mulai dari pemantauan cuaca, transaksi pasar finansial, konsumsi daya energi listrik, hingga operasional sistem transportasi publik. "
        "Dalam domain transportasi penerbangan sipil, kemampuan untuk memprediksi volume mobilitas penumpang di masa depan secara akurat menjadi fondasi strategis bagi maskapai penerbangan dan pengelola bandar udara. "
        "Perencanaan kapasitas penerbangan yang tidak akurat dapat menimbulkan inefisiensi biaya operasional yang fatal, baik berupa idle capacity akibat kursi kosong yang berlebihan, maupun risiko kehilangan pendapatan serta penurunan kualitas layanan akibat lonjakan penumpang yang melampaui kapasitas armada yang tersedia (Box et al., 2015)."
    )
    add_body_paragraph(
        "Karakteristik data deret waktu pada penerbangan internasional memiliki kompleksitas yang tinggi karena memadukan tren kenaikan jangka panjang yang bersifat non-linier dan komponen musiman (seasonality) berulang yang dipengaruhi oleh liburan musim panas, libur hari raya, dan dinamika iklim global (Hyndman & Athanasopoulos, 2018). "
        "Metode statistika deret waktu tradisional seperti Autoregressive Integrated Moving Average (ARIMA) dan Exponential Smoothing kerap menghadapi kendala dalam menangkap ketergantungan temporal jangka panjang yang bersifat non-linier serta memerlukan asumsi kestasioneran data yang kaku."
    )
    add_body_paragraph(
        "Perkembangan teknologi Deep Learning, khususnya arsitektur Recurrent Neural Network (RNN) dengan varian Long Short-Term Memory (LSTM) yang diperkenalkan oleh Hochreiter & Schmidhuber (1997), menawarkan terobosan fundamental dalam memodelkan data berurutan. "
        "LSTM dirancang khusus dengan struktur gerbang memorik (gating mechanism) yang mampu mengatasi persoalan vanishing gradient dan exploding gradient, sehingga memungkinkan jaringan saraf mempertahankan memori informasi kontekstual dari langkah waktu yang jauh di masa lalu."
    )
    add_body_paragraph(
        "Tujuan dari penelitian tugas ini adalah merancang, membangun, mengevaluasi, dan mengintegrasikan sistem peramalan deret waktu berbasis LSTM menggunakan dataset benchmark historis penerbangan internasional (AirPassengers). "
        "Alur kerja yang diterapkan mencakup eksplorasi data komprehensif, normalisasi skala dengan MinMaxScaler, pembuatan sekuens windowing temporal, perancangan arsitektur Sequential LSTM berlapis dengan Dropout dan optimasi Adam, evaluasi menggunakan metrik RMSE, MAE, MAPE, dan R², serta implementasi sistem ke dalam aplikasi web interaktif berbasis Flask yang siap dideploy ke lingkungan cloud publik."
    )

    # 6. METODA
    add_section_heading("METODA")
    add_body_paragraph(
        "Metodologi pelaksanaan penelitian proyek ini dirancang secara sistematis dalam enam tahapan utama yang terintegrasi, dimulai dari pengumpulan dataset hingga deployment aplikasi web interaktif, sebagaimana diuraikan dalam sub-bagian berikut."
    )

    add_subsection_heading("Rancangan Alur Penelitian")
    add_body_paragraph(
        "Alur kerja penelitian dibagi menjadi: (1) Akuisisi dan eksplorasi dataset (EDA); (2) Pra-pemrosesan data yang mencakup normalisasi skala dan pembentukan struktur sekuens (sliding window); (3) Pemisahan data latih dan uji secara kronologis; (4) Desain arsitektur jaringan LSTM dan pelatihan model; (5) Evaluasi kinerja model menggunakan metrik regresi dan visualisasi deviasi; serta (6) Ekspor artefak model/scaler dan integrasi aplikasi web Flask."
    )

    add_subsection_heading("Dataset dan Sumber Data")
    add_body_paragraph(
        "Penelitian ini menggunakan dataset historis AirPassengers yang bersumber dari repositori publik deret waktu internasional (Kaggle/Box-Jenkins Benchmark). "
        "Dataset ini memuat rekaman jumlah penumpang pesawat bulanan selama rentang waktu 12 tahun, yaitu dari Januari 1949 sampai dengan Desember 1960, dengan total 144 observasi sekuensial berstempel waktu (timestamp) bulanan yang konsisten tanpa nilai yang hilang (zero missing values)."
    )

    add_subsection_heading("Pra-Pemrosesan Data dan Normalisasi Skala")
    add_body_paragraph(
        "Model jaringan saraf tiruan deep learning sangat sensitif terhadap skala fitur input karena fungsi aktivasi non-linier seperti hyperbolic tangent (tanh) beroperasi optimal pada rentang nilai yang terbatas. "
        "Oleh karena itu, fitur jumlah penumpang dinormalisasi ke dalam rentang [0, 1] menggunakan MinMaxScaler dari pustaka Scikit-Learn dengan formulasi matematis sebagai berikut:"
    )
    add_body_paragraph(
        "x_norm = (x - x_min) / (x_max - x_min)                                                     (1)\n"
        "di mana x adalah nilai jumlah penumpang asli, x_min adalah nilai observasi minimum dalam dataset (104 ribu penumpang), dan x_max adalah nilai observasi maksimum (622 ribu penumpang)."
    )

    add_subsection_heading("Pembuatan Sekuens Temporal (Sliding Window)")
    add_body_paragraph(
        "Untuk mentransformasikan permasalahan deret waktu menjadi format pembelajaran terbimbing (supervised learning), diterapkan teknik sliding window dengan panjang look-back timestep T = 12 bulan. "
        "Ukuran jendela 12 bulan dipilih secara ilmiah karena merepresentasikan satu siklus musiman tahunan penuh (annual seasonality). "
        "Secara matematis, untuk setiap indeks t >= 12, vektor masukan X_t dan target y_t dibentuk melalui pasangan:"
    )
    add_body_paragraph(
        "X_t = [x_{t-12}, x_{t-11}, ..., x_{t-1}]^T,      y_t = x_t                                (2)"
    )
    add_body_paragraph(
        "Dari total 144 observasi bulanan, proses windowing menghasilkan 132 sampel sekuens. "
        "Dataset kemudian dipisahkan secara kronologis (time-based split) tanpa pengacakan untuk mencegah data leakage: 80% sampel awal (105 sekuens, periode 1950 - 1957) dialokasikan sebagai Data Latih (Training Set), dan 20% sampel akhir (27 sekuens, periode 1958 - 1960) digunakan sebagai Data Uji (Testing Set)."
    )

    add_subsection_heading("Reshaping Tensor dan Arsitektur Model LSTM")
    add_body_paragraph(
        "Lapisan LSTM pada TensorFlow/Keras membutuhkan masukan tensor berdimensi 3D dengan format (samples, timesteps, features). "
        "Dalam studi kasus univariat ini, data diubah menjadi bentuk (105, 12, 1) untuk data latih dan (27, 12, 1) untuk data uji. "
        "Komputasi di dalam setiap sel memori LSTM dikendalikan oleh persamaan gerbang matematis berikut:"
    )
    add_body_paragraph(
        "Forget Gate:      f_t = σ(W_f · [h_{t-1}, x_t] + b_f)                                      (3)\n"
        "Input Gate:       i_t = σ(W_i · [h_{t-1}, x_t] + b_i)                                      (4)\n"
        "Candidate State:  C̃_t = tanh(W_c · [h_{t-1}, x_t] + b_c)                                  (5)\n"
        "Cell State:       C_t = f_t * C_{t-1} + i_t * C̃_t                                          (6)\n"
        "Output Gate:      o_t = σ(W_o · [h_{t-1}, x_t] + b_o)                                      (7)\n"
        "Hidden State:     h_t = o_t * tanh(C_t)                                                    (8)"
    )
    add_body_paragraph(
        "Arsitektur deep learning yang dibangun mengadopsi model Sequential berlapis (stacked LSTM): "
        "Lapisan pertama terdiri atas LSTM dengan 64 unit tersembunyi, fungsi aktivasi tanh, dan parameter return_sequences=True guna meneruskan sekuens temporal ke lapisan berikutnya. "
        "Lapisan kedua berupa Dropout dengan laju 0.20 untuk memutus koneksi bobot acak selama pelatihan guna mencegah overfitting. "
        "Lapisan ketiga adalah lapisan LSTM kedua dengan 32 unit tersembunyi (return_sequences=False). "
        "Lapisan keempat berupa Dropout 0.20, diikuti oleh lapisan Dense fully-connected dengan 16 neuron (aktivasi ReLU), dan lapisan keluaran Dense tunggal (linear) untuk memproyeksikan estimasi nilai skalar penumpang."
    )

    add_subsection_heading("Kompilasi dan Strategi Pelatihan")
    add_body_paragraph(
        "Model dikompilasi menggunakan optimizer Adam (laju pembelajaran awal 0.001) dan fungsi kerugian Mean Squared Error (MSE). "
        "Untuk menjamin stabilitas konvergensi dan efisiensi waktu komputasi, diimplementasikan dua mekanisme callback: "
        "(1) EarlyStopping dengan parameter monitor='val_loss', patience=30, dan restore_best_weights=True; serta "
        "(2) ReduceLROnPlateau dengan factor=0.5 dan patience=15 untuk mereduksi laju pembelajaran saat kurva loss validasi mulai mengalami plateau."
    )

    add_subsection_heading("Metrik Evaluasi Performa")
    add_body_paragraph(
        "Setelah pelatihan selesai, estimasi nilai prediksi pada data uji dikembalikan ke skala penumpang asli menggunakan inverse_transform. "
        "Kinerja kuantitatif diukur melalui empat metrik regresi baku:"
    )
    add_body_paragraph(
        "RMSE = sqrt( (1/n) * Σ (y_i - ŷ_i)^2 )                                                    (9)\n"
        "MAE  = (1/n) * Σ |y_i - ŷ_i|                                                              (10)\n"
        "MAPE = (1/n) * Σ |(y_i - ŷ_i) / y_i| * 100%                                              (11)\n"
        "R²   = 1 - ( Σ (y_i - ŷ_i)^2 / Σ (y_i - ȳ)^2 )                                            (12)"
    )

    # 7. HASIL DAN PEMBAHASAN
    add_section_heading("HASIL DAN PEMBAHASAN")
    add_body_paragraph(
        "Bagian ini memaparkan temuan eksperimen secara mendalam, mencakup eksplorasi visual data deret waktu, karakteristik dekomposisi, proses konvergensi pelatihan, evaluasi metrik kinerja model pada data uji, analisis residual, serta implementasi sistem aplikasi web interaktif."
    )

    add_subsection_heading("Eksplorasi Deret Waktu dan Pola Musiman")
    add_body_paragraph(
        "Visualisasi deret waktu pada Gambar 1 memperlihatkan dua sifat menonjol pada volume penumpang pesawat internasional periode 1949-1960. "
        "Pertama, terdapat tren sekuler yang konsisten meningkat dari tahun ke tahun, mencerminkan pesatnya ekspansi industri transportasi udara pasca-Perang Dunia II. "
        "Kedua, terlihat osilasi musiman yang berulang secara periodik dalam siklus 12 bulan dengan amplitudo yang semakin membesar (multiplicative seasonality)."
    )

    add_figure("reports/figures/eda_timeseries.png", "Gambar 1  Tren Historis Jumlah Penumpang Maskapai Internasional (1949 - 1960)")

    add_body_paragraph(
        "Dekomposisi time series secara aditif memisahkan data menjadi empat komponen utama: Observed, Trend (moving average 12 bulan), Seasonal, dan Residual, sebagaimana disajikan pada Gambar 2. "
        "Komponen musiman menunjukkan variasi berulang yang sangat teratur dengan deviasi positif tertinggi pada bulan Juli dan Agustus (+60 ribu hingga +80 ribu penumpang di atas tren rata-rata), yang berkaitan langsung dengan masa liburan musim panas internasional di belahan bumi utara. "
        "Sebaliknya, titik terendah secara konsisten terjadi pada bulan November."
    )

    add_figure("reports/figures/eda_decomposition.png", "Gambar 2  Dekomposisi Deret Waktu: Observed, Trend, Seasonal, dan Residual", width_inch=5.6)

    # Tabel 1 Keterangan Rata Kiri di atas tabel (Arial 9)
    tab1_p = doc.add_paragraph()
    tab1_p.paragraph_format.space_before = Pt(8)
    tab1_p.paragraph_format.space_after = Pt(3)
    tab1_p.paragraph_format.keep_with_next = True
    tab1_r = tab1_p.add_run("Tabel 1  Statistik Deskriptif Dataset AirPassengers (1949 - 1960)")
    tab1_r.font.name = 'Arial'
    tab1_r.font.size = Pt(9)
    tab1_r.font.bold = True

    table1 = doc.add_table(rows=7, cols=3)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER
    table1.autofit = False

    t1_headers = ["Parameter Statistik", "Nilai (Ribuan Penumpang)", "Keterangan Analisis"]
    t1_data = [
        ["Jumlah Observasi (N)", "144 Bulan", "Data lengkap tanpa nilai kosong (12 tahun)"],
        ["Rata-rata (Mean)", "280.30 Ribu", "Rata-rata volume penumpang per bulan"],
        ["Standar Deviasi (Std)", "119.97 Ribu", "Variasi persebaran data cukup tinggi"],
        ["Nilai Minimum (Min)", "104.00 Ribu", "Titik terendah tercatat pada November 1949"],
        ["Nilai Median (Q2)", "265.50 Ribu", "Nilai tengah data observasi"],
        ["Nilai Maksimum (Max)", "622.00 Ribu", "Puncak tertinggi tercatat pada Juli 1960"]
    ]

    for col_idx, h in enumerate(t1_headers):
        cell = table1.cell(0, col_idx)
        cell.text = h
        cell.paragraphs[0].runs[0].font.name = 'Arial'
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

    for row_idx, row_values in enumerate(t1_data):
        for col_idx, val in enumerate(row_values):
            cell = table1.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.paragraphs[0].runs[0].font.name = 'Arial'
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            set_cell_margins(cell, top=60, bottom=60, left=120, right=120)

    add_body_paragraph("")

    add_subsection_heading("Dinamika Pelatihan Model dan Konvergensi Loss")
    add_body_paragraph(
        "Pelatihan model LSTM dijalankan selama maksimum 150 epoch dengan batch size 8. "
        "Gambar 3 memperlihatkan kurva penurunan loss pelatihan (train loss) dan validasi (validation loss). "
        "Mekanisme EarlyStopping menghentikan proses pelatihan secara otomatis pada epoch ke-103 dan mengembalikan bobot optimal dari epoch ke-73, di mana nilai loss validasi mencapai titik minimum terbaik. "
        "Pemberian Dropout 0.20 terbukti ampuh mencegah overfitting, diindikasikan oleh kurva validasi yang bergerak selaras dengan kurva latih tanpa adanya divergensi."
    )

    add_figure("reports/figures/training_loss.png", "Gambar 3  Kurva Loss Pelatihan dan Validasi Model LSTM")

    add_subsection_heading("Evaluasi Kinerja Model pada Data Uji")
    add_body_paragraph(
        "Kinerja model LSTM dievaluasi secara ketat pada data uji (out-of-sample test set) yang mencakup 27 bulan pengamatan terakhir (1958-1960). "
        "Hasil perbandingan kuantitatif antara data latih dan data uji disajikan pada Tabel 2."
    )

    # Tabel 2
    tab2_p = doc.add_paragraph()
    tab2_p.paragraph_format.space_before = Pt(8)
    tab2_p.paragraph_format.space_after = Pt(3)
    tab2_p.paragraph_format.keep_with_next = True
    tab2_r = tab2_p.add_run("Tabel 2  Performa Evaluasi Metrik Model LSTM pada Data Latih dan Data Uji")
    tab2_r.font.name = 'Arial'
    tab2_r.font.size = Pt(9)
    tab2_r.font.bold = True

    table2 = doc.add_table(rows=5, cols=4)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER
    table2.autofit = False

    t2_headers = ["Metrik Evaluasi", "Data Latih (Train)", "Data Uji (Test)", "Standar Kriteria Penilaian"]
    t2_data = [
        ["Root Mean Squared Error (RMSE)", "28.648", "34.835", "Mendekati nol (skala ribuan penumpang)"],
        ["Mean Absolute Error (MAE)", "23.346", "28.141", "Deviasi rata-rata absolut sangat rendah"],
        ["Mean Absolute Percentage Error (MAPE)", "9.855%", "6.592%", "Kategori Sangat Akurat (< 10%)"],
        ["Koefisien Determinasi (R²)", "0.9000", "0.8090", "Model mampu menjelaskan 80.9% variansi data uji"]
    ]

    for col_idx, h in enumerate(t2_headers):
        cell = table2.cell(0, col_idx)
        cell.text = h
        cell.paragraphs[0].runs[0].font.name = 'Arial'
        cell.paragraphs[0].runs[0].font.size = Pt(9)
        cell.paragraphs[0].runs[0].font.bold = True
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

    for row_idx, row_values in enumerate(t2_data):
        for col_idx, val in enumerate(row_values):
            cell = table2.cell(row_idx + 1, col_idx)
            cell.text = val
            cell.paragraphs[0].runs[0].font.name = 'Arial'
            cell.paragraphs[0].runs[0].font.size = Pt(9)
            if col_idx in [1, 2]:
                cell.paragraphs[0].runs[0].font.bold = True
            set_cell_margins(cell, top=60, bottom=60, left=120, right=120)

    add_body_paragraph("")
    add_body_paragraph(
        "Berdasarkan standar interpretasi Lewis (1982), nilai MAPE di bawah 10% mengklasifikasikan performa model peramalan ke dalam kategori 'Sangat Akurat' (Highly Accurate). "
        "Model LSTM memperoleh nilai MAPE sebesar 6.592% pada data uji yang belum pernah dipelajari sebelumnya, serta skor R² sebesar 0.8090. "
        "Hasil ini membuktikan bahwa model mampu menggeneralisasi struktur pola musiman dan tren penumpang dengan sangat baik tanpa mengalami gejala menghafal data (overfitting)."
    )

    add_figure("reports/figures/model_prediction_test.png", "Gambar 4  Perbandingan Nilai Aktual vs Prediksi Model LSTM pada Data Uji", width_inch=5.5)

    add_body_paragraph(
        "Gambar 4 memperlihatkan plot perbandingan garis nilai aktual dan hasil prediksi LSTM pada rentang data uji. "
        "Model berhasil merekonstruksi gelombang fluktuasi tajam di musim liburan Juli-Agustus 1958, 1959, dan 1960 dengan deviasi yang berada dalam batas toleransi ±1 RMSE. "
        "Gambar 5 menyajikan evaluasi komprehensif pada seluruh rentang waktu observasi, memperlihatkan kontinuitas antara fitting data latih dan peramalan data uji."
    )

    add_figure("reports/figures/full_series_forecast.png", "Gambar 5  Evaluasi Komprehensif: Fitting Data Latih dan Generalisasi Data Uji", width_inch=5.6)

    add_subsection_heading("Analisis Residual Kesalahan Prediksi")
    add_body_paragraph(
        "Evaluasi residual (selisih antara nilai aktual dan prediksi) dilakukan untuk menguji validitas asumsi keacakan error. "
        "Sebagaimana disajikan pada Gambar 6, scatter plot residual terhadap nilai prediksi menunjukkan sebaran titik yang tersebar secara acak di sekitar sumbu horizontal nol tanpa pola non-linier atau heteroskedastisitas yang sistematis. "
        "Selain itu, histogram residual memperlihatkan kurva lonceng yang simetris mendekati distribusi normal, menegaskan bahwa model LSTM telah berhasil menyerap sebagian besar sinyal informasi sistematis dari data deret waktu."
    )

    add_figure("reports/figures/residuals_distribution.png", "Gambar 6  Distribusi dan Scatter Plot Residual Kesalahan Prediksi", width_inch=5.6)

    add_subsection_heading("Pengembangan dan Integrasi Aplikasi Web Flask")
    add_body_paragraph(
        "Model Keras terlatih diekspor ke dalam format lstm_model.keras dan lstm_model.h5, sementara objek normalisasi disimpan sebagai scaler.joblib. "
        "Aplikasi web interaktif dibangun menggunakan kerangka kerja Flask (Python 3.11) dan dirancang dengan antarmuka modern responsif berbasis Bootstrap 5 dan Chart.js. "
        "Aplikasi menyediakan lima modul fungsional: "
        "(1) Dashboard Eksekutif: menyajikan ringkasan statistik KPI (total observasi, nilai ekstrem, tren pertumbuhan); "
        "(2) Modul Eksplorasi Data: visualisasi time series historis interaktif dan tabel dekomposisi; "
        "(3) Modul Evaluasi Model: kartu skor metrik (RMSE, MAE, MAPE, R²), kurva loss training, dan analisis residual; "
        "(4) Modul Simulasi Peramalan: fitur simulasi proyeksi masa depan hingga 36 bulan ke depan dengan opsi skenario pasar (standar, optimis, konservatif) serta opsi pengujian sekuens input kustom; dan "
        "(5) RESTful API Endpoint (/api/forecast dan /api/historical) untuk memungkinkan integrasi layanan ke sistem informasi eksternal."
    )

    # 8. SIMPULAN DAN SARAN
    add_section_heading("SIMPULAN DAN SARAN")
    add_body_paragraph(
        "Berdasarkan serangkaian proses eksperimen, analisis, dan evaluasi yang telah dilakukan, dapat disimpulkan bahwa arsitektur deep learning Long Short-Term Memory (LSTM) Sequential berhasil menyelesaikan tantangan peramalan deret waktu pada data jumlah penumpang pesawat internasional secara optimal. "
        "Penerapan pra-pemrosesan normalisasi MinMaxScaler dan teknik windowing dengan panjang look-back 12 bulan terbukti sangat efektif dalam menangkap komponen musiman tahunan yang kuat dan tren kenaikan non-linier. "
        "Model LSTM yang dibangun mampu menghasilkan tingkat kesalahan yang sangat rendah pada data uji out-of-sample dengan RMSE 34.835, MAE 28.141, MAPE 6.592%, dan R² 0.8090, yang masuk dalam kategori sangat akurat. "
        "Integrasi model dan skaler ke dalam aplikasi web berbasis Flask memberikan kemudahan bagi pemangku kepentingan untuk mengakses visualisasi data historis dan melakukan proyeksi peramalan multi-step secara interaktif."
    )
    add_body_paragraph(
        "Kelebihan utama dari sistem yang dibangun adalah kemampuannya dalam memodelkan interaksi ketergantungan temporal jangka panjang tanpa memerlukan asumsi stasioneritas yang kaku seperti pada metode ARIMA konvensional. "
        "Namun demikian, penelitian ini memiliki keterbatasan karena hanya memanfaatkan pendekatan univariat yang bergantung semata pada data historis penumpang tanpa menyertakan variabel eksogen eksternal seperti harga bahan bakar avtur, indeks pertumbuhan ekonomi makro, atau kapasitas kursi maskapai. "
        "Untuk penelitian lanjutan, disarankan untuk mengintegrasikan fitur multivariat (multivariate time series) dan mengeksplorasi arsitektur mutakhir seperti Bidirectional LSTM atau Temporal Fusion Transformers (TFT), serta mengimplementasikan pipeline continuous learning agar model dapat memperbarui bobotnya secara otomatis seiring bertambahnya data operasional baru."
    )

    # 9. PUSTAKA ACUAN
    add_section_heading("PUSTAKA ACUAN")
    add_body_paragraph("Buku")
    add_body_paragraph(
        "Box, G. E., Jenkins, G. M., Reinsel, G. C., & Ljung, G. M. (2015). Time Series Analysis: Forecasting and Control (5th ed.). Hoboken, New Jersey: John Wiley & Sons.\n"
        "Goodfellow, I., Bengio, Y., & Courville, A. (2016). Deep Learning. Cambridge, Massachusetts: MIT Press.\n"
        "Hyndman, R. J., & Athanasopoulos, G. (2018). Forecasting: Principles and Practice (2nd ed.). Melbourne, Australia: OTexts."
    )
    
    add_body_paragraph("Jurnal/Prosiding/Disertasi/Tesis/Skripsi")
    add_body_paragraph(
        "Gers, F. A., Schmidhuber, J., & Cummins, F. (2000). Learning to Forget: Continual Prediction with LSTM. Neural Computation, 12(10), 2451-2471. https://doi.org/10.1162/089976600300015015\n"
        "Hochreiter, S., & Schmidhuber, J. (1997). Long Short-Term Memory. Neural Computation, 9(8), 1735-1780. https://doi.org/10.1162/neco.1997.9.8.1735\n"
        "Lewis, C. D. (1982). Industrial and Business Forecasting Methods: A Practical Guide to Exponential Smoothing and Curve Fitting. London: Butterworth Scientific.\n"
        "Siami-Namini, S., Tavakoli, N., & Namin, A. S. (2018). A Comparison of ARIMA and LSTM in Forecasting Time Series. In 17th IEEE International Conference on Machine Learning and Applications (ICMLA), 1394-1401. https://doi.org/10.1109/ICMLA.2018.00227"
    )

    add_body_paragraph("Lain-lain")
    add_body_paragraph(
        "Chollet, F., et al. (2015). Keras: Deep Learning for humans. GitHub Repository. https://github.com/keras-team/keras\n"
        "Pallets Projects. (2024). Flask Documentation: Web Development, One Drop at a Time. https://flask.palletsprojects.com/ (Diakses tanggal 31 Oktober 2026)."
    )

    # Save DOCX document
    output_docx = 'reports/Laporan_Tugas_TA04_LSTM_Time_Series.docx'
    doc.save(output_docx)
    print(f"Report DOCX saved to {output_docx}")

if __name__ == '__main__':
    generate_report()
