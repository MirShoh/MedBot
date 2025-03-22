from flask import Flask, request, jsonify
from google.cloud import vision
import base64
import os

app = Flask(__name__)

# Google Cloud Vision API sozlamalari
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"D:\ARXIV\Dasturlar\MirShoh\MedBot (with Gemini AI)\medbot-vision-key.json"
vision_client = vision.ImageAnnotatorClient()

# Mashhur dori nomlari ro‘yxati
COMMON_DRUGS = {
    "PARACETAMOL", "IBUPROFEN", "ASPIRIN", "AMOXICILLIN", "CETIRIZINE",
    "METFORMIN", "OMEPRAZOLE", "DICLOFENAC", "NUROFEN", "PANADOL",
    "IBUPROFEN FORTE", "ASPIRIN CARDIO", "PARACETAMOL EXTRA",
    "ПАРАЦЕТАМОЛ", "ИБУПРОФЕН", "АСПИРИН"
}

@app.route('/analyze', methods=['POST'])
def analyze_image():
    data = request.json
    image_data = base64.b64decode(data['image'].split(',')[1])
    image = vision.Image(content=image_data)
    response = vision_client.text_detection(image=image)
    
    if not response.text_annotations:
        return jsonify({"drug_info": "Dori nomi aniqlanmadi"})
    
    full_text = response.text_annotations[0].description.lower()
    lines = full_text.split('\n')
    
    potential_drugs = []
    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        line_upper = line.upper()
        if line_upper in COMMON_DRUGS:
            potential_drugs.append(line_upper)
        else:
            words = line.split()
            for i in range(len(words)):
                for j in range(i + 1, min(i + 4, len(words) + 1)):
                    combined = " ".join(words[i:j]).upper()
                    if combined in COMMON_DRUGS:
                        potential_drugs.append(combined)
    
    dori_nomi = max(potential_drugs, key=len) if potential_drugs else "Noma'lum"
    drug_info = f"Dori: {dori_nomi}\nFoydasi: Og‘riq va isitma uchun"
    return jsonify({"drug_info": drug_info})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)