# Ingredientes del catálogo
# Responsable: Shanda
#
# Sin parámetros da solo los comunes; con ?todos=true da el catálogo completo.

from fastapi import APIRouter

import catalogo

router = APIRouter(prefix="/api")


@router.get("/ingredientes")
def listar_ingredientes(todos: bool = False):
    agrupados = {}
    for ingrediente in catalogo.INGREDIENTES:
        if not todos and ingrediente["clave"] not in catalogo.EN_CHECKLIST:
            continue
        categoria = ingrediente["categoria"]
        if categoria not in agrupados:
            agrupados[categoria] = []
        agrupados[categoria].append({"clave": ingrediente["clave"], "nombre": ingrediente["nombre"]})
    return agrupados
