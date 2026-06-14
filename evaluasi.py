import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi

# Load data
with open("data_bersih.json", "r") as f:
    loker_list = json.load(f)

dokumen = [l["teks_gabung"] for l in loker_list]

# Setup TF-IDF & BM25
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(dokumen)
bm25 = BM25Okapi([d.split() for d in dokumen])

ground_truth = {
    "frontend engineer": [
        i for i, l in enumerate(loker_list)
        if any(k in l["teks_gabung"] for k in ["frontend", "front end", "web engineer", "react", "vue"])
    ],
    "data analyst": [
        i for i, l in enumerate(loker_list)
        if any(k in l["teks_gabung"] for k in ["data analyst", "analytics", "data science", "sql"])
    ],
    "software engineer": [
        i for i, l in enumerate(loker_list)
        if any(k in l["teks_gabung"] for k in ["software engineer", "developer", "programming", "backend"])
    ],
    "marketing manager": [
        i for i, l in enumerate(loker_list)
        if any(k in l["teks_gabung"] for k in ["marketing", "brand", "campaign", "social media"])
    ],
    "product manager": [
        i for i, l in enumerate(loker_list)
        if any(k in l["teks_gabung"] for k in ["product manager", "product", "roadmap", "agile"])
    ],
}

# ========================
# Fungsi Cari
# ========================
def cari(query, metode="bm25", top_k=10):
    query = query.lower()
    if metode == "tfidf":
        skor = cosine_similarity(vectorizer.transform([query]), tfidf_matrix).flatten()
    else:
        skor = bm25.get_scores(query.split())
    ranking = sorted(enumerate(skor), key=lambda x: x[1], reverse=True)
    return [i for i, s in ranking[:top_k]]

# ========================
# Hitung Precision & Recall
# ========================
def evaluasi(metode, top_k=10):
    print(f"\n{'='*50}")
    print(f"EVALUASI METODE: {metode.upper()} | Top-{top_k}")
    print(f"{'='*50}")
    
    total_precision = 0
    total_recall = 0
    
    for query, relevan in ground_truth.items():
        hasil = cari(query, metode=metode, top_k=top_k)
        
        # Hitung
        benar = len(set(hasil) & set(relevan))
        precision = benar / len(hasil) if hasil else 0
        recall = benar / len(relevan) if relevan else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        total_precision += precision
        total_recall += recall
        
        print(f"\nQuery  : '{query}'")
        print(f"Relevan: {len(relevan)} dokumen")
        print(f"Hasil  : {len(hasil)} dokumen")
        print(f"Benar  : {benar} dokumen")
        print(f"  Precision : {precision:.4f} ({precision*100:.1f}%)")
        print(f"  Recall    : {recall:.4f} ({recall*100:.1f}%)")
        print(f"  F1-Score  : {f1:.4f}")
    
    # Rata-rata
    n = len(ground_truth)
    avg_p = total_precision / n
    avg_r = total_recall / n
    avg_f1 = 2 * (avg_p * avg_r) / (avg_p + avg_r) if (avg_p + avg_r) > 0 else 0
    
    print(f"\n{'─'*50}")
    print(f"RATA-RATA (MAP):")
    print(f"  Avg Precision : {avg_p:.4f} ({avg_p*100:.1f}%)")
    print(f"  Avg Recall    : {avg_r:.4f} ({avg_r*100:.1f}%)")
    print(f"  Avg F1-Score  : {avg_f1:.4f}")
    
    return avg_p, avg_r, avg_f1

# Jalankan evaluasi keduanya
p_bm25, r_bm25, f_bm25   = evaluasi("bm25")
p_tfidf, r_tfidf, f_tfidf = evaluasi("tfidf")

# Perbandingan akhir
print(f"\n{'='*50}")
print("PERBANDINGAN BM25 vs TF-IDF")
print(f"{'='*50}")
print(f"{'Metode':<10} {'Precision':>10} {'Recall':>10} {'F1-Score':>10}")
print(f"{'─'*42}")
print(f"{'BM25':<10} {p_bm25:>10.4f} {r_bm25:>10.4f} {f_bm25:>10.4f}")
print(f"{'TF-IDF':<10} {p_tfidf:>10.4f} {r_tfidf:>10.4f} {f_tfidf:>10.4f}")

if f_bm25 > f_tfidf:
    print(f"\n✅ BM25 lebih baik dari TF-IDF!")
else:
 