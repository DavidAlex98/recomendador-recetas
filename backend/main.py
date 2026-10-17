# Servidor de RecetApp.
# Responsable: David
#
# Cómo encenderlo (desde la carpeta backend):
#     python -m uvicorn main:app --reload
# O desde la carpeta principal:
#     python -m uvicorn main:app --reload --app-dir backend
#
# Luego abrir:
#     http://localhost:8000        la aplicación
#     http://localhost:8000/docs   para probar los endpoints

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from db import CARPETA_PROYECTO
from rutas import admin, despensa, ejemplo, favoritos, historial, ingredientes, recetas, recomendacion, usuarios

app = FastAPI(title="RecetApp")

# Rutas de cada integrante
app.include_router(ejemplo.router)
app.include_router(ingredientes.router)    # Shanda
app.include_router(recetas.router)         # David
app.include_router(despensa.router)        # Shanda
app.include_router(usuarios.router)        # Rubí
app.include_router(recomendacion.router)   # David
app.include_router(favoritos.router)       # Cristian
app.include_router(admin.router)           # Brandon
app.include_router(historial.router)       # David

# Páginas del frontend (esta línea va al final)
app.mount("/", StaticFiles(directory=CARPETA_PROYECTO / "frontend", html=True), name="frontend")
