"""
Punto de entrada del servidor RecetApp.
Responsable: David

Este archivo solo une las piezas. Cada integrante escribe sus endpoints en su
propio archivo dentro de backend/rutas/, así nadie edita el mismo archivo.

Cómo correr el servidor (desde la carpeta backend/):
    uvicorn main:app --reload

Luego abre en el navegador:
    http://localhost:8000        -> la aplicación (carpeta frontend/)
    http://localhost:8000/docs   -> documentación y pruebas de la API
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from rutas import admin, despensa, ejemplo, favoritos, ingredientes, recetas, recomendacion, usuarios

app = FastAPI(title="RecetApp API", description="Recomendación de recetas según tu despensa")

# 1. Registrar las rutas de cada módulo
app.include_router(ejemplo.router)
app.include_router(ingredientes.router)      # Shanda
app.include_router(recetas.router)           # Shanda
app.include_router(despensa.router)          # Shanda
app.include_router(usuarios.router)          # Rubí
app.include_router(recomendacion.router)     # David
app.include_router(favoritos.router)         # Cristian
app.include_router(admin.router)             # Brandon

# 2. Servir las páginas del frontend. Va al final para no tapar las rutas /api
CARPETA_FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=CARPETA_FRONTEND, html=True), name="frontend")
