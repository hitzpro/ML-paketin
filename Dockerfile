# Gunakan image Python yang ringan
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements dulu (agar cache layer optimal)
COPY requirements.txt .

# Install dependencies
# --no-cache-dir agar image kecil
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua sisa file (model .joblib dan script)
COPY . .

# Expose port (Render biasanya baca env PORT, tapi kita set default 5000)
EXPOSE 5000

# Perintah menjalankan server
# Host 0.0.0.0 wajib untuk Docker
CMD ["uvicorn", "app_trans:app", "--host", "0.0.0.0", "--port", "5000"]