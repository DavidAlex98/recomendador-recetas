# Responsable: Rubí
#
# Endpoints:
#   POST /api/registro  ->  crear usuario (contraseña cifrada con bcrypt)
#   POST /api/login     ->  iniciar sesión

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt

from db import anotar, consultar, ejecutar

router = APIRouter(prefix="/api")


# Registrar un usuario
class Registro(BaseModel):
    nombre: str
    correo: str
    contrasena: str


# Iniciar sesión
class Login(BaseModel):
    correo: str
    contrasena: str


# POST /api/registro
@router.post("/registro")
def registro(datos: Registro):

    # Validacion que los campos no estén vacíos
    if (
        datos.nombre.strip() == ""
        or datos.correo.strip() == ""
        or datos.contrasena.strip() == ""
    ):
        raise HTTPException(
            status_code=400,
            detail="Todos los campos son obligatorios"
        )

    # Validar el formato  del correo
    correo = datos.correo.strip()

    partes = correo.split("@")
    if (
        len(partes) != 2
        or partes[0] == ""
        or "." not in partes[1]
        or partes[1].startswith(".")
        or partes[1].endswith(".")
    ):
        raise HTTPException(
            status_code=400,
            detail="El correo no es válido"
        )

    # Revisar si el correo ya existe
    existente = consultar(
        """
        SELECT id
        FROM usuarios
        WHERE LOWER(correo) = LOWER(%s)
        """,
        (correo,)
    )

    if existente:
        raise HTTPException(
            status_code=400,
            detail="El correo ya está registrado"
        )

    # Cifrar la contraseña con bcrypt
    contrasena_hash = bcrypt.hashpw(
        datos.contrasena.encode(),
        bcrypt.gensalt()
    ).decode()

    ejecutar(
        """
        INSERT INTO usuarios
        (nombre, correo, contrasena_hash, rol, activo)
        VALUES (%s, %s, %s, 'usuario', TRUE)
        """,
        (
            datos.nombre.strip(),
            correo,
            contrasena_hash
        )
    )

    anotar(None, "Se registró " + correo)

    return {
        "mensaje": "Usuario registrado correctamente"
    }


# POST /api/login
@router.post("/login")
def login(datos: Login):

    # Buscar al usuario por correo y verificar que esté activo
    filas = consultar(
        """
        SELECT id, nombre, rol, contrasena_hash
        FROM usuarios
        WHERE LOWER(correo) = LOWER(%s)
          AND activo = TRUE
        """,
        (datos.correo.strip(),)
    )

    # Si el usuario no existe
    if not filas:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    usuario = filas[0]

    # Comparar la contraseña con bcrypt.
    # Si la contraseña se guardó con el cifrado viejo (SHA-256),
    # bcrypt da error; en ese caso la tomamos como incorrecta.
    try:
        correcta = bcrypt.checkpw(
            datos.contrasena.encode(),
            usuario["contrasena_hash"].encode()
        )
    except ValueError:
        correcta = False

    if not correcta:
        raise HTTPException(
            status_code=401,
            detail="Correo o contraseña incorrectos"
        )

    anotar(usuario["id"], "Inició sesión")

    return {
        "id": usuario["id"],
        "nombre": usuario["nombre"],
        "rol": usuario["rol"]
    }
