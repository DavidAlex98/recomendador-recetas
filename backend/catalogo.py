# Catálogo de ingredientes (archivo JSON).
# Responsable: David
#
# Los ingredientes no están en la base de datos, están en un archivo JSON.
# Este archivo lo lee una vez y lo deja en la lista INGREDIENTES.
# Cada ingrediente es un diccionario, por ejemplo:
#   {"clave": "cebolla", "nombre": "Cebolla", "categoria": "verduras", ...}

import json

with open("../datos/ingredientes-guatemala.json", encoding="utf-8") as archivo:
    datos = json.load(archivo)

INGREDIENTES = datos["ingredientes"]


def existe(clave):
    """Devuelve True si la clave está en el catálogo."""
    for ingrediente in INGREDIENTES:
        if ingrediente["clave"] == clave:
            return True
    return False
