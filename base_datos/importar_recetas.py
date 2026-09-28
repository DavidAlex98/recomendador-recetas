# Carga las recetas de datos/recetas.json a la base de datos.
# Responsable: David
#
# Cómo correrlo (desde la carpeta principal del proyecto):
#     python base_datos/importar_recetas.py

import json
import os

import psycopg
from dotenv import load_dotenv

# Leer los datos de conexión del archivo .env
load_dotenv()

conexion = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"),
)
cursor = conexion.cursor()

# Leer el archivo de recetas
with open("datos/recetas.json", encoding="utf-8") as archivo:
    recetas = json.load(archivo)

print("Importando", len(recetas), "recetas... (tarda unos segundos)")

# Borrar lo que había antes, para no repetir recetas
cursor.execute("DELETE FROM pasos")
cursor.execute("DELETE FROM receta_ingredientes")
cursor.execute("DELETE FROM recetas")

for receta in recetas:
    cursor.execute(
        "INSERT INTO recetas (id, nombre, categoria, descripcion, dificultad, tiempo_min, porciones, vegetariano, vegano, sin_gluten) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (receta["id"], receta["nombre"], receta["categoria"], receta["descripcion"], receta["dificultad"],
         receta["tiempo_min"], receta["porciones"], receta["vegetariano"], receta["vegano"], receta["sin_gluten"]),
    )

    for ingrediente in receta["ingredientes"]:
        cursor.execute(
            "INSERT INTO receta_ingredientes (receta_id, clave, cantidad, unidad, opcional) VALUES (%s, %s, %s, %s, %s)",
            (receta["id"], ingrediente["clave"], ingrediente["cantidad"], ingrediente["unidad"], ingrediente["opcional"]),
        )

    numero = 1
    for paso in receta["pasos"]:
        cursor.execute(
            "INSERT INTO pasos (receta_id, numero, instruccion) VALUES (%s, %s, %s)",
            (receta["id"], numero, paso),
        )
        numero = numero + 1

# Guardar los cambios
conexion.commit()
conexion.close()

print("¡Importación completada!")
