import json
import re

def bersihkan_teks(teks):
    if not teks:
        return ""
    # Hapus HTML tag
    teks = re.sub(r'<[^>]+>', ' ', teks)
    # Hapus karakter aneh
    teks = re.sub(r'[^a-zA-Z0-9\s]', ' ', teks)
    # Huruf kecil semua
    teks = teks.lower()
    # Hapus spasi berlebih
    teks = ' '.join(teks.split())
    return teks

# Baca data loker
with open("data_loker.json", "r") as f:
    loker_list = json.load(f)

# Bersihkan tiap loker
hasil_bersih = []
for loker in loker_list:
    loker_bersih = {
        "judul"      : bersihkan_teks(loker["judul"]),
        "perusahaan" : bersihkan_teks(loker["perusahaan"]),
        "lokasi"     : bersihkan_teks(loker["lokasi"]),
        "tags"       : bersihkan_teks(loker["tags"]),
        "url"        : loker["url"],
        "sumber"     : loker.get("sumber", ""),
        # Gabungkan semua teks jadi satu untuk diindeks
        "teks_gabung": bersihkan_teks(
            loker["judul"] + " " + 
            loker["tags"] + " " + 
            loker["lokasi"]
        )
    }
    hasil_bersih.append(loker_bersih)
    print(f"✅ {loker_bersih['judul']}")

# Simpan hasil bersih
with open("data_bersih.json", "w") as f:
    json.dump(hasil_bersih, f, indent=2)

print(f"\n💾 Disimpan ke data_bersih.json!")
print(f"Total: {len(hasil_bersih)} loker")