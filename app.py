import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Gunakan Streamlit Secrets untuk menyimpan API Key
# Ini adalah cara paling aman untuk menyimpan kredensial di Streamlit Cloud
API_KEY = st.secrets["gemini_api_key"]

# Nama model Gemini
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda
INITIAL_CHATBOT_CONTEXT = [
    {
        "role": "user",
        "parts": ["Kamu adalah seorang tenaga medis. Tuliskan penyakit yang perlu di diagnosis. Jawaban singkat dan jelas. Tolak pertanyaan selain tentang penyakit"]
    },
    {
        "role": "model",
        "parts": ["Baik! Tuliskan penyakit yang perlu di diagnosis."]
    }
]

# ==============================================================================
# FUNGSI UTAMA APLIKASI STREAMLIT
# ==============================================================================

# Judul Aplikasi
st.title("👨‍⚕️ Chatbot Diagnosis Medis")

# Konfigurasi API dengan API Key dari Streamlit Secrets
genai.configure(api_key=API_KEY)

# Inisialisasi model
try:
    model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )
except Exception as e:
    st.error(f"Kesalahan saat inisialisasi model: {e}")
    st.info("Pastikan nama model benar dan API Key valid.")
    st.stop()

# Inisialisasi riwayat chat di Streamlit session_state
if "messages" not in st.session_state:
    st.session_state.messages = INITIAL_CHATBOT_CONTEXT

# Tampilkan pesan dari riwayat chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["parts"][0])

# Tangani input dari pengguna
if prompt := st.chat_input("Tuliskan keluhan Anda..."):
    # Tambahkan pesan pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "parts": [prompt]})
    # Tampilkan pesan pengguna
    with st.chat_message("user"):
        st.markdown(prompt)

    # Dapatkan respons dari model
    with st.chat_message("model"):
        with st.spinner("Sedang Mendiagnosis..."):
            try:
                # Gunakan riwayat chat dari session_state
                chat = model.start_chat(history=st.session_state.messages)
                response = chat.send_message(prompt)
                
                # Tampilkan respons dari model
                st.markdown(response.text)
                
                # Tambahkan respons model ke riwayat
                st.session_state.messages.append({"role": "model", "parts": [response.text]})
                
            except Exception as e:
                st.error(f"Maaf, terjadi kesalahan saat memproses permintaan: {e}")
                st.info("Coba ulangi atau periksa koneksi internet.")
