# Carga las recetas de datos/recetas.json a la base de datos.
# Responsable: David
#
# Cómo correrlo (desde la carpeta principal del proyecto):
#     python base_datos/importar_recetas.py
#
# Se puede correr varias veces: actualiza las recetas que ya existen
# y NO borra los favoritos, el plan ni el historial de los usuarios.

import json
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# La carpeta principal del proyecto, armada desde este archivo
# (así funciona sin importar desde qué carpeta se corra)
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent

# Leer los datos de conexión del archivo .env
load_dotenv(CARPETA_PROYECTO / ".env")

conexion = psycopg.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dbname=os.getenv("DB_NAME"),
    connect_timeout=5,  # si no conecta en 5 segundos, muestra el error
)
cursor = conexion.cursor()

# Leer el archivo de recetas
with open(CARPETA_PROYECTO / "datos" / "recetas.json", encoding="utf-8") as archivo:
    recetas = json.load(archivo)

print("Importando", len(recetas), "recetas... (tarda unos segundos)")

for receta in recetas:
    # Si la receta ya existe, se actualizan sus datos (ON CONFLICT)
    cursor.execute(
        "INSERT INTO recetas (id, nombre, categoria, descripcion, dificultad, tiempo_min, porciones, vegetariano, vegano, sin_gluten) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
        "ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre, categoria = EXCLUDED.categoria, "
        "descripcion = EXCLUDED.descripcion, dificultad = EXCLUDED.dificultad, tiempo_min = EXCLUDED.tiempo_min, "
        "porciones = EXCLUDED.porciones, vegetariano = EXCLUDED.vegetariano, vegano = EXCLUDED.vegano, "
        "sin_gluten = EXCLUDED.sin_gluten",
        (receta["id"], receta["nombre"], receta["categoria"], receta["descripcion"], receta["dificultad"],
         receta["tiempo_min"], receta["porciones"], receta["vegetariano"], receta["vegano"], receta["sin_gluten"]),
    )

    # Los ingredientes y pasos se borran y se vuelven a poner
    cursor.execute("DELETE FROM receta_ingredientes WHERE receta_id = %s", (receta["id"],))
    cursor.execute("DELETE FROM pasos WHERE receta_id = %s", (receta["id"],))

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
