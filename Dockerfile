# Gunakan image Python
FROM python:3.10-slim

# Set folder kerja
WORKDIR /app

# --- TAMBAHAN PENTING ---
# Install library sistem yang dibutuhkan XGBoost/Scikit-learn
RUN apt-get update && apt-get install -y \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*
# ------------------------

# Copy requirements dulu
COPY requirements.txt .

# Install library python
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file project (termasuk .joblib)
COPY . .

# Expose port
EXPOSE 5000

# Jalankan aplikasi
CMD ["uvicorn", "app_trans:app", "--host", "0.0.0.0", "--port", "5000"]
