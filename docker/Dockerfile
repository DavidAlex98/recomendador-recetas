# Contenedor de la app FastAPI
# Responsable: David

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY datos ./datos
COPY base_datos ./base_datos
COPY frontend ./frontend

WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
