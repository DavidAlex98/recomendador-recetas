# Rutas de recetas
# Responsable: David
#
#   GET /api/recetas?buscar=pepian&categoria=Sopas  ->  buscar recetas
#   GET /api/recetas/gt-0001  ->  una receta con sus ingredientes y pasos

from fastapi import APIRouter, HTTPException

from db import consultar

router = APIRouter(prefix="/api")


# Lista de recetas, con búsqueda por nombre y filtro por categoría
@router.get("/recetas")
def listar_recetas(buscar: str = "", categoria: str = ""):
    sql = "SELECT id, nombre, categoria, dificultad, tiempo_min FROM recetas WHERE nombre ILIKE %s"
    datos = ["%" + buscar + "%"]

    if categoria != "":
        sql = sql + " AND categoria = %s"
        datos.append(categoria)

    sql = sql + " ORDER BY nombre LIMIT 50"
    return consultar(sql, datos)


# Una receta completa, con sus ingredientes y pasos
@router.get("/recetas/{receta_id}")
def ver_receta(receta_id: str):
    recetas = consultar("SELECT * FROM recetas WHERE id = %s", (receta_id,))

    if len(recetas) == 0:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    receta = recetas[0]
    receta["ingredientes"] = consultar(
        "SELECT clave, cantidad, unidad, opcional FROM receta_ingredientes WHERE receta_id = %s",
        (receta_id,),
    )
    receta["pasos"] = consultar(
        "SELECT numero, instruccion FROM pasos WHERE receta_id = %s ORDER BY numero",
        (receta_id,),
    )
    return receta
