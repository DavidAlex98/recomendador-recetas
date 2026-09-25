"""
Rutas de Ingredientes.
Responsable: Shanda   (Semana 2 del cronograma)

Por hacer:
  GET /api/ingredientes  -> ingredientes del catálogo JSON agrupados por categoría
     (usa catalogo.INGREDIENTES; no necesita MySQL)

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Ingredientes"])


# Escribe tus endpoints debajo de esta línea.
