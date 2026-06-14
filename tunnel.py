from pyngrok import ngrok
import subprocess

# Jalankan streamlit di background
subprocess.Popen(["streamlit", "run", "app.py", "--server.port=8501"])

# Buat tunnel publik
url = ngrok.connect(8501)
print(f"\n🌐 Link Publik: {url}")
print("Bagikan link ini saat presentasi!")
print("Tekan Ctrl+C untuk stop")

input()  # Jaga program tetap jalan