FROM python:3.11-slim

# Instalamos dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Aprovechamos el cache de capas de Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos el puerto
EXPOSE 8000

# Usamos un script de arranque o comando directo optimizado
# Agregamos --proxy-headers si vas a usar Render/CloudRun
CMD python -m alembic upgrade head && \
    python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers