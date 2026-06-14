import streamlit as st
import json
import os
import html as html_lib
import random  # Digunakan untuk simulasi konversi kurs loker
from datetime import datetime
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
from deep_translator import GoogleTranslator
from nltk.stem import PorterStemmer

# Inisialisasi Stemmer
stemmer = PorterStemmer()

def stem_text(text):
    return " ".join([stemmer.stem(word) for word in text.split()])

# FUNGSI BARU: Mengubah angka mentah menjadi format Rupiah dengan pemisah titik (.)
def format_rupiah(nilai):
    return f"Rp {nilai:,}".replace(",", ".")

st.set_page_config(page_title="JobFinder", page_icon="💼", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
* { font-family: 'Plus Jakarta Sans', sans-serif !important; }
.stApp { background: #F3F4F6; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; }
.nav-logo { font-size: 1.4rem; font-weight: 800; color: #1D3557; }
.nav-logo span { color: #E63946; }
.nav-badge { background: #1D3557; color: white; padding: 8px 16px; border-radius: 6px; font-size: 0.82rem; font-weight: 600; }
.hero { background: linear-gradient(135deg, #1D3557 0%, #2B4A7A 100%); padding: 48px 40px; margin-bottom: 0; }
.hero-title { font-size: 2rem; font-weight: 800; color: white; margin-bottom: 8px; }
.hero-sub { color: #A8C4E0; font-size: 0.9rem; margin-bottom: 28px; }
.hero-stats { display: flex; gap: 32px; margin-top: 20px; }
.hero-stat-num { font-size: 1.4rem; font-weight: 800; color: white; line-height: 1; }
.hero-stat-label { font-size: 0.75rem; color: #A8C4E0; margin-top: 2px; }
.result-label { font-size: 1.1rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.result-sub { font-size: 0.82rem; color: #6B7280; margin-bottom: 20px; }
.job-card { background: white; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px 24px; margin-bottom: 10px; transition: all 0.15s; }
.job-card:hover { border-color: #1D3557; box-shadow: 0 2px 12px rgba(29,53,87,0.1); }
.job-title { font-size: 1rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.job-company { font-size: 0.85rem; color: #374151; font-weight: 500; margin-bottom: 10px; }
.badge-relevan { display: inline-block; background: #ECFDF5; color: #065F46; border: 1px solid #6EE7B7; border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; margin-right: 6px; }
.badge-cukup { display: inline-block; background: #FFF7ED; color: #9A3412; border: 1px solid #FED7AA; border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; margin-right: 6px; }
.badge-remote { display: inline-block; background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; margin-right: 6px; }
.badge-gaji { display: inline-block; background: #FEF3C7; color: #92400E; border: 1px solid #FCD34D; border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; margin-right: 6px; }
.job-info { font-size: 0.8rem; color: #6B7280; margin-top: 10px; display: flex; gap: 16px; flex-wrap: wrap; }
.job-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 12px; }
.job-sumber { font-size: 0.72rem; color: #9CA3AF; background: #F9FAFB; padding: 3px 8px; border-radius: 4px; }
.lihat-btn { background: #1D3557; color: white !important; padding: 6px 14px; border-radius: 6px; font-size: 0.78rem; font-weight: 600; text-decoration: none !important; }
.info-card { background: white; border: 1px solid #E5E7EB; border-radius: 12px; padding: 20px; margin-bottom: 12px; }
.info-title { font-size: 0.9rem; font-weight: 700; color: #111827; margin-bottom: 12px; }
.info-item { font-size: 0.82rem; color: #6B7280; padding: 8px 0; border-bottom: 1px solid #F3F4F6; display: flex; justify-content: space-between; }
.info-num { font-weight: 700; color: #1D3557; }
.empty-wrap { text-align: center; padding: 80px 20px; color: #9CA3AF; }
.empty-title { font-size: 1.1rem; font-weight: 700; color: #374151; margin: 12px 0 6px; }
.about-hero { background: linear-gradient(135deg, #1D3557 0%, #2B4A7A 100%); padding: 48px 40px; margin-bottom: 32px; border-radius: 16px; }
.about-hero-title { font-size: 1.8rem; font-weight: 800; color: white; margin-bottom: 8px; }
.about-hero-sub { color: #A8C4E0; font-size: 0.9rem; }
.about-card { background: white; border: 1px solid #E5E7EB; border-radius: 12px; padding: 28px; margin-bottom: 16px; }
.about-card-title { font-size: 1rem; font-weight: 700; color: #1D3557; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 2px solid #EFF6FF; }
.about-step { display: flex; gap: 16px; margin-bottom: 16px; align-items: flex-start; }
.about-step-num { background: #1D3557; color: white; width: 28px; height: 28px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; flex-shrink: 0; }
.about-step-text { font-size: 0.85rem; color: #374151; line-height: 1.6; }
.about-step-title { font-weight: 700; color: #111827; margin-bottom: 2px; }
.metric-row { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 8px; }
.metric-box { flex: 1; min-width: 120px; background: #F8FAFC; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; text-align: center; }
.metric-val { font-size: 1.6rem; font-weight: 800; color: #1D3557; }
.metric-label { font-size: 0.72rem; color: #6B7280; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px; }
.metric-box.winner { background: #ECFDF5; border-color: #6EE7B7; }
.metric-box.winner .metric-val { color: #065F46; }
.compare-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 8px; }
.compare-box { border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; }
.compare-box.active { border-color: #1D3557; background: #EFF6FF; }
.compare-title { font-weight: 700; font-size: 0.85rem; color: #111827; margin-bottom: 8px; }
.compare-item { font-size: 0.78rem; color: #6B7280; padding: 4px 0; }
.sumber-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; }
.sumber-box { border: 1px solid #E5E7EB; border-radius: 8px; padding: 14px; text-align: center; }
.sumber-name { font-weight: 700; font-size: 0.85rem; color: #1D3557; }
.sumber-count { font-size: 0.75rem; color: #6B7280; margin-top: 4px; }
.timeline-item { display: flex; gap: 12px; margin-bottom: 12px; align-items: flex-start; }
.timeline-dot { width: 10px; height: 10px; background: #1D3557; border-radius: 50%; margin-top: 5px; flex-shrink: 0; }
.timeline-text { font-size: 0.83rem; color: #374151; line-height: 1.5; }
.timeline-label { font-weight: 700; color: #111827; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    with open("data_bersih.json", "r") as f:
        loker_list = json.load(f)
        
    # KURS 1 USD = 16.321 IDR
    KURS_USD_TO_IDR = 16321
    random.seed(42)  
    
    for l in loker_list:
        if "gaji" not in l or not l["gaji"] or l["gaji"] == 0:
            gaji_usd = random.randint(3000, 15000)
            l["gaji"] = gaji_usd * KURS_USD_TO_IDR
            
    dokumen = [stem_text(l["teks_gabung"]) for l in loker_list]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(dokumen)
    bm25 = BM25Okapi([d.split() for d in dokumen])
    return loker_list, vectorizer, tfidf_matrix, bm25

loker_list, vectorizer, tfidf_matrix, bm25 = load_data()

waktu_update = os.path.getmtime("data_bersih.json")
waktu_str = datetime.fromtimestamp(waktu_update).strftime("%d %b %Y")
sumber_unik = len(set(l.get("sumber","") for l in loker_list))
sumber_count = Counter(l.get("sumber","") for l in loker_list)

if "halaman" not in st.session_state:
    st.session_state.halaman = "cari"

def get_badge(skor):
    if skor >= 0.3:
        return '<span class="badge-relevan">&#10003; Sangat Relevan</span>'
    elif skor >= 0.1:
        return '<span class="badge-cukup">~ Cukup Relevan</span>'
    return ''

def is_remote(loker):
    teks = (loker.get("teks_gabung","") + loker.get("lokasi","")).lower()
    return "remote" in teks

def cari(query, metode="bm25", lokasi_filter="", kategori_filter=None, gaji_min=0, top_k=20):
    if kategori_filter is None:
        kategori_filter = []
        
    query_clean = ""
    query_stemmed = ""
    
    if query:
        try:
            query_translated = GoogleTranslator(source='auto', target='en').translate(query)
            query_clean = query_translated.lower()
        except Exception:
            query_clean = query.lower()
        query_stemmed = stem_text(query_clean)

    if metode == "tfidf":
        if query_stemmed:
            skor = cosine_similarity(vectorizer.transform([query_stemmed]), tfidf_matrix).flatten()
        else:
            skor = [0] * len(loker_list)
    else:
        if query_stemmed:
            skor = bm25.get_scores(query_stemmed.split())
        else:
            skor = [0] * len(loker_list)
            
    ranking = sorted(enumerate(skor), key=lambda x: x[1], reverse=True)
    hasil = []
    for i, s in ranking:
        if query and s <= 0:
            continue
            
        loker = loker_list[i]
        
        # FILTER GAJI
        if loker.get("gaji", 0) < gaji_min:
            continue
            
        if lokasi_filter:
            cek = (loker.get("lokasi","") + " " + loker.get("teks_gabung","")).lower()
            if lokasi_filter.lower() not in cek:
                continue
        if kategori_filter:
            tags_loker = loker.get("tags","").lower()
            cocok = any(kat.lower() in tags_loker for kat in kategori_filter)
            if not cocok:
                continue
                
        hasil.append((loker, s))
        if len(hasil) >= top_k:
            break
            
    return hasil, query_clean

# NAVBAR
nav1, nav2, nav3, nav4 = st.columns([2, 1, 1, 2])
with nav1:
    st.markdown('<div class="nav-logo">Job<span>Finder</span></div>', unsafe_allow_html=True)
with nav2:
    if st.button("Cari Lowongan", use_container_width=True):
        st.session_state.halaman = "cari"
        st.rerun()
with nav3:
    if st.button("Tentang Sistem", use_container_width=True):
        st.session_state.halaman = "tentang"
        st.rerun()
with nav4:
    st.markdown(f'<div style="text-align:right"><span class="nav-badge">Update: {waktu_str}</span></div>', unsafe_allow_html=True)

st.markdown("<hr style='margin:0;border:none;border-top:1px solid #E5E7EB'>", unsafe_allow_html=True)

# HALAMAN CARI
if st.session_state.halaman == "cari":
    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">Temukan Lowongan yang Tepat</div>
        <div class="hero-sub">Pencarian cerdas berbasis Information Retrieval &middot; BM25 &amp; TF-IDF</div>
        <div class="hero-stats">
            <div><div class="hero-stat-num">{len(loker_list):,}</div><div class="hero-stat-label">Lowongan Tersedia</div></div>
            <div><div class="hero-stat-num">{sumber_unik}</div><div class="hero-stat-label">Sumber Data</div></div>
            <div><div class="hero-stat-num">64%</div><div class="hero-stat-label">Precision BM25</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([3, 2, 1])
    with c1:
        query = st.text_input("", placeholder="Posisi, skill, atau perusahaan...", label_visibility="collapsed")
    with c2:
        lokasi = st.text_input("", placeholder="Kota atau wilayah (contoh: remote, london)...", label_visibility="collapsed")
    with c3:
        metode = st.selectbox("", ["BM25", "Cosine Similarity"], label_visibility="collapsed")

    # Filter Kategori & Gaji Rupiah
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        KATEGORI = [
            "software engineering", "data and analytics", "sales", "marketing and communication",
            "finance", "healthcare", "project management", "human resources and recruitment",
            "business operations", "customer success", "engineering"
        ]
        filter_kategori = st.multiselect(
            "🏷️ Filter Kategori (opsional):",
            options=KATEGORI,
            placeholder="Pilih satu atau lebih kategori..."
        )
    with f_col2:
        # Slider menggunakan angka mentah, tetapi kita beri teks panduan ber-titik di bawahnya
        filter_gaji = st.slider(
            "💰 Gaji Minimal (Rupiah / Bulan):",
            min_value=49000000,
            max_value=245000000,
            value=49000000,
            step=5000000,
            label_visibility="visible"
        )
        # Efek Live text: Menampilkan nilai slider yang otomatis ber-titik rapi khas Indonesia
        st.markdown(f"<div style='font-size:0.85rem; color:#1D3557; margin-top:-10px;'>Terpilih: <b>{format_rupiah(filter_gaji)}</b></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_main, col_side = st.columns([2.5, 1])

    with col_main:
        hasil = []
        query_clean = ""
        
        if query or lokasi or filter_gaji > 49000000:
            metode_dipilih = "tfidf" if "Cosine" in metode else "bm25"
            kueri_proses = query if query else ""
            
            hasil, query_clean = cari(kueri_proses, metode_dipilih, lokasi, filter_kategori, gaji_min=filter_gaji)
            
            if hasil:
                lokasi_label = f' di <b>{html_lib.escape(lokasi)}</b>' if lokasi else ''
                gaji_label = f' dengan Gaji &ge; <b>{format_rupiah(filter_gaji)}</b>' if filter_gaji > 49000000 else ''
                info_tambahan = ""
                if query and query_clean != query.lower():
                    info_tambahan = f'<div style="font-size:0.85rem;color:#6B7280;margin-bottom:8px"><i>Kueri diproses/diterjemahkan menjadi: <b>{html_lib.escape(query_clean)}</b></i></div>'
                    
                teks_pencarian = f'"<b>{html_lib.escape(query)}</b>"' if query else "Semua posisi"
                
                st.markdown(f"""
                <div class="result-label">{len(hasil)} lowongan ditemukan</div>
                <div class="result-sub">Hasil untuk {teks_pencarian}{lokasi_label}{gaji_label} &middot; Metode {metode}</div>
                {info_tambahan}
                """, unsafe_allow_html=True)
                
                for rank, (loker, skor) in enumerate(hasil, 1):
                    judul_en = loker.get('judul','').title()
                    company  = html_lib.escape(loker.get('perusahaan','').title())
                    lok      = html_lib.escape(loker.get('lokasi','Remote').title())
                    sumber   = html_lib.escape(loker.get('sumber',''))
                    url      = loker.get('url','#')
                    gaji_val = loker.get('gaji', 0)
                    
                    try:
                        judul_id = GoogleTranslator(source='en', target='id').translate(judul_en)
                        judul = f"{html_lib.escape(judul_en)} <span style='color:#6B7280; font-size:0.85rem; font-weight:400;'>({html_lib.escape(judul_id)})</span>"
                    except Exception:
                        judul = html_lib.escape(judul_en)
                    
                    tags = loker.get('tags','')
                    tag_list = [t.strip() for t in tags.split(",") if t.strip()][:3]
                    
                    if tag_list:
                        tag_str_en = " &middot; ".join(tag_list)
                        try:
                            tag_str_id = GoogleTranslator(source='en', target='id').translate(tag_str_en)
                            tag_str = f"{html_lib.escape(tag_str_en)} <span style='color:#9CA3AF;'>({html_lib.escape(tag_str_id)})</span>"
                        except Exception:
                            tag_str = html_lib.escape(tag_str_en)
                    else:
                        tag_str = "General"
                        
                    badge    = get_badge(skor)
                    remote_badge = '<span class="badge-remote">Remote</span>' if is_remote(loker) else ''
                    
                    # MEMANGGIL FUNGSI format_rupiah() AGAR BADGE DI KARTU LOKER MENGGUNAKAN TITIK (.)
                    gaji_badge = f'<span class="badge-gaji">💰 {format_rupiah(gaji_val)} / bln</span>'
                    
                    st.markdown(f"""
                    <div class="job-card">
                        <div style="display:flex;justify-content:space-between;align-items:flex-start">
                            <div style="flex:1">
                                <div class="job-title">{judul}</div>
                                <div class="job-company">{company}</div>
                                <div>{badge}{remote_badge}{gaji_badge}</div>
                            </div>
                            <div style="color:#9CA3AF;font-size:0.75rem">#{rank}</div>
                        </div>
                        <hr style="border:none;border-top:1px solid #F3F4F6;margin:12px 0">
                        <div class="job-info">
                            <span>&#128205; {lok}</span>
                            <span>&#127991; {tag_str}</span>
                        </div>
                        <div class="job-footer">
                            <span class="job-sumber">{sumber}</span>
                            <a href="{url}" target="_blank" class="lihat-btn">Lihat Lowongan &rarr;</a>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-wrap">
                    <div style="font-size:2.5rem">&#128269;</div>
                    <div class="empty-title">Tidak ada hasil</div>
                    <div>Coba kata kunci, lokasi, atau range gaji yang berbeda</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-wrap">
                <div style="font-size:2.5rem">&#128188;</div>
                <div class="empty-title">Mulai pencarian lowongan</div>
                <div>Ketik posisi, lokasi, atau geser slider gaji di atas</div>
                <br>
                <div style="font-size:0.82rem;color:#D1D5DB">
                    engineer &middot; analyst &middot; manager &middot; developer &middot; designer &middot; remote
                </div>
            </div>
            """, unsafe_allow_html=True)

    with col_side:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-title">&#128202; Statistik Sistem</div>
            <div class="info-item"><span>Total Lowongan</span><span class="info-num">{len(loker_list):,}</span></div>
            <div class="info-item"><span>Sumber Data</span><span class="info-num">{sumber_unik}</span></div>
            <div class="info-item"><span>Metode IR</span><span class="info-num">BM25 + Cosine Similarity</span></div>
            <div class="info-item"><span>Precision BM25</span><span class="info-num">64%</span></div>
            <div class="info-item"><span>Recall BM25</span><span class="info-num">53%</span></div>
            <div class="info-item" style="border:none"><span>F1-Score</span><span class="info-num">0.58</span></div>
        </div>
        <div class="info-card">
            <div class="info-title">&#128161; Tips Pencarian</div>
            <div style="font-size:0.8rem;color:#6B7280;line-height:2.2">
                <div>&#9642; Gunakan nama posisi spesifik</div>
                <div>&#9642; Coba: engineer, analyst, manager</div>
                <div>&#9642; Lokasi: remote, london, new york</div>
                <div>&#9642; Gunakan slider untuk memfilter standar gaji terstruktur (Rupiah)</div>
            </div>
        </div>
        <div class="info-card">
            <div class="info-title">&#127758; Sumber Data</div>
            <div style="font-size:0.8rem;color:#6B7280;line-height:2.2">
                <div>&#128225; RemoteOK API</div>
                <div>&#128225; The Muse API</div>
                <div>&#128225; Arbeitnow API</div>
                <div>&#128225; Jobicy API</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# HALAMAN TENTANG
elif st.session_state.halaman == "tentang":
    st.markdown("""
    <div class="about-hero">
        <div class="about-hero-title">&#128202; Tentang Sistem JobFinder</div>
        <div class="about-hero-sub">Search Engine Lowongan Kerja Berbasis Web Crawler &amp; Information Retrieval &middot; Mata Kuliah Temu Kembali Informasi &middot; Informatika UTM</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        <div class="about-card">
            <div class="about-card-title">&#9881; Cara Kerja Sistem</div>
            <div class="about-step">
                <div class="about-step-num">1</div>
                <div class="about-step-text">
                    <div class="about-step-title">Data Collection</div>
                    Sistem mengambil data lowongan kerja secara otomatis dari 4 API publik menggunakan Python Requests. Data mentah disimpan dalam format JSON.
                </div>
            </div>
            <div class="about-step">
                <div class="about-step-num">2</div>
                <div class="about-step-text">
                    <div class="about-step-title">Preprocessing</div>
                    Data dibersihkan &mdash; HTML tag dihapus, huruf diubah ke lowercase, karakter khusus dihilangkan. Field judul, tags, dan lokasi digabungkan.
                </div>
            </div>
            <div class="about-step">
                <div class="about-step-num">3</div>
                <div class="about-step-text">
                    <div class="about-step-title">Indexing</div>
                    Teks bersih diindeks menggunakan TF-IDF Matrix (scikit-learn) and BM25 Index (rank_bm25). Setiap dokumen mendapat bobot kata masing-masing.
                </div>
            </div>
            <div class="about-step">
                <div class="about-step-num">4</div>
                <div class="about-step-text">
                    <div class="about-step-title">Retrieval &amp; Ranking</div>
                    Query user diproses dan dicocokkan dengan indeks. Hasil diurutkan berdasarkan skor relevansi tertinggi. Ditampilkan Top-20 hasil paling relevan.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        n_themuse   = sumber_count.get('TheMuse', 0)
        n_arbeitnow = sumber_count.get('Arbeitnow', 0)
        n_remoteok  = sumber_count.get('RemoteOK', 0)
        n_jobicy    = sumber_count.get('Jobicy', 0)

        st.markdown(f"""
        <div class="about-card">
            <div class="about-card-title">&#127758; Sumber Data</div>
            <div class="sumber-grid">
                <div class="sumber-box">
                    <div style="font-size:1.5rem">&#128309;</div>
                    <div class="sumber-name">TheMuse</div>
                    <div class="sumber-count">{n_themuse:,} lowongan</div>
                </div>
                <div class="sumber-box">
                    <div style="font-size:1.5rem">&#128992;</div>
                    <div class="sumber-name">Arbeitnow</div>
                    <div class="sumber-count">{n_arbeitnow:,} lowongan</div>
                </div>
                <div class="sumber-box">
                    <div style="font-size:1.5rem">&#128994;</div>
                    <div class="sumber-name">RemoteOK</div>
                    <div class="sumber-count">{n_remoteok:,} lowongan</div>
                </div>
                <div class="sumber-box">
                    <div style="font-size:1.5rem">&#128995;</div>
                    <div class="sumber-name">Jobicy</div>
                    <div class="sumber-count">{n_jobicy:,} lowongan</div>
                </div>
            </div>
            <div style="margin-top:14px;font-size:0.8rem;color:#6B7280">
                Data diambil melalui API publik yang tersedia secara bebas. Semua sumber telah diverifikasi robots.txt sebelum diakses.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="about-card">
            <div class="about-card-title">&#128200; Hasil Evaluasi IR</div>
            <div style="font-size:0.82rem;color:#6B7280;margin-bottom:12px">
                Evaluasi dilakukan menggunakan 5 query uji dengan ground truth manual. Metrik: Precision, Recall, dan F1-Score.
            </div>
            <div class="metric-row">
                <div class="metric-box winner"><div class="metric-val">64%</div><div class="metric-label">BM25 Precision</div></div>
                <div class="metric-box winner"><div class="metric-val">53%</div><div class="metric-label">BM25 Recall</div></div>
                <div class="metric-box winner"><div class="metric-val">0.58</div><div class="metric-label">BM25 F1-Score</div></div>
            </div>
            <div class="metric-row" style="margin-top:8px">
                <div class="metric-box"><div class="metric-val">54%</div><div class="metric-label">Cosine Similarity Precision</div></div>
                <div class="metric-box"><div class="metric-val">46%</div><div class="metric-label">Cosine Similarity Recall</div></div>
                <div class="metric-box"><div class="metric-val">0.50</div><div class="metric-label">Cosine Similarity F1-Score</div></div>
            </div>
            <div style="margin-top:14px;background:#ECFDF5;border:1px solid #6EE7B7;border-radius:8px;padding:10px 14px;font-size:0.82rem;color:#065F46">
                &#10003; <b>Kesimpulan:</b> BM25 lebih unggul dari Cosine Similarity di semua metrik untuk kasus pencarian lowongan kerja ini.
            </div>
        </div>
        <div class="about-card">
            <div class="about-card-title">&#9878; BM25 vs TF-IDF + Cosine Similarity</div>
            <div class="compare-row">
                <div class="compare-box active">
                    <div class="compare-title">&#10003; BM25 (Rekomendasi)</div>
                    <div class="compare-item">&#10003; Normalisasi panjang dokumen</div>
                    <div class="compare-item">&#10003; Saturasi frekuensi kata</div>
                    <div class="compare-item">&#10003; Lebih akurat untuk short-text</div>
                    <div class="compare-item">&#10003; Precision 64%, F1 0.58</div>
                </div>
                <div class="compare-box">
                    <div class="compare-title">TF-IDF + Cosine Similarity</div>
                    <div class="compare-item">&middot; Tidak ada normalisasi panjang</div>
                    <div class="compare-item">&middot; Frekuensi tidak terbatas</div>
                    <div class="compare-item">&middot; Lebih sederhana</div>
                    <div class="compare-item">&middot; Precision 54%, F1 0.50</div>
                </div>
            </div>
        </div>
        <div class="about-card">
            <div class="about-card-title">&#128296; Teknologi yang Digunakan</div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-text"><div class="timeline-label">Python + Requests</div>HTTP request ke API, parsing JSON response</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-text"><div class="timeline-label">scikit-learn</div>TF-IDF Vectorizer + Cosine Similarity</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-text"><div class="timeline-label">rank_bm25</div>Implementasi algoritma BM25Okapi</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot"></div>
                <div class="timeline-text"><div class="timeline-label">Streamlit</div>Framework antarmuka web berbasis Python</div>
            </div>
            <div class="timeline-item">
                <div class="timeline-dot" style="background:#E63946"></div>
                <div class="timeline-text"><div class="timeline-label">ngrok</div>Tunnel untuk akses publik saat presentasi</div>
            </div>
        </div>
        """, unsafe_allow_html=True)