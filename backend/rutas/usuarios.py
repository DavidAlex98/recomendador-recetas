# Responsable: Rubí
#
# Por hacer:
#   POST /api/registro  ->  crear usuario (contraseña cifrada)
#   POST /api/login  ->  iniciar sesión
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo
