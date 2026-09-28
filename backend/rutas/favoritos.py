# Responsable: Cristian
#
# Por hacer:
#   GET, POST y DELETE /api/favoritos
#   GET /api/historial
#   Lista de compras con estados: generada, comprada, cerrada
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
