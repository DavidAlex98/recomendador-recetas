# Responsable: Brandon
#
# Por hacer:
#   Crear, editar y borrar recetas
#   Aprobar o rechazar recetas propuestas
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
