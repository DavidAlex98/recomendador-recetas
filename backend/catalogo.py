"""
Catálogo de ingredientes (archivo JSON).
Responsable: David

Enfoque híbrido del proyecto:
  - Los ingredientes y sus categorías viven en datos/ingredientes-guatemala.json
  - PostgreSQL guarda solo datos que cambian: usuarios, recetas, despensas, favoritos...
  - En PostgreSQL, un ingrediente se guarda por su CLAVE del JSON (por ejemplo "cebolla").

Este archivo carga el JSON una sola vez, al arrancar el servidor, y ofrece
funciones para buscar y validar ingredientes.
"""
import json
from pathlib import Path

RUTA_JSON = Path(__file__).resolve().parent.parent / "datos" / "ingredientes-guatemala.json"

with open(RUTA_JSON, encoding="utf-8") as archivo:
    _datos = json.load(archivo)

# Diccionario: clave -> datos del ingrediente
# Ejemplo: INGREDIENTES["cebolla"]["nombre"] == "Cebolla"
INGREDIENTES = {ing["clave"]: ing for ing in _datos["ingredientes"]}


def existe(clave):
    """True si la clave existe en el catálogo."""
    return clave in INGREDIENTES


def obtener(clave):
    """Devuelve los datos de un ingrediente, o None si no existe."""
    return INGREDIENTES.get(clave)


def claves_invalidas(claves):
    """De una lista de claves, devuelve las que NO existen en el catálogo."""
    return [clave for clave in claves if clave not in INGREDIENTES]


def categorias():
    """Lista de categorías de ingredientes, en orden alfabético."""
    return sorted({ing["categoria"] for ing in INGREDIENTES.values()})
