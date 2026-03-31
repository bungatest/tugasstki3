# 🔬 TF-IDF Full Pipeline
**Aplikasi Information Retrieval berbasis Streamlit**
Mata Kuliah: Information Retrieval — Teknik Informatika

---

## 📦 Struktur File
```
tfidf_app/
├── app.py           ← Aplikasi utama Streamlit
├── corpus.py        ← 10 dokumen artikel bahasa Indonesia
├── requirements.txt ← Daftar library Python
└── README.md        ← Panduan ini
```

---

## 🚀 Cara Menjalankan

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Jalankan aplikasi
```bash
streamlit run app.py
```

Aplikasi akan terbuka otomatis di browser: `http://localhost:8501`

---

## 🔄 Pipeline yang Diimplementasikan

| Step | Proses | Keterangan |
|------|--------|------------|
| 01 | **Dataset** | 10 artikel teknologi Indonesia |
| 02 | **Case Folding** | Ubah ke huruf kecil |
| 03 | **Tokenizing** | Pisahkan teks jadi token |
| 04 | **Stopword Removal** | Hapus kata umum (dan, atau, yang, ...) |
| 05 | **Stemming** | Bentuk kata dasar (Sastrawi) |
| 06 | **TF** | Term Frequency per dokumen |
| 07 | **DF** | Document Frequency |
| 08 | **IDF** | Inverse Document Frequency |
| 09 | **TF-IDF Matrix** | Matriks pembobotan lengkap |
| 10 | **Vocabulary Index** | Daftar term unik |
| 11 | **Query Engine** | Input & preprocessing query |
| 12 | **Similarity Ranking** | Cosine similarity + ranking + highlight |

---

## 📚 Library yang Digunakan
- `streamlit` — UI Framework
- `pandas` — Manipulasi data & tabel
- `numpy` — Komputasi numerik
- `PySastrawi` — Stemmer bahasa Indonesia (Nazief-Adriani)
- `matplotlib` & `seaborn` — Visualisasi grafik
- `scikit-learn` — Referensi TF-IDF (sklearn)

---

## 📋 Rumus yang Diimplementasikan
```
TF(t, d)      = kemunculan(t, d) / total_kata(d)
IDF(t)        = log₁₀( N / DF(t) )
TF-IDF(t, d)  = TF(t, d) × IDF(t)
cos(Q, D)     = (Q · D) / (|Q| × |D|)
```

---

## 💡 Contoh Query
- `teknologi kecerdasan buatan pendidikan`
- `keamanan siber data digital`
- `startup investasi fintech Indonesia`
- `lingkungan energi terbarukan`
- `cloud computing infrastruktur`
