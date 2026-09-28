# Responsable: Shanda
#
# Por hacer:
#   GET /api/ingredientes  ->  ingredientes del JSON agrupados por categoría
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
