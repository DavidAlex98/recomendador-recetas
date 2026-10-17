# Historial de recetas vistas
# Responsable: David
#
#   POST /api/historial/{usuario_id}/{receta_id}  ->  anotar que el usuario vio una receta
#   GET  /api/historial/{usuario_id}              ->  las últimas recetas que vio

from fastapi import APIRouter, HTTPException

from db import consultar, ejecutar

router = APIRouter(prefix="/api")


@router.post("/historial/{usuario_id}/{receta_id}")
def anotar_vista(usuario_id: int, receta_id: str):
    if not consultar("SELECT id FROM usuarios WHERE id = %s", (usuario_id,)):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not consultar("SELECT id FROM recetas WHERE id = %s", (receta_id,)):
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    ejecutar("INSERT INTO historial (usuario_id, receta_id) VALUES (%s, %s)", (usuario_id, receta_id))
    return {"mensaje": "Vista anotada"}


@router.get("/historial/{usuario_id}")
def ver_historial(usuario_id: int):
    # Cada receta una sola vez, con la fecha de la última vez que se vio
    return consultar(
        """
        SELECT recetas.id, recetas.nombre, recetas.categoria, MAX(historial.visto_en) AS visto_en
        FROM historial
        JOIN recetas ON recetas.id = historial.receta_id
        WHERE historial.usuario_id = %s
        GROUP BY recetas.id, recetas.nombre, recetas.categoria
        ORDER BY visto_en DESC
        LIMIT 10
        """,
        (usuario_id,),
    )
