from flask import Flask, request, jsonify
import json
import requests

app = Flask(__name__)

with open('D:\Internship SPIL\Project_1\procedure.json', 'r', encoding='utf-8') as f:
    prosedur = json.load(f)

informasi_ringkas = []
for item in prosedur["proses_penawaran_harga"]:
    langkah = item.get('langkah', '')
    deskripsi = item.get('deskripsi', '')
        
    informasi_ringkas.append({
        "langkah": langkah,
        "deskripsi": deskripsi
    })

ringkasan_json = json.dumps(informasi_ringkas, indent=2)

PROMPT_STATIC = """
Berikut adalah contoh prosedur beserta deskripsinya dalam bentuk JSON:

{referensi_data}

Tugas Anda:
1. Berikan kritik dengan cara kalimat langkah sebelumnya menjadi kalimat langkah baru dengan mempertimbangkan logika, kesinambungan antar langkah, dan para pemangku kepentingan

Catatan:
1. Gunakan daftar pada file JSON diatas hanya sebagai contoh kasus anda dalam memberikan kritik maupun saran dan jangan menjiplak
2. Gunakan Bahasa Indonesia untuk memberikan respon
3. Anda tidak perlu menampilkan data yang menjadi referensi Anda
4. Jangan melakukan redundansi dalam memprediksi masalah yang sama atau mirip
5. Jangan menghilangkan konteks atau istilah penting yang digunakan

Contoh:
Input:
1. Prosedur: {prosedur}
2. Langkah yang akan dikritisi: {langkah}

Output yang diharapkan:
1. Langkah baru (deskripsi langkah yang baru)
2. Kritik (alasan membuat langkah baru)

Catatan:
1. Output yang diberikan hanya pada langkah {langkah} dan abaikan langkah lainnya
2. Huruf pada output jangan ditebalkan/bold dan hilangkan langsung output langkah baru dan kritik, tidak perlu kalimat pembuka
"""

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "api-key"
GROQ_MODEL = "llama3-70b-8192"

@app.route('/prediksi-risiko', methods=['POST'])
def prediksi_risiko():
    data_input = request.get_json()
    prosedur_input = data_input.get("steps")
    langkah_input = data_input.get("current_step")

    if not prosedur_input:
        return jsonify({"error": "Field 'prosedur' wajib diisi"}), 400

    user_prompt = PROMPT_STATIC.format(referensi_data=ringkasan_json, prosedur=prosedur_input, langkah=langkah_input)

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten yang membantu mengkritisi sebuah langkah prosedur dan memperbaikinya."},
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

    return jsonify({"prosedur": prosedur_input, "prediksi": prediksi})

if __name__ == '__main__':
    app.run(debug=True)
