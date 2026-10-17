# Responsable: Shanda
#
# Por hacer:
#   GET /api/despensa/{usuario_id}  ->  ingredientes guardados del usuario
#   POST /api/despensa/{usuario_id}  ->  agregar un ingrediente
#   DELETE /api/despensa/{usuario_id}/{clave}  ->  quitar un ingrediente
#
# Guíate con rutas/ejemplo.py y prueba en http://localhost:8000/docs

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import catalogo
from db import consultar, ejecutar

router = APIRouter(prefix="/api")


# Escribe tus endpoints aquí abajo

class IngredienteDespensa(BaseModel):
	clave: str


def verificar_usuario(usuario_id: int):
	usuarios = consultar("SELECT id FROM usuarios WHERE id = %s", (usuario_id,))
	if not usuarios:
		raise HTTPException(status_code=404, detail="Usuario no encontrado")


@router.get("/despensa/{usuario_id}")
def obtener_despensa(usuario_id: int):
	verificar_usuario(usuario_id)
	ingredientes = consultar(
		"SELECT clave FROM despensa WHERE usuario_id = %s ORDER BY clave",
		(usuario_id,),
	)
	for ingrediente in ingredientes:
		ingrediente["nombre"] = catalogo.nombre(ingrediente["clave"])
	return ingredientes


@router.post("/despensa/{usuario_id}", status_code=201)
def agregar_ingrediente(usuario_id: int, datos: IngredienteDespensa):
	verificar_usuario(usuario_id)
	if not catalogo.existe(datos.clave):
		raise HTTPException(status_code=400, detail="Ingrediente no válido")

	existente = consultar(
		"SELECT id FROM despensa WHERE usuario_id = %s AND clave = %s",
		(usuario_id, datos.clave),
	)
	if existente:
		raise HTTPException(status_code=409, detail="El ingrediente ya está en la despensa")

	ejecutar(
		"INSERT INTO despensa (usuario_id, clave) VALUES (%s, %s)",
		(usuario_id, datos.clave),
	)
	return {"clave": datos.clave, "nombre": catalogo.nombre(datos.clave)}


@router.delete("/despensa/{usuario_id}/{clave}")
def quitar_ingrediente(usuario_id: int, clave: str):
	verificar_usuario(usuario_id)
	existente = consultar(
		"SELECT id FROM despensa WHERE usuario_id = %s AND clave = %s",
		(usuario_id, clave),
	)
	if not existente:
		raise HTTPException(status_code=404, detail="Ingrediente no encontrado en la despensa")

	ejecutar(
		"DELETE FROM despensa WHERE usuario_id = %s AND clave = %s",
		(usuario_id, clave),
	)
	return {"clave": clave, "mensaje": "Ingrediente eliminado"}
