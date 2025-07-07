import requests
import json

with open('D:\Internship SPIL\Project_1\example.json', 'r', encoding='utf-8') as f:
    data_kegiatan = json.load(f)

informasi_ringkas = []

for item in data_kegiatan:
    kegiatan = item['kegiatan']
    for risiko in item['risiko']:
        masalah = risiko.get('masalah', '')
        resiko_timbul = risiko.get('resiko_yang_timbul', '')
        pengendalian = risiko.get('pengendalian_risiko', '')
        tindakan = risiko.get('tindakan_perbaikan', '')

        informasi_ringkas.append({
            "kegiatan": kegiatan,
            "masalah": masalah,
            "resiko_yang_timbul": resiko_timbul,
            "pengendalian_risiko": pengendalian,
            "tindakan_perbaikan": tindakan
        })


ringkasan_json = json.dumps(informasi_ringkas, indent=2)

kegiatan = input("Masukkan nama kegiatan: ")

prompt_static = """
Berikut adalah daftar kegiatan dan risikonya dalam bentuk JSON:

{referensi_data}

Catatan:
1. Gunakan daftar kegiatan pada file JSON diatas hanya sebagai contoh kasus anda dalam memprediksi dan jangan menjiplak
2. Gunakan Bahasa Indonesia untuk memberikan respon
3. Anda tidak perlu menampilkan data yang menjadi referensi Anda
4. Jangan melakukan redundansi dalam memprediksi masalah yang sama atau mirip

Tugas Anda:
1. Tinjau dan prediksi masalah, resiko, pengendalian resiko, dan tindakan perbaikan yang kemungkinan akan muncul pada tahap {nama_kegiatan}
2. Fokus untuk prediksi terhadap tahap {nama_kegiatan} dan jangan terpengaruh oleh tahap lainnya
3. Berikan hasil prediksi yang berupa pasangan yang terdiri dari masalah, resiko, pengendalian resiko, dan tindakan perbaikan yang berhubungan
4. Anda tidak dibatasi dengan jumlah kandidat prediksi anda

Contoh:
Input:
1. Kegiatan

Output yang diharapkan:
Prediksi 1
1. Masalah
2. Resiko yang timbul
3. Pengendalian resiko (Pencegahan terjadinya masalah)
4. Tindakan perbaikan (Penanganan setelah terjadinya masalah)

Prediksi 2
1. Masalah
2. Resiko yang timbul
3. Pengendalian resiko (Pencegahan terjadinya masalah)
4. Tindakan perbaikan (Penanganan setelah terjadinya masalah)
"""

user_prompt = prompt_static.format(referensi_data=ringkasan_json, nama_kegiatan=kegiatan)

model = "llama3-70b-8192"
API_KEY = "api-key"

url = "https://api.groq.com/openai/v1/chat/completions"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "system", "content": "Kamu adalah asisten yang membantu mengidentifikasi masalah dan resiko sekaligus solusi yang kemungkinan terjadi pada suatu kegiatan."},
        {"role": "user", "content": user_prompt}
    ],
    "temperature": 0.4
}

response = requests.post(url, headers=headers, json=data)
print(response.json()['choices'][0]['message']['content'])
