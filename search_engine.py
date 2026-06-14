import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

# Load data
with open("data_bersih.json", "r") as f:
    loker_list = json.load(f)

# Ambil teks gabungan tiap loker
dokumen = [loker["teks_gabung"] for loker in loker_list]

# ========================
# TF-IDF
# ========================
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(dokumen)

# ========================
# BM25
# ========================
tokenized = [doc.split() for doc in dokumen]
bm25 = BM25Okapi(tokenized)

# ========================
# Fungsi Pencarian
# ========================
def cari(query, metode="bm25", top_k=5):
    query = query.lower()
    print(f"\n🔍 Query: '{query}' | Metode: {metode.upper()}")
    print("="*50)

    if metode == "tfidf":
        query_vec = vectorizer.transform([query])
        skor = cosine_similarity(query_vec, tfidf_matrix).flatten()
    else:  # bm25
        skor = bm25.get_scores(query.split())

    # Urutkan berdasarkan skor
    ranking = sorted(enumerate(skor), key=lambda x: x[1], reverse=True)

    for rank, (idx, nilai) in enumerate(ranking[:top_k], 1):
        loker = loker_list[idx]
        print(f"\n#{rank} Skor: {nilai:.4f}")
        print(f"  Judul      : {loker['judul']}")
        print(f"  Perusahaan : {loker['perusahaan']}")
        print(f"  Lokasi     : {loker['lokasi']}")
        print(f"  Tags       : {loker['tags']}")

# Test pencarian
cari("frontend engineer", metode="bm25")
cari("frontend engineer", metode="tfidf")