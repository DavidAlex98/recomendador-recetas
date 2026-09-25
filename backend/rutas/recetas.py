"""
Rutas de Recetas.
Responsable: Shanda   (Semana 3 del cronograma)

Por hacer:
  GET /api/recetas?buscar=texto -> buscar recetas por nombre (máximo 20)
  GET /api/recetas/{id}         -> detalle: datos, ingredientes y pasos de una receta
     (si el id no existe: raise HTTPException(404, 'Receta no encontrada'))

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Recetas"])


# Escribe tus endpoints debajo de esta línea.
