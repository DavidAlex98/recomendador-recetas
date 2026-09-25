"""
Importa el catálogo de recetas (datos/recetas-guatemala.ndjson) a MySQL.
Responsable: David

Qué hace:
  1. Lee las 3,248 recetas del archivo NDJSON (una receta por línea).
  2. Quita las recetas repetidas: mismo plato, mismos ingredientes y mismos pasos.
  3. Revisa que cada ingrediente exista en el catálogo JSON.
  4. Borra las recetas que ya había en MySQL y guarda las nuevas.

Cómo correrlo (desde la carpeta principal del proyecto, con MySQL encendido
y después de correr base_datos/crear_tablas.sql):
    python base_datos/importar_recetas.py

Para solo revisar el archivo sin tocar la base de datos:
    python base_datos/importar_recetas.py --solo-revisar
"""
import json
import sys
from pathlib import Path

# Permite usar db.py y catalogo.py que están en la carpeta backend/
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CARPETA_PROYECTO / "backend"))

import catalogo  # noqa: E402
from db import conectar  # noqa: E402

ARCHIVO_RECETAS = CARPETA_PROYECTO / "datos" / "recetas-guatemala.ndjson"


def leer_recetas():
    with open(ARCHIVO_RECETAS, encoding="utf-8") as archivo:
        return [json.loads(linea) for linea in archivo if linea.strip()]


def quitar_repetidas(recetas):
    """Deja solo la primera receta de cada grupo de recetas idénticas."""
    vistas = set()
    unicas = []
    for receta in recetas:
        ingredientes = sorted(
            (i["clave"], i["cantidad"], i["unidad"], i["opcional"]) for i in receta["ingredientes"]
        )
        pasos = tuple(p["instruccion"] for p in receta["pasos"])
        huella = (receta["receta_base"], tuple(ingredientes), pasos)
        if huella not in vistas:
            vistas.add(huella)
            unicas.append(receta)
    return unicas


def insertar_por_lotes(cursor, sql, filas, tamano=200):
    """
    Inserta las filas en grupos pequeños. MySQL de XAMPP no acepta paquetes
    de más de 1 MB, así que no se puede mandar todo de una sola vez.
    """
    for inicio in range(0, len(filas), tamano):
        cursor.executemany(sql, filas[inicio:inicio + tamano])


def fila_receta(r):
    """Convierte una receta del JSON en los valores de la tabla recetas."""
    return (
        r["id"], r["nombre"], r["nombre_completo"], r["receta_base"], r["categoria"],
        r.get("descripcion"), r["origen"].get("departamento"), r["dificultad"],
        r["tiempos"]["total_min"], r["porciones"], r["picante"]["nivel"],
        r["apto"]["vegetariano"], r["apto"]["vegano"], r["apto"]["sin_gluten"], r["apto"]["sin_lacteos"],
        r["costo_estimado_gtq"]["por_porcion"], r["nutricion_por_porcion"]["calorias_kcal"],
    )


def main():
    solo_revisar = "--solo-revisar" in sys.argv

    recetas = leer_recetas()
    unicas = quitar_repetidas(recetas)
    print(f"Recetas en el archivo: {len(recetas)}")
    print(f"Recetas repetidas quitadas: {len(recetas) - len(unicas)}")
    print(f"Recetas a importar: {len(unicas)}")

    # Enfoque híbrido: todas las claves deben existir en el catálogo JSON
    faltantes = sorted({i["clave"] for r in unicas for i in r["ingredientes"] if not catalogo.existe(i["clave"])})
    if faltantes:
        print("ERROR: estos ingredientes no existen en el catálogo JSON:", ", ".join(faltantes))
        sys.exit(1)
    print("Todos los ingredientes existen en el catálogo JSON.")

    if solo_revisar:
        print("Modo --solo-revisar: no se tocó la base de datos.")
        return

    conexion = conectar()
    cursor = conexion.cursor()
    try:
        # Borrar lo anterior (pasos e ingredientes se borran solos por ON DELETE CASCADE)
        cursor.execute("DELETE FROM recetas")

        insertar_por_lotes(
            cursor,
            """INSERT INTO recetas (id, nombre, nombre_completo, receta_base, categoria, descripcion,
                   departamento, dificultad, tiempo_total_min, porciones, picante_nivel,
                   vegetariano, vegano, sin_gluten, sin_lacteos, costo_porcion_gtq, calorias_porcion)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            [fila_receta(r) for r in unicas],
        )
        insertar_por_lotes(
            cursor,
            """INSERT INTO receta_ingredientes (receta_id, clave, cantidad, unidad, preparacion, opcional)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            [(r["id"], i["clave"], i["cantidad"], i["unidad"], i.get("preparacion"), i["opcional"])
             for r in unicas for i in r["ingredientes"]],
        )
        insertar_por_lotes(
            cursor,
            "INSERT INTO pasos (receta_id, numero, instruccion) VALUES (%s, %s, %s)",
            [(r["id"], p["n"], p["instruccion"]) for r in unicas for p in r["pasos"]],
        )
        conexion.commit()
        print("¡Importación completada!")
    except Exception:
        try:
            conexion.rollback()  # si algo falla, no queda la base a medias
        except Exception:
            pass
        raise
    finally:
        conexion.close()


if __name__ == "__main__":
    main()
