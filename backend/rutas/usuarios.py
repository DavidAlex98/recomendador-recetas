# Responsable: Rubí
#
# Por hacer:
#   POST /api/registro  ->  crear usuario (contraseña cifrada)
#   POST /api/login  ->  iniciar sesión
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import hashlib

from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# registrar un usuario
class Registro(BaseModel):
    nombre: str
    correo: str
    contrasena: str


# iniciar sesión
class Login(BaseModel):
    correo: str
    contrasena: str


# POST /api/registro
@router.post("/registro")
def registro(datos: Registro):

    # Revisar si el correo ya existe
    existente = consultar(
        """
        SELECT id
        FROM usuarios
        WHERE correo = %s
        """,
        (datos.correo,)
    )

    if existente:
       raise HTTPException(status_code=400, detail="El correo ya está registrado")
    
    # Cifrar la contraseña
    contrasena_hash = hashlib.sha256(
        datos.contrasena.encode()
    ).hexdigest()

    ejecutar(
        """
        INSERT INTO usuarios
        (nombre, correo, contrasena_hash, rol, activo)
        VALUES (%s, %s, %s, 'usuario', TRUE)
        """,
        (
            datos.nombre,
            datos.correo,
            contrasena_hash
        )
    )

    return {
        "mensaje": "Usuario registrado correctamente"
    }


# POST /api/login
@router.post("/login")
def login(datos: Login):

    # Cifrar la contraseña recibida
    contrasena_hash = hashlib.sha256(
        datos.contrasena.encode()
    ).hexdigest()

    filas = consultar(
        """
        SELECT id, nombre, rol
        FROM usuarios
        WHERE correo = %s
          AND contrasena_hash = %s
          AND activo = TRUE
        """,
        (
            datos.correo,
            contrasena_hash
        )
    )

    if not filas:
       raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    usuario = filas[0]

    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "rol": usuario["rol"]
    }

