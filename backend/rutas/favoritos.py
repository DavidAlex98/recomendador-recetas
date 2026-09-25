"""
Rutas de Favoritos, historial y lista de compras.
Responsable: Cristian   (Semanas 4 a 6 del cronograma)

Por hacer:
  Semana 4: POST, DELETE y GET /api/favoritos
  Semana 5: GET /api/historial (recetas consultadas)
  Semana 6: lista de compras con estados: generada -> comprada -> cerrada

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Favoritos, historial y lista de compras"])


# Escribe tus endpoints debajo de esta línea.
