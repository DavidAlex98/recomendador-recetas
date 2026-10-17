# Rutas de ingredientes
# Responsable: Shanda
#
#   GET /api/ingredientes  ->  ingredientes del JSON agrupados por categoría
#   (solo los comunes de catalogo.EN_CHECKLIST, para no saturar la página)

from fastapi import APIRouter

import catalogo

router = APIRouter(prefix="/api")


@router.get("/ingredientes")
def listar_ingredientes():
    agrupados = {}
    for ingrediente in catalogo.INGREDIENTES:
        if ingrediente["clave"] not in catalogo.EN_CHECKLIST:
            continue
        categoria = ingrediente["categoria"]
        if categoria not in agrupados:
            agrupados[categoria] = []
        agrupados[categoria].append({"clave": ingrediente["clave"], "nombre": ingrediente["nombre"]})
    return agrupados
