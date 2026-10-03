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


# Favoritos

@router.get("/favoritos/{usuario_id}")
def obtener_favoritos(usuario_id: int):
    sql = """
        SELECT recetas.* 
        FROM favoritos
        JOIN recetas ON favoritos.receta_id = recetas.id
        WHERE favoritos.usuario_id = %s
    """
    return consultar(sql, (usuario_id,))


@router.post("/favoritos/{usuario_id}/{receta_id}")
def agregar_favorito(usuario_id: int, receta_id: str):
    # Validar que el usuario exista
    usuario = consultar("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
    if len(usuario) == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar que la receta exista
    receta = consultar("SELECT id FROM recetas WHERE id = %s", (receta_id,))
    if len(receta) == 0:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    # Validar que no esté repetido
    existe = consultar("SELECT id FROM favoritos WHERE usuario_id = %s AND receta_id = %s", (usuario_id, receta_id))
    if len(existe) > 0:
        raise HTTPException(status_code=400, detail="Esa receta ya está en favoritos")

    sql = "INSERT INTO favoritos (usuario_id, receta_id) VALUES (%s, %s)"
    ejecutar(sql, (usuario_id, receta_id))
    return {"mensaje": "Receta agregada a favoritos"}


@router.delete("/favoritos/{usuario_id}/{receta_id}")
def eliminar_favorito(usuario_id: int, receta_id: str):
    sql = "DELETE FROM favoritos WHERE usuario_id = %s AND receta_id = %s"
    ejecutar(sql, (usuario_id, receta_id))
    return {"mensaje": "Receta eliminada de favoritos"}


# Plan semanal

@router.post("/plan/{usuario_id}")
def agregar_al_plan(usuario_id: int, item: ItemPlan):
    # Validar que el usuario exista
    usuario = consultar("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
    if len(usuario) == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Validar que la receta exista
    receta = consultar("SELECT id FROM recetas WHERE id = %s", (item.receta_id,))
    if len(receta) == 0:
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    # Validar día válido
    dias = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    if item.dia.lower() not in dias:
        raise HTTPException(status_code=400, detail="El día debe ser de lunes a domingo")

    sql = """
        INSERT INTO plan_semanal (usuario_id, receta_id, dia, estado)
        VALUES (%s, %s, %s, 'planificado')
    """
    ejecutar(sql, (usuario_id, item.receta_id, item.dia))
    return {"mensaje": "Receta agregada al plan semanal"}


@router.get("/plan/{usuario_id}")
def obtener_plan(usuario_id: int):
    sql = """
        SELECT plan_semanal.id, plan_semanal.dia, plan_semanal.estado, recetas.id as receta_id, recetas.nombre
        FROM plan_semanal
        JOIN recetas ON plan_semanal.receta_id = recetas.id
        WHERE plan_semanal.usuario_id = %s
    """
    return consultar(sql, (usuario_id,))


@router.put("/plan/{id}/estado")
def actualizar_estado_plan(id: int, datos: EstadoPlan):
    nuevo_estado = datos.estado.lower()
    if nuevo_estado not in ["cocinado", "omitido"]:
        raise HTTPException(status_code=400, detail="El estado debe ser 'cocinado' u 'omitido'")

    plan = consultar("SELECT estado FROM plan_semanal WHERE id = %s", (id,))
    if not plan:
        raise HTTPException(status_code=404, detail="Registro del plan no encontrado")

    if plan[0]["estado"] != "planificado":
        raise HTTPException(status_code=400, detail="Solo se pueden modificar items en estado 'planificado'")

    sql = "UPDATE plan_semanal SET estado = %s WHERE id = %s"
    ejecutar(sql, (nuevo_estado, id))
    return {"mensaje": "Estado actualizado a " + nuevo_estado}