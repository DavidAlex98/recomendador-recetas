# Responsable: Brandon
#
# Por hacer:
#   Crear, editar y borrar recetas
#   Aprobar o rechazar recetas propuestas
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Datos que manda el usuario al proponer una receta
class Propuesta(BaseModel):
    nombre: str
    descripcion: str = ""


# Datos que manda el admin al rechazar una propuesta
class Rechazo(BaseModel):
    motivo: str


# POST /api/propuestas/{usuario_id}
# Un usuario propone una receta nueva. Queda guardada como pendiente.
@router.post("/propuestas/{usuario_id}")
def proponer_receta(usuario_id: int, datos: Propuesta):

    # Revisar que el usuario exista
    usuario = consultar("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    ejecutar(
        """
        INSERT INTO recetas_propuestas
        (usuario_id, nombre, descripcion, estado)
        VALUES (%s, %s, %s, 'pendiente')
        """,
        (usuario_id, datos.nombre, datos.descripcion),
    )

    return {"mensaje": "Propuesta enviada, queda pendiente de revisión"}


# GET /api/admin/propuestas
# Lista las propuestas que todavía no se revisan.
@router.get("/admin/propuestas")
def listar_propuestas_pendientes():
    return consultar(
        """
        SELECT p.id, p.usuario_id, u.nombre AS usuario, p.nombre, p.descripcion, p.creado_en
        FROM recetas_propuestas p
        JOIN usuarios u ON u.id = p.usuario_id
        WHERE p.estado = 'pendiente'
        ORDER BY p.creado_en
        """
    )


# Busca una propuesta y avisa si no existe o si ya fue revisada
def _buscar_propuesta_pendiente(propuesta_id):
    filas = consultar("SELECT * FROM recetas_propuestas WHERE id = %s", (propuesta_id,))
    if not filas:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")

    propuesta = filas[0]
    if propuesta["estado"] != "pendiente":
        raise HTTPException(status_code=400, detail="La propuesta ya fue revisada")

    return propuesta


# PUT /api/admin/propuestas/{id}/aprobar
@router.put("/admin/propuestas/{propuesta_id}/aprobar")
def aprobar_propuesta(propuesta_id: int):
    _buscar_propuesta_pendiente(propuesta_id)

    ejecutar(
        "UPDATE recetas_propuestas SET estado = 'aprobada' WHERE id = %s",
        (propuesta_id,),
    )

    return {"mensaje": "Propuesta aprobada"}


# PUT /api/admin/propuestas/{id}/rechazar
@router.put("/admin/propuestas/{propuesta_id}/rechazar")
def rechazar_propuesta(propuesta_id: int, datos: Rechazo):
    _buscar_propuesta_pendiente(propuesta_id)

    ejecutar(
        "UPDATE recetas_propuestas SET estado = 'rechazada', motivo_rechazo = %s WHERE id = %s",
        (datos.motivo, propuesta_id),
    )

    return {"mensaje": "Propuesta rechazada"}


# GET /api/admin/reporte
# Recetas por categoría, total de usuarios y propuestas por estado.
@router.get("/admin/reporte")
def reporte():
    recetas_por_categoria = consultar(
        "SELECT categoria, COUNT(*) AS total FROM recetas GROUP BY categoria ORDER BY categoria"
    )

    total_usuarios = consultar("SELECT COUNT(*) AS total FROM usuarios")[0]["total"]

    propuestas_por_estado = consultar(
        "SELECT estado, COUNT(*) AS total FROM recetas_propuestas GROUP BY estado ORDER BY estado"
    )

    return {
        "recetas_por_categoria": recetas_por_categoria,
        "total_usuarios": total_usuarios,
        "propuestas_por_estado": propuestas_por_estado,
    }
