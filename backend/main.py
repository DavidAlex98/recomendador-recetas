# Servidor de RecetApp.
# Responsable: David
#
# Cómo encenderlo (desde la carpeta backend):
#     python -m uvicorn main:app --reload
#
# Luego abrir:
#     http://localhost:8000        la aplicación
#     http://localhost:8000/docs   para probar los endpoints

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from rutas import admin, despensa, ejemplo, favoritos, ingredientes, recetas, recomendacion, usuarios

app = FastAPI(title="RecetApp")

# Rutas de cada integrante
app.include_router(ejemplo.router)
app.include_router(ingredientes.router)    # Shanda
app.include_router(recetas.router)         # Shanda
app.include_router(despensa.router)        # Shanda
app.include_router(usuarios.router)        # Rubí
app.include_router(recomendacion.router)   # David
app.include_router(favoritos.router)       # Cristian
app.include_router(admin.router)           # Brandon

# Páginas del frontend (esta línea va al final)
app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
