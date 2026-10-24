# Servidor de RecetApp
# Responsable: David
#
# Encender (desde la carpeta backend):  python -m uvicorn main:app --reload

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from db import CARPETA_PROYECTO
from rutas import admin, despensa, ejemplo, favoritos, historial, ingredientes, recetas, recomendacion, reconocer, usuarios

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
app.include_router(reconocer.router)       # David

# Páginas del frontend (esta línea va al final)
app.mount("/", StaticFiles(directory=CARPETA_PROYECTO / "frontend", html=True), name="frontend")
