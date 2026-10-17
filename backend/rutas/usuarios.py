# Registro e inicio de sesión
# Responsable: Rubí

import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import anotar, consultar, ejecutar

router = APIRouter(prefix="/api")


class Registro(BaseModel):
    nombre: str
    correo: str
    contrasena: str


class Login(BaseModel):
    correo: str
    contrasena: str


@router.post("/registro")
def registro(datos: Registro):
    nombre = datos.nombre.strip()
    correo = datos.correo.strip()

    if nombre == "" or correo == "" or datos.contrasena.strip() == "":
        raise HTTPException(status_code=400, detail="Todos los campos son obligatorios")

    partes = correo.split("@")
    if (
        len(partes) != 2
        or partes[0] == ""
        or "." not in partes[1]
        or partes[1].startswith(".")
        or partes[1].endswith(".")
    ):
        raise HTTPException(status_code=400, detail="El correo no es válido")

    if consultar("SELECT id FROM usuarios WHERE LOWER(correo) = LOWER(%s)", (correo,)):
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # La contraseña se guarda cifrada con bcrypt
    contrasena_hash = bcrypt.hashpw(datos.contrasena.encode(), bcrypt.gensalt()).decode()

    ejecutar(
        "INSERT INTO usuarios (nombre, correo, contrasena_hash, rol, activo) VALUES (%s, %s, %s, 'usuario', TRUE)",
        (nombre, correo, contrasena_hash),
    )
    anotar(None, "Se registró " + correo)
    return {"mensaje": "Usuario registrado correctamente"}


@router.post("/login")
def login(datos: Login):
    filas = consultar(
        "SELECT id, nombre, rol, contrasena_hash FROM usuarios WHERE LOWER(correo) = LOWER(%s) AND activo = TRUE",
        (datos.correo.strip(),),
    )
    if not filas:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    usuario = filas[0]

    # Las contraseñas viejas (antes de bcrypt) dan error y se toman como incorrectas
    try:
        correcta = bcrypt.checkpw(datos.contrasena.encode(), usuario["contrasena_hash"].encode())
    except ValueError:
        correcta = False

    if not correcta:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    anotar(usuario["id"], "Inició sesión")
    return {"id": usuario["id"], "nombre": usuario["nombre"], "rol": usuario["rol"]}
