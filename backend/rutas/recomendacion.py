"""
Rutas de Recomendación.
Responsable: David   (Semanas 3 y 4 del cronograma)

Por hacer:
  POST /api/recomendaciones -> recibe claves de ingredientes y devuelve:
     - 'completas': recetas que se pueden hacer con lo que hay
     - 'casi': recetas a las que les falta 1 ingrediente (con la lista de faltantes)
     Básicos que siempre se asumen: sal, aceite, azúcar. Los opcionales no cuentan.

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Recomendación"])


# Escribe tus endpoints debajo de esta línea.
