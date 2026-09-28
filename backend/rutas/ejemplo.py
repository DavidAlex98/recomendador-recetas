# EJEMPLO: copia estos endpoints como modelo para los tuyos.
# Responsable: David
#
# Pruébalos en http://localhost:8000/docs

from fastapi import APIRouter
from pydantic import BaseModel

import catalogo
from db import consultar

router = APIRouter(prefix="/api")


# 1. GET que consulta la base de datos
@router.get("/estado")
def estado():
    try:
        filas = consultar("SELECT COUNT(*) AS total FROM recetas")
        return {"base_de_datos": "conectada", "total_recetas": filas[0]["total"]}
    except Exception as error:
        return {"base_de_datos": "sin conexión", "detalle": str(error)}


# 2. GET que lee el archivo JSON de ingredientes
@router.get("/categorias")
def categorias():
    lista = []
    for ingrediente in catalogo.INGREDIENTES:
        if ingrediente["categoria"] not in lista:
            lista.append(ingrediente["categoria"])
    lista.sort()
    return lista


# 3. POST que recibe datos
# La clase dice qué datos esperamos recibir
class Ingredientes(BaseModel):
    ingredientes: list[str]


@router.post("/validar-ingredientes")
def validar_ingredientes(datos: Ingredientes):
    no_existen = []
    for clave in datos.ingredientes:
        if not catalogo.existe(clave):
            no_existen.append(clave)
    return {"no_existen": no_existen}
