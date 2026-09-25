"""
Rutas de Usuarios.
Responsable: Rubí   (Semanas 3 a 6 del cronograma)

Por hacer:
  POST /api/registro  -> crear usuario (contraseña cifrada con hash, NUNCA en texto plano)
  POST /api/login     -> iniciar sesión
  Semana 4: roles (visitante, usuario, administrador) y protección de rutas
  Semana 5: administrar usuarios (activar, desactivar, cambiar rol)
  Semana 6: recuperar contraseña

Cómo empezar: abre rutas/ejemplo.py, copia la forma de un endpoint y pégalo aquí.
Prueba tu endpoint en http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api", tags=["Usuarios"])


# Escribe tus endpoints debajo de esta línea.
