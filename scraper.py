import requests
import json
import time

headers = {"User-Agent": "Mozilla/5.0"}

def ambil_remoteok():
    print("📡 Mengambil dari RemoteOK...")
    try:
        r = requests.get("https://remoteok.com/api", headers=headers, timeout=15)
        data = r.json()
        hasil = []
        for item in data:
            if "id" in item and "position" in item:
                hasil.append({
                    "judul"     : item.get("position", "-"),
                    "perusahaan": item.get("company", "-"),
                    "lokasi"    : item.get("location", "Remote"),
                    "tags"      : ", ".join(item.get("tags", [])),
                    "deskripsi" : item.get("description", ""),
                    "url"       : item.get("url", "-"),
                    "sumber"    : "RemoteOK"
                })
        print(f"✅ RemoteOK: {len(hasil)} loker")
        return hasil
    except Exception as e:
        print(f"❌ RemoteOK error: {e}")
        return []

def ambil_themuse():
    print("📡 Mengambil dari The Muse...")
    hasil = []
    for page in range(1, 26):  # ambil 25 halaman (~500 loker)
        try:
            url = f"https://www.themuse.com/api/public/jobs?page={page}&level=Mid%20Level"
            r = requests.get(url, timeout=15)
            data = r.json()
            results = data.get("results", [])
            if not results:
                break  # halaman kosong, berhenti
            for item in results:
                lokasi = ""
                if item.get("locations"):
                    lokasi = item["locations"][0].get("name", "Remote")
                hasil.append({
                    "judul"     : item.get("name", "-"),
                    "perusahaan": item.get("company", {}).get("name", "-"),
                    "lokasi"    : lokasi,
                    "tags"      : item.get("categories", [{}])[0].get("name", "") if item.get("categories") else "",
                    "deskripsi" : item.get("contents", ""),
                    "url"       : item.get("refs", {}).get("landing_page", "-"),
                    "sumber"    : "TheMuse"
                })
            time.sleep(0.3)  # jeda supaya tidak di-rate-limit
        except Exception as e:
            print(f"❌ The Muse halaman {page} error: {e}")
    print(f"✅ The Muse: {len(hasil)} loker")
    return hasil

def cek_api_baru():
    apis = [
        "https://jobicy.com/api/v2/remote-jobs",
        "https://findwork.dev/api/jobs/",
        "https://www.reed.co.uk/api/1.0/search?keywords=developer",
    ]
    
    for url in apis:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            print(f"\nURL: {url[:50]}")
            print(f"Status: {r.status_code}")
            print(f"Preview: {r.text[:200]}")
        except Exception as e:
            print(f"❌ Error: {e}")

cek_api_baru()

def ambil_arbeitnow():
    print("📡 Mengambil dari Arbeitnow...")
    hasil = []
    page = 1
    while True:
        try:
            url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
            r = requests.get(url, headers=headers, timeout=15)
            data = r.json()
            jobs = data.get("data", [])
            if not jobs:
                break
            for item in jobs:
                hasil.append({
                    "judul"     : item.get("title", "-"),
                    "perusahaan": item.get("company_name", "-"),
                    "lokasi"    : item.get("location", "Remote"),
                    "tags"      : ", ".join(item.get("tags", [])),
                    "deskripsi" : item.get("description", ""),
                    "url"       : item.get("url", "-"),
                    "sumber"    : "Arbeitnow"
                })
            # stop jika sudah cukup banyak atau tidak ada halaman berikutnya
            if len(hasil) >= 150 or not data.get("links", {}).get("next"):
                break
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"❌ Arbeitnow halaman {page} error: {e}")
            break
    print(f"✅ Arbeitnow: {len(hasil)} loker")
    return hasil

def ambil_jobicy():
    print("📡 Mengambil dari Jobicy...")
    hasil = []
    try:
        url = "https://jobicy.com/api/v2/remote-jobs?count=50"
        r = requests.get(url, headers=headers, timeout=15)
        data = r.json()
        jobs = data.get("jobs", [])
        for item in jobs:
            hasil.append({
                "judul"     : item.get("jobTitle", "-"),
                "perusahaan": item.get("companyName", "-"),
                "lokasi"    : item.get("jobGeo", "Remote"),
                "tags"      : item.get("jobIndustry", [""])[0] if item.get("jobIndustry") else "",
                "deskripsi" : item.get("jobDescription", ""),
                "url"       : item.get("url", "-"),
                "sumber"    : "Jobicy"
            })
    except Exception as e:
        print(f"❌ Jobicy error: {e}")
    print(f"✅ Jobicy: {len(hasil)} loker")
    return hasil

# Gabungkan semua sumber
print("=" * 50)
print("🚀 Memulai scraping dari semua sumber...")
print("=" * 50)

semua = []
semua += ambil_remoteok()
semua += ambil_themuse()
semua += ambil_arbeitnow()
semua += ambil_jobicy()

with open("data_loker.json", "w") as f:
    json.dump(semua, f, indent=2)

print(f"\n{'=' * 50}")
print(f"🎉 Total gabungan: {len(semua)} loker tersimpan!")
print(f"{'=' * 50}")