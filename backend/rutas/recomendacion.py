# Recomendación de recetas
# Responsable: David
#
# Una receta sale solo si tienes todo lo importante. Los opcionales y lo
# básico (catalogo.BASICOS) no cuentan. Primero salen las que llevan proteína.

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

    # Ingredientes de cada receta: {"gt-0001": [fila, fila, ...]}
    ingredientes_de = {}
    for fila in filas:
        if fila["receta_id"] not in ingredientes_de:
            ingredientes_de[fila["receta_id"]] = []
        ingredientes_de[fila["receta_id"]].append(fila)

    resultado = []
    for receta in recetas:
        receta["usados"] = 0
        tiene_proteina = False
        usa_algo_mio = False
        le_falta_algo = False

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
            # 1 punto por ingrediente tuyo y 10 más si lleva proteína
            receta["puntos"] = receta["usados"]
            if tiene_proteina:
                receta["puntos"] = receta["puntos"] + 10
            resultado.append(receta)

    resultado.sort(key=sacar_puntos, reverse=True)
    return resultado


def sacar_puntos(receta):
    return receta["puntos"]
