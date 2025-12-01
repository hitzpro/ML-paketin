import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# --- 1. Load Model & Preprocessor ---
try:
    print("⏳ Memuat model...")
    # Pastikan nama file ini BENAR ada di folder yang sama
    model = joblib.load("model_trans.joblib")
    preprocessor = joblib.load("preprocessor_trans.joblib")
    label_encoder = joblib.load("encoder_label_trans.joblib")
    print("✅ Model berhasil dimuat!")
except Exception as e:
    print(f"❌ Error loading files: {e}")
    # Biar server gak langsung mati kalau file gak ketemu, tapi nanti error pas predict
    model = None 

app = FastAPI()

# --- 2. Definisikan Input (Validasi Otomatis) ---
class CustomerData(BaseModel):
    # Kolom Kategori
    plan_type: str
    device_brand: str
    
    # Kolom Numerik
    avg_data_usage_gb: float
    pct_video_usage: float
    avg_call_duration: float
    sms_freq: int
    monthly_spend: float
    topup_freq: int
    travel_score: float
    complaint_count: int

@app.get("/")
def home():
    return {"message": "Server ML (FastAPI) is Running! Send POST to /predict"}

@app.post("/predict")
def predict(data: CustomerData):
    if model is None:
        raise HTTPException(status_code=500, detail="Model belum dimuat. Cek file .joblib")

    try:
        # A. Konversi input Pydantic ke DataFrame Pandas
        # Kita susun manual dictionary-nya agar urutan kolomnya PASTI benar sesuai training
        input_data = {
            "plan_type": [data.plan_type],
            "device_brand": [data.device_brand],
            "avg_data_usage_gb": [data.avg_data_usage_gb],
            "pct_video_usage": [data.pct_video_usage],
            "avg_call_duration": [data.avg_call_duration],
            "sms_freq": [data.sms_freq],
            "monthly_spend": [data.monthly_spend],
            "topup_freq": [data.topup_freq],
            "travel_score": [data.travel_score],
            "complaint_count": [data.complaint_count]
        }
        
        # Buat DataFrame
        input_df = pd.DataFrame(input_data)

        # B. Preprocessing (Transform)
        # Preprocessor ini pintar, dia tau mana kolom kategori/angka dari saat training dulu
        processed_data = preprocessor.transform(input_df)

        # C. Prediksi
        prediction_index = model.predict(processed_data)
        
        # Ambil nilai integer prediksi (misal: 0, 1, 2)
        pred_value = int(prediction_index[0])

        # D. Decoding Label (misal: 0 -> "General Offer")
        label_result = label_encoder.inverse_transform(prediction_index)[0]

        return {
            "label_prediction": label_result,
            "prediction_value": pred_value
        }

    except Exception as e:
        # Tangkap error apapun (misal kolom kurang/tipe salah)
        raise HTTPException(status_code=500, detail=f"Prediction Error: {str(e)}")

# Script agar bisa dijalankan langsung dengan `python app_trans.py`
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)