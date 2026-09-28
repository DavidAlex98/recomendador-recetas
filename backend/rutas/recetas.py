# Responsable: Shanda
#
# Por hacer:
#   GET /api/recetas?buscar=pepian  ->  buscar recetas por nombre
#   GET /api/recetas/{id}  ->  una receta con sus ingredientes y pasos
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
