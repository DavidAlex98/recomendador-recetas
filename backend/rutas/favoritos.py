# Responsable: Cristian
#
# Endpoints:
#   - GET, POST, DELETE /api/favoritos
#   - POST, GET, PUT /api/plan

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Esquemas Pydantic
class ItemPlan(BaseModel):
    receta_id: str
    dia: str  # Ej: 'lunes', 'martes', etc.


class EstadoPlan(BaseModel):
    estado: str  # 'cocinado' u 'omitido'


# ==================== FAVORITOS ====================

@router.get("/favoritos/{usuario_id}")
def obtener_favoritos(usuario_id: int):
    sql = """
        SELECT r.* 
        FROM favoritos f
        JOIN recetas r ON f.receta_id = r.id
        WHERE f.usuario_id = %s
    """
    return consultar(sql, (usuario_id,))


@router.post("/favoritos/{usuario_id}/{receta_id}")
def agregar_favorito(usuario_id: int, receta_id: str):
    sql = "INSERT INTO favoritos (usuario_id, receta_id) VALUES (%s, %s)"
    try:
        ejecutar(sql, (usuario_id, receta_id))
        return {"mensaje": "Receta agregada a favoritos"}
    except Exception as e:
        # Muestra el detalle del error de PostgreSQL para depuración
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/favoritos/{usuario_id}/{receta_id}")
def eliminar_favorito(usuario_id: int, receta_id: str):
    sql = "DELETE FROM favoritos WHERE usuario_id = %s AND receta_id = %s"
    ejecutar(sql, (usuario_id, receta_id))
    return {"mensaje": "Receta eliminada de favoritos"}


# ==================== PLAN SEMANAL ====================

@router.post("/plan/{usuario_id}")
def agregar_al_plan(usuario_id: int, item: ItemPlan):
    sql = """
        INSERT INTO plan_semanal (usuario_id, receta_id, dia, estado)
        VALUES (%s, %s, %s, 'planificado')
    """
    try:
        ejecutar(sql, (usuario_id, item.receta_id, item.dia))
        return {"mensaje": "Receta agregada al plan semanal"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/plan/{usuario_id}")
def obtener_plan(usuario_id: int):
    sql = """
        SELECT p.id, p.dia, p.estado, r.id as receta_id, r.nombre
        FROM plan_semanal p
        JOIN recetas r ON p.receta_id = r.id
        WHERE p.usuario_id = %s
    """
    return consultar(sql, (usuario_id,))


@router.put("/plan/{id}/estado")
def actualizar_estado_plan(id: int, datos: EstadoPlan):
    nuevo_estado = datos.estado.lower()
    if nuevo_estado not in ["cocinado", "omitido"]:
        raise HTTPException(
            status_code=400, detail="El estado debe ser 'cocinado' u 'omitido'"
        )

    plan = consultar("SELECT estado FROM plan_semanal WHERE id = %s", (id,))
    if not plan:
        raise HTTPException(
            status_code=404, detail="Registro del plan no encontrado"
        )

    if plan[0]["estado"] != "planificado":
        raise HTTPException(
            status_code=400,
            detail="Solo se pueden modificar items en estado 'planificado'",
        )

    sql = "UPDATE plan_semanal SET estado = %s WHERE id = %s"
    ejecutar(sql, (nuevo_estado, id))
    return {"mensaje": f"Estado actualizado a {nuevo_estado}"}