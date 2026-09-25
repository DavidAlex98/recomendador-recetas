"""
Rutas de Despensa.
Responsable: Shanda   (Semana 4 del cronograma)

Por hacer:
  GET  /api/despensa -> ingredientes guardados del usuario
  POST /api/despensa -> guardar la despensa (validar claves con catalogo.claves_invalidas)

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Despensa"])


# Escribe tus endpoints debajo de esta línea.
