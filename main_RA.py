from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

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

PROMPT_STATIC = """
Berikut adalah contoh daftar kegiatan dan risikonya dalam bentuk JSON:

{referensi_data}

Tugas Anda:
1. Tinjau dan prediksi masalah, resiko, pengendalian resiko, dan tindakan perbaikan yang kemungkinan akan muncul pada tahap {nama_kegiatan}
2. Fokus untuk prediksi terhadap tahap {nama_kegiatan} dan jangan terpengaruh oleh tahap lainnya
3. Berikan hasil prediksi yang berupa pasangan yang terdiri dari masalah, resiko, pengendalian resiko, dan tindakan perbaikan yang berhubungan

Catatan:
1. Gunakan daftar kegiatan pada file JSON diatas hanya sebagai contoh kasus anda dalam memprediksi dan jangan menjiplak
2. Gunakan Bahasa Indonesia untuk memberikan respon
3. Anda tidak perlu menampilkan data yang menjadi referensi Anda
4. Jangan melakukan redundansi dalam memprediksi masalah
5. Anda tidak dibatasi dengan jumlah kandidat prediksi anda

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

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "api-key"
GROQ_MODEL = "llama3-70b-8192"

@app.route('/prediksi-risiko', methods=['POST'])
def prediksi_risiko():
    data_input = request.get_json()
    nama_kegiatan = data_input.get("kegiatan")

    if not nama_kegiatan:
        return jsonify({"error": "Field 'kegiatan' wajib diisi"}), 400

    user_prompt = PROMPT_STATIC.format(referensi_data=ringkasan_json, nama_kegiatan=nama_kegiatan)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten yang membantu mengidentifikasi masalah dan resiko sekaligus solusi yang kemungkinan terjadi pada suatu kegiatan."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.4
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return jsonify({"error": "Gagal meminta prediksi dari API Groq", "detail": response.text}), 500

    result = response.json()
    prediksi = result['choices'][0]['message']['content']

    return jsonify({"kegiatan": nama_kegiatan, "prediksi": prediksi})

if __name__ == '__main__':
    app.run(debug=True)
