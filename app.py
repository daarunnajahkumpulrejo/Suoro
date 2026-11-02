import os
import re
import tempfile
from pathlib import Path

import gradio as gr
import numpy as np
import scipy.io.wavfile
from pocket_tts import TTSModel

# ------------------------------------------------------------
# Konfigurasi model.
# Model ini adalah fine-tune Bahasa Indonesia berbasis Pocket TTS.
# Revision dipin agar aplikasi tidak tiba-tiba berubah jika model
# di-update oleh pemilik repository.
# ------------------------------------------------------------
MODEL_CONFIG = (
    "hf://tryzz889/pocket-tts-indonesian/"
    "indonesian_6l.yaml"
)

# EOS -6.0 adalah nilai yang dilaporkan paling baik pada evaluasi
# model Indonesian 6-layer.
EOS_THRESHOLD = -6.0

# Batas praktis teks untuk UI. Pocket TTS sendiri menangani teks
# panjang dengan pemotongan otomatis, tetapi batas UI mencegah
# request yang tidak sengaja terlalu besar.
MAX_TEXT_CHARS = 4000

# Model dimuat sekali saat aplikasi start agar tidak mengunduh
# dan membangun model setiap kali tombol Generate ditekan.
print("Loading Indonesian Pocket TTS model...")
model = TTSModel.load_model(
    config=MODEL_CONFIG,
    eos_threshold=EOS_THRESHOLD,
)
print("Model loaded successfully.")


def clean_text(text: str) -> str:
    """Normalisasi teks ringan tanpa mengubah bahasa pengguna."""
    # Menghapus spasi di awal/akhir.
    text = text.strip()

    # Mengubah rangkaian whitespace menjadi satu spasi.
    text = re.sub(r"\s+", " ", text)

    # Menghindari input kosong.
    if not text:
        raise ValueError("Teks tidak boleh kosong.")

    # Model Indonesian ini dilatih dengan angka yang ditulis sebagai
    # kata; angka digit dapat menjadi out-of-vocabulary.
    if re.search(r"\d", text):
        raise ValueError(
            "Tuliskan angka sebagai kata. Contoh: "
            "'15' → 'lima belas'."
        )

    # Membatasi panjang request dari UI.
    if len(text) > MAX_TEXT_CHARS:
        raise ValueError(
            f"Teks terlalu panjang. Maksimal {MAX_TEXT_CHARS} karakter."
        )

    return text


def validate_audio(audio_path: str) -> str:
    """Memastikan file referensi suara layak dipakai."""
    # Pastikan file benar-benar tersedia.
    if not audio_path or not Path(audio_path).exists():
        raise ValueError("Upload audio referensi terlebih dahulu.")

    # Membaca audio untuk mendapatkan sample rate dan panjangnya.
    sample_rate, audio = scipy.io.wavfile.read(audio_path)

    # Mengubah array stereo menjadi satu channel untuk pengukuran.
    if audio.ndim > 1:
        audio_mono = audio.mean(axis=1)
    else:
        audio_mono = audio

    # Menghitung durasi audio.
    duration = len(audio_mono) / float(sample_rate)

    # Voice prompt idealnya sekitar 10–20 detik.
    if duration < 3:
        raise ValueError(
            "Audio terlalu pendek. Gunakan rekaman minimal sekitar 3 detik."
        )

    # Pocket TTS hanya memproses sampai 30 detik untuk prompt panjang.
    if duration > 30:
        raise ValueError(
            "Audio terlalu panjang. Potong menjadi maksimal 30 detik; "
            "disarankan 10–20 detik."
        )

    return audio_path


def generate_voice(reference_audio: str, text: str):
    """Cloning suara zero-shot dan mengembalikan WAV untuk Gradio."""
    try:
        # Validasi input.
        reference_audio = validate_audio(reference_audio)
        text = clean_text(text)

        # Membuat speaker state dari audio referensi.
        # State ini menangkap karakter suara/acoustic conditioning.
        voice_state = model.get_state_for_audio_prompt(
            reference_audio
        )

        # Menghasilkan waveform Bahasa Indonesia.
        audio = model.generate_audio(
            voice_state,
            text,
            copy_state=True,
        )

        # Mengubah tensor menjadi NumPy float32.
        waveform = audio.detach().cpu().numpy()

        # Menghapus dimensi channel/batch yang tidak diperlukan.
        waveform = np.squeeze(waveform).astype(np.float32)

        # Menyimpan hasil ke file WAV sementara.
        output_path = tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ).name

        # Menulis audio pada sample rate model.
        scipy.io.wavfile.write(
            output_path,
            model.sample_rate,
            waveform,
        )

        return output_path

    except Exception as exc:
        # Gradio akan menampilkan pesan error ini kepada pengguna.
        raise gr.Error(str(exc)) from exc


# ------------------------------------------------------------
# Antarmuka Gradio.
# ------------------------------------------------------------
with gr.Blocks(
    title="Indonesian AI Voice Cloning",
    theme=gr.themes.Soft(),
) as demo:
    gr.Markdown(
        """
# 🎙️ Indonesian AI Voice Cloning

Zero-shot **voice cloning Bahasa Indonesia** dari audio referensi
pendek. Tidak perlu training speaker.

### Rekomendasi audio
- 10–20 detik
- satu pembicara
- minim musik/noise
- suara jelas
- WAV lebih disarankan

### Tips Bahasa Indonesia
- Tulis angka sebagai kata: `dua puluh lima`, bukan `25`.
- Gunakan tanda baca normal agar ritme kalimat lebih natural.
- Rekaman referensi yang bersih biasanya menghasilkan cloning suara
  yang lebih konsisten.
        """
    )

    with gr.Row():
        reference_audio = gr.Audio(
            label="🎤 Audio Referensi",
            type="filepath",
        )

        text = gr.Textbox(
            label="📝 Teks Bahasa Indonesia",
            placeholder=(
                "Contoh: Halo semuanya, hari ini kita akan membahas "
                "sesuatu yang menarik."
            ),
            lines=8,
        )

    generate_button = gr.Button(
        "🚀 Generate Voice",
        variant="primary",
    )

    output = gr.Audio(
        label="🔊 Hasil Voice Cloning",
        type="filepath",
    )

    generate_button.click(
        fn=generate_voice,
        inputs=[reference_audio, text],
        outputs=output,
    )

    gr.Markdown(
        """
---
**Catatan:** Gunakan hanya suara milik sendiri atau suara yang
Anda memiliki izin untuk kloning. Jangan gunakan aplikasi ini
untuk menyamar sebagai orang lain atau melakukan penipuan.
        """
    )


if __name__ == "__main__":
    # PORT dapat diberikan oleh Hugging Face Spaces, Render,
    # Docker, atau platform deployment lain.
    port = int(os.environ.get("PORT", "7860"))

    # 0.0.0.0 membuat server dapat diakses oleh platform hosting.
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
    )
