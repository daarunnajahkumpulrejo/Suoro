# 🇮🇩 Indonesian AI Voice Cloning

Aplikasi Gradio untuk **zero-shot voice cloning Bahasa Indonesia** menggunakan Indonesian Pocket TTS.

Model yang digunakan adalah `tryzz889/pocket-tts-indonesian`, model Indonesian berbasis Pocket TTS yang dilatih pada 502 jam speech Bahasa Indonesia.

## Fitur

- Upload audio referensi 10–20 detik
- Zero-shot voice cloning
- Bahasa Indonesia native
- Gradio Web UI
- Download hasil WAV langsung dari UI
- Tidak membutuhkan training speaker
- Bisa dijalankan di Google Colab
- Bisa dijalankan dari repository GitHub

## Struktur

```text
indonesian-voice-cloning/
├── app.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Jalankan di Google Colab

Buat notebook baru lalu jalankan:

```bash
!git clone https://github.com/USERNAME/REPO.git
%cd REPO
!pip install -r requirements.txt
!python app.py
```

Untuk Colab, jika ingin URL publik Gradio sementara, ubah bagian akhir `app.py`:

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=True,
)
```

Kemudian jalankan:

```bash
!python app.py
```

Colab akan menampilkan URL `gradio.live`.

## Jalankan lokal

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## Deploy

GitHub berfungsi sebagai repository source code. Untuk menjalankan aplikasi secara online, repository ini dapat dihubungkan ke platform hosting yang menjalankan Python/Gradio, misalnya Hugging Face Spaces atau server cloud.

Untuk Hugging Face Spaces, pilih:
- SDK: Gradio
- Python: sesuai runtime Space
- Hardware: CPU untuk model ringan ini, GPU opsional

Upload `app.py` dan `requirements.txt`, lalu Space akan menginstal dependency dan menjalankan aplikasi.

## Catatan model

Model Indonesian Pocket TTS yang dipakai menyediakan voice cloning dari audio prompt. Model 6-layer adalah varian yang direkomendasikan oleh model card.

Model card melaporkan:
- 438 MB untuk model 6-layer
- speaker similarity sekitar 0.939 pada evaluasi
- WER median 9.09%
- rekomendasi EOS threshold `-6.0`

Model card juga mencatat bahwa prompt suara yang bersih dan berkualitas tinggi sangat berpengaruh terhadap hasil cloning.

## Input teks

Model dilatih dengan transcript yang menulis angka sebagai kata. Karena itu gunakan:

```text
lima belas
dua puluh lima
seratus ribu
```

bukan:

```text
15
25
100000
```

## Lisensi

Periksa lisensi model `tryzz889/pocket-tts-indonesian` sebelum digunakan dalam produk komersial atau didistribusikan kembali.

Kode aplikasi dalam repository ini dapat Anda modifikasi sesuai kebutuhan.

## Etika penggunaan

Gunakan hanya suara yang Anda miliki atau yang Anda punya izin untuk kloning. Jangan gunakan untuk impersonasi, penipuan, atau membuat orang lain seolah-olah mengatakan sesuatu yang tidak pernah mereka katakan.
