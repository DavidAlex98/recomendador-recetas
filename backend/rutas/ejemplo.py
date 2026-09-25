"""
ARCHIVO DE EJEMPLO: cópialo como modelo para tus propias rutas.
Responsable: David

Aquí hay tres endpoints que muestran los tres casos que vamos a usar:
  1. GET que consulta MySQL             -> /api/estado
  2. GET que lee el catálogo JSON       -> /api/categorias
  3. POST que recibe datos y los valida -> /api/validar-ingredientes

Para probarlos, corre el servidor y abre http://localhost:8000/docs
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar

# Todas las rutas de este archivo empiezan con /api
router = APIRouter(prefix="/api", tags=["Ejemplo"])


# ---------------------------------------------------------------------------
# 1. GET que consulta MySQL
# ---------------------------------------------------------------------------
@router.get("/estado")
def estado_del_sistema():
    """Dice si la base de datos está conectada y cuántas recetas hay."""
    try:
        filas = consultar("SELECT COUNT(*) AS total FROM recetas")
        return {"base_de_datos": "conectada", "total_recetas": filas[0]["total"]}
    except Exception as error:
        # Si MySQL no está encendido o faltan las tablas, avisamos sin romper la app
        return {"base_de_datos": "sin conexión", "detalle": str(error)}


# ---------------------------------------------------------------------------
# 2. GET que lee el catálogo JSON (no necesita MySQL)
# ---------------------------------------------------------------------------
@router.get("/categorias")
def listar_categorias():
    """Devuelve las categorías de ingredientes del catálogo JSON."""
    return catalogo.categorias()


# ---------------------------------------------------------------------------
# 3. POST que recibe datos del frontend y los valida
# ---------------------------------------------------------------------------
# Un "modelo" describe qué datos esperamos recibir. FastAPI revisa solo
# que vengan con el tipo correcto y, si no, responde un error 422.
class ListaDeIngredientes(BaseModel):
    ingredientes: list[str]


@router.post("/validar-ingredientes")
def validar_ingredientes(datos: ListaDeIngredientes):
    """Revisa que todas las claves recibidas existan en el catálogo JSON."""
    invalidas = catalogo.claves_invalidas(datos.ingredientes)
    if invalidas:
        # HTTPException corta la función y devuelve un error claro al frontend
        raise HTTPException(status_code=400, detail=f"Ingredientes que no existen: {', '.join(invalidas)}")
    return {"validos": True, "total": len(datos.ingredientes)}
