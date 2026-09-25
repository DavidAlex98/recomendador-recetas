"""
Rutas de Administrador.
Responsable: Brandon   (Semanas 4 a 6 del cronograma)

Por hacer:
  Semana 4: listar y eliminar recetas
  Semana 5: crear y editar recetas (con bitácora de Shanda)
  Semana 6: aprobar o rechazar recetas propuestas: pendiente -> aprobada / rechazada

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Administrador"])


# Escribe tus endpoints debajo de esta línea.
