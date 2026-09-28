# Responsable: Shanda
#
# Por hacer:
#   GET /api/despensa  ->  ingredientes guardados del usuario
#   POST /api/despensa  ->  guardar la despensa
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
