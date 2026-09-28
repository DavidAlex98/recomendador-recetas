# Responsable: David
#
# Por hacer:
#   POST /api/recomendaciones  ->  recetas que se pueden hacer con los ingredientes
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
