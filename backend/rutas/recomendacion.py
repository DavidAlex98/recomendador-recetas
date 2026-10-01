# Recomendación de recetas
# Responsable: David
#
#   POST /api/recomendaciones  ->  recetas que se pueden hacer con lo que tienes
#
# Regla: si te falta un ingrediente importante, esa receta NO sale.
# Los ingredientes opcionales no cuentan, y lo básico (azúcar, especias y
# grasas, ver catalogo.py) se da por hecho que siempre lo hay en casa.

from fastapi import APIRouter
from pydantic import BaseModel

import catalogo
from db import consultar

router = APIRouter(prefix="/api")


class Despensa(BaseModel):
    ingredientes: list[str]


@router.post("/recomendaciones")
def recomendar(despensa: Despensa):
    marcados = despensa.ingredientes
    tengo = marcados + catalogo.BASICOS

    recetas = consultar("SELECT id, nombre, categoria, dificultad, tiempo_min FROM recetas ORDER BY nombre")
    filas = consultar("SELECT receta_id, clave, opcional FROM receta_ingredientes")

    # Juntar los ingredientes de cada receta: {"gt-0001": [fila, fila, ...]}
    ingredientes_de = {}
    for fila in filas:
        if fila["receta_id"] not in ingredientes_de:
            ingredientes_de[fila["receta_id"]] = []
        ingredientes_de[fila["receta_id"]].append(fila)

    resultado = []
    for receta in recetas:
        receta["usados"] = 0   # cuántos de tus ingredientes usa
        tiene_proteina = False
        usa_algo_mio = False   # que lo principal sea algo de lo que marcaste
        le_falta_algo = False  # que no le falte nada importante

        for ingrediente in ingredientes_de[receta["id"]]:
            if ingrediente["clave"] in marcados:
                receta["usados"] = receta["usados"] + 1
                if ingrediente["opcional"] == False:
                    usa_algo_mio = True
            if ingrediente["opcional"] == False and ingrediente["clave"] in catalogo.PROTEINAS:
                tiene_proteina = True
            if ingrediente["opcional"] == False and ingrediente["clave"] not in tengo:
                le_falta_algo = True

        if usa_algo_mio and not le_falta_algo:
            # Puntos para ordenar: primero las que llevan proteína,
            # y después las que usan más de lo que tienes
            receta["puntos"] = receta["usados"]
            if tiene_proteina:
                receta["puntos"] = receta["puntos"] + 10
            resultado.append(receta)

    resultado.sort(key=sacar_puntos, reverse=True)
    return resultado


def sacar_puntos(receta):
    return receta["puntos"]
