# Panel de administración: propuestas, recetas y reportes
# Responsable: Brandon
#
# Las rutas /api/admin reciben ?admin_id= y revisan que sea un administrador.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import anotar, conectar, consultar, ejecutar

router = APIRouter(prefix="/api")

DIFICULTADES = ["fácil", "media", "alta"]


class Propuesta(BaseModel):
    nombre: str
    descripcion: str = ""


class Rechazo(BaseModel):
    motivo: str


class IngredienteReceta(BaseModel):
    clave: str
    cantidad: float | None = None
    unidad: str = ""
    opcional: bool = False


class Receta(BaseModel):
    nombre: str
    categoria: str
    descripcion: str = ""
    dificultad: str = "fácil"
    tiempo_min: int
    porciones: int
    vegetariano: bool = False
    vegano: bool = False
    sin_gluten: bool = False
    ingredientes: list[IngredienteReceta]
    pasos: list[str]


def verificar_admin(admin_id):
    filas = consultar("SELECT rol FROM usuarios WHERE id = %s AND activo = TRUE", (admin_id,))
    if not filas or filas[0]["rol"] != "admin":
        raise HTTPException(status_code=403, detail="Solo un administrador puede hacer esto")


# Propuestas: pendiente -> aprobada o rechazada

@router.post("/propuestas/{usuario_id}")
def proponer_receta(usuario_id: int, datos: Propuesta):

    usuario = consultar("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.nombre.strip() == "":
        raise HTTPException(status_code=400, detail="La receta necesita un nombre")

    ejecutar(
        """
        INSERT INTO recetas_propuestas
        (usuario_id, nombre, descripcion, estado)
        VALUES (%s, %s, %s, 'pendiente')
        """,
        (usuario_id, datos.nombre.strip(), datos.descripcion.strip()),
    )
    anotar(usuario_id, "Propuso la receta " + datos.nombre.strip())

    return {"mensaje": "Propuesta enviada, queda pendiente de revisión"}


@router.get("/propuestas/{usuario_id}")
def mis_propuestas(usuario_id: int):
    return consultar(
        """
        SELECT id, nombre, descripcion, estado, motivo_rechazo, creado_en
        FROM recetas_propuestas
        WHERE usuario_id = %s
        ORDER BY creado_en DESC
        """,
        (usuario_id,),
    )


@router.get("/admin/propuestas")
def listar_propuestas_pendientes(admin_id: int):
    verificar_admin(admin_id)
    return consultar("SELECT * FROM vista_propuestas_pendientes ORDER BY creado_en")


def buscar_propuesta_pendiente(propuesta_id):
    filas = consultar("SELECT * FROM recetas_propuestas WHERE id = %s", (propuesta_id,))
    if not filas:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")

    propuesta = filas[0]
    if propuesta["estado"] != "pendiente":
        raise HTTPException(status_code=400, detail="La propuesta ya fue revisada")

    return propuesta


@router.put("/admin/propuestas/{propuesta_id}/aprobar")
def aprobar_propuesta(propuesta_id: int, admin_id: int):
    verificar_admin(admin_id)
    propuesta = buscar_propuesta_pendiente(propuesta_id)

    # Procedimiento almacenado: cambia el estado y anota en la bitácora
    ejecutar("CALL revisar_propuesta(%s, 'aprobada', NULL, %s)", (propuesta_id, admin_id))

    return {
        "mensaje": "Propuesta aprobada. Complétala para agregarla como receta.",
        "nombre": propuesta["nombre"],
        "descripcion": propuesta["descripcion"],
    }


@router.put("/admin/propuestas/{propuesta_id}/rechazar")
def rechazar_propuesta(propuesta_id: int, datos: Rechazo, admin_id: int):
    verificar_admin(admin_id)
    buscar_propuesta_pendiente(propuesta_id)

    if datos.motivo.strip() == "":
        raise HTTPException(status_code=400, detail="Escribe el motivo del rechazo")

    ejecutar(
        "CALL revisar_propuesta(%s, 'rechazada', %s, %s)",
        (propuesta_id, datos.motivo.strip(), admin_id),
    )

    return {"mensaje": "Propuesta rechazada"}


# Reportes

@router.get("/admin/reporte")
def reporte(admin_id: int):
    verificar_admin(admin_id)

    recetas_por_categoria = consultar(
        "SELECT categoria, COUNT(*) AS total FROM recetas GROUP BY categoria ORDER BY categoria"
    )

    total_usuarios = consultar("SELECT COUNT(*) AS total FROM usuarios")[0]["total"]

    propuestas_por_estado = consultar(
        "SELECT estado, COUNT(*) AS total FROM recetas_propuestas GROUP BY estado ORDER BY estado"
    )

    recetas_populares = consultar(
        """
        SELECT * FROM vista_recetas_populares
        WHERE veces_favorita > 0 OR veces_vista > 0
        ORDER BY veces_favorita DESC, veces_vista DESC
        LIMIT 5
        """
    )

    usuarios = consultar("SELECT * FROM vista_resumen_usuarios ORDER BY id")

    return {
        "recetas_por_categoria": recetas_por_categoria,
        "total_usuarios": total_usuarios,
        "propuestas_por_estado": propuestas_por_estado,
        "recetas_populares": recetas_populares,
        "usuarios": usuarios,
    }


@router.get("/admin/bitacora")
def ver_bitacora(admin_id: int):
    verificar_admin(admin_id)
    return consultar(
        """
        SELECT bitacora.id, bitacora.accion, bitacora.fecha, usuarios.nombre AS usuario
        FROM bitacora
        LEFT JOIN usuarios ON usuarios.id = bitacora.usuario_id
        ORDER BY bitacora.fecha DESC
        LIMIT 50
        """
    )


@router.get("/admin/categorias")
def categorias_de_recetas(admin_id: int):
    verificar_admin(admin_id)
    filas = consultar("SELECT DISTINCT categoria FROM recetas ORDER BY categoria")
    lista = []
    for fila in filas:
        lista.append(fila["categoria"])
    return lista


# Recetas: crear, editar y borrar

def validar_receta(datos):
    if datos.nombre.strip() == "" or datos.categoria.strip() == "":
        raise HTTPException(status_code=400, detail="La receta necesita nombre y categoría")

    if datos.dificultad not in DIFICULTADES:
        raise HTTPException(status_code=400, detail="La dificultad debe ser fácil, media o alta")

    if datos.tiempo_min <= 0 or datos.porciones <= 0:
        raise HTTPException(status_code=400, detail="El tiempo y las porciones deben ser mayores que 0")

    if len(datos.ingredientes) == 0:
        raise HTTPException(status_code=400, detail="La receta necesita al menos un ingrediente")

    for ingrediente in datos.ingredientes:
        if not catalogo.existe(ingrediente.clave):
            raise HTTPException(status_code=400, detail="Ingrediente no válido: " + ingrediente.clave)

    pasos = []
    for paso in datos.pasos:
        if paso.strip() != "":
            pasos.append(paso.strip())
    if len(pasos) == 0:
        raise HTTPException(status_code=400, detail="La receta necesita al menos un paso")

    return pasos


# Todo en una sola conexión: si algo falla, no se guarda nada a medias
def guardar_receta(receta_id, datos, pasos, es_nueva):
    conexion = conectar()
    cursor = conexion.cursor()

    valores = (
        datos.nombre.strip(), datos.categoria.strip(), datos.descripcion.strip(), datos.dificultad,
        datos.tiempo_min, datos.porciones, datos.vegetariano, datos.vegano, datos.sin_gluten,
    )

    if es_nueva:
        cursor.execute(
            """
            INSERT INTO recetas (nombre, categoria, descripcion, dificultad, tiempo_min,
                                 porciones, vegetariano, vegano, sin_gluten, id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            valores + (receta_id,),
        )
    else:
        cursor.execute(
            """
            UPDATE recetas
            SET nombre = %s, categoria = %s, descripcion = %s, dificultad = %s, tiempo_min = %s,
                porciones = %s, vegetariano = %s, vegano = %s, sin_gluten = %s
            WHERE id = %s
            """,
            valores + (receta_id,),
        )
        cursor.execute("DELETE FROM receta_ingredientes WHERE receta_id = %s", (receta_id,))
        cursor.execute("DELETE FROM pasos WHERE receta_id = %s", (receta_id,))

    for ingrediente in datos.ingredientes:
        cursor.execute(
            "INSERT INTO receta_ingredientes (receta_id, clave, cantidad, unidad, opcional) VALUES (%s, %s, %s, %s, %s)",
            (receta_id, ingrediente.clave, ingrediente.cantidad, ingrediente.unidad, ingrediente.opcional),
        )

    numero = 1
    for paso in pasos:
        cursor.execute(
            "INSERT INTO pasos (receta_id, numero, instruccion) VALUES (%s, %s, %s)",
            (receta_id, numero, paso),
        )
        numero = numero + 1

    conexion.commit()
    conexion.close()


@router.post("/admin/recetas", status_code=201)
def crear_receta(datos: Receta, admin_id: int):
    verificar_admin(admin_id)
    pasos = validar_receta(datos)

    # Función de la base: siguiente id libre, por ejemplo nu-0001
    receta_id = consultar("SELECT siguiente_id_receta() AS id")[0]["id"]

    guardar_receta(receta_id, datos, pasos, es_nueva=True)
    anotar(admin_id, "Creó la receta " + receta_id)

    return {"mensaje": "Receta creada", "id": receta_id}


@router.put("/admin/recetas/{receta_id}")
def editar_receta(receta_id: str, datos: Receta, admin_id: int):
    verificar_admin(admin_id)

    if not consultar("SELECT id FROM recetas WHERE id = %s", (receta_id,)):
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    pasos = validar_receta(datos)
    guardar_receta(receta_id, datos, pasos, es_nueva=False)
    anotar(admin_id, "Editó la receta " + receta_id)

    return {"mensaje": "Receta actualizada", "id": receta_id}


@router.delete("/admin/recetas/{receta_id}")
def borrar_receta(receta_id: str, admin_id: int):
    verificar_admin(admin_id)

    if not consultar("SELECT id FROM recetas WHERE id = %s", (receta_id,)):
        raise HTTPException(status_code=404, detail="Receta no encontrada")

    # Procedimiento almacenado: borra la receta y lo que depende de ella
    ejecutar("CALL borrar_receta(%s)", (receta_id,))
    anotar(admin_id, "Borró la receta " + receta_id)

    return {"mensaje": "Receta borrada"}
