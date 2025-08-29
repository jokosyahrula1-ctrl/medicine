# app.py
import streamlit as st
import google.generativeai as genai
import os

# ==============================================================================
# PENGATURAN API KEY DAN MODEL
# ==============================================================================

# Ambil API Key dari Streamlit Secrets
# Anda harus menambahkan API Key di Streamlit Cloud sebagai "GEMINI_API_KEY"
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("Peringatan: API Key belum diatur di Streamlit Secrets.")
    st.error("Harap tambahkan GEMINI_API_KEY ke Secrets Anda.")
    st.stop() # Hentikan eksekusi jika API Key tidak ditemukan

# Nama model Gemini yang akan digunakan.
MODEL_NAME = 'gemini-1.5-flash'

# ==============================================================================
# KONTEKS AWAL CHATBOT
# ==============================================================================

# Definisikan peran chatbot Anda di sini.
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
# FUNGSI UTAMA CHATBOT UNTUK STREAMLIT
# ==============================================================================

# Konfigurasi Gemini API
try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"Kesalahan saat mengkonfigurasi API Key: {e}")
    st.stop()

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
    st.error(f"Kesalahan saat inisialisasi model '{MODEL_NAME}': {e}")
    st.stop()

# --- Tampilan Antarmuka Streamlit ---
st.set_page_config(page_title="Chatbot Diagnosa Penyakit", page_icon="🩺")
st.title("👨‍⚕️ Chatbot Diagnosa Penyakit")
st.markdown("Masukkan nama penyakit yang ingin Anda ketahui lebih lanjut.")

# Inisialisasi riwayat chat di session_state jika belum ada
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Tambahkan pesan awal dari chatbot
    st.session_state.messages.append({"role": "assistant", "content": "Baik! Tuliskan penyakit yang perlu di diagnosis."})

# Tampilkan riwayat chat yang ada
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Inisialisasi sesi chat dengan riwayat awal
# Ini memastikan model 'mengingat' konteks awal di setiap interaksi
chat_history = [
    {"role": m["role"], "parts": [m["content"]]}
    for m in st.session_state.messages
    if m["role"] in ["user", "assistant"]
]
chat = model.start_chat(history=chat_history)

# Ambil input pengguna
if user_input := st.chat_input("Tuliskan penyakit di sini..."):
    # Tambahkan input pengguna ke riwayat
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Tampilkan input pengguna di UI
    with st.chat_message("user"):
        st.write(user_input)

    # Dapatkan respons dari model
    with st.chat_message("assistant"):
        with st.spinner("Sedang memproses..."):
            try:
                response = chat.send_message(user_input, request_options={"timeout": 60})
                
                if response and response.text:
                    st.write(response.text)
                    # Tambahkan respons model ke riwayat
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                else:
                    st.warning("Maaf, saya tidak bisa memberikan balasan.")
            except Exception as e:
                st.error(f"Terjadi kesalahan saat berkomunikasi dengan Gemini: {e}")
                st.warning("Silakan coba lagi.")
