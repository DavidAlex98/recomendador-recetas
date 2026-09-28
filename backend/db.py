"""
Conexión a la base de datos PostgreSQL.
Responsable: David

Todas las rutas usan las funciones de este archivo. Nadie más necesita
escribir código de conexión.

Los datos de conexión (usuario, contraseña...) se leen del archivo .env que
está en la carpeta principal del proyecto. Ese archivo NO se sube a GitHub:
cada quien crea el suyo copiando .env.example.
"""
import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Carga las variables del archivo .env (está una carpeta arriba de backend/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def conectar(base_de_datos=None):
    """Abre una conexión nueva a PostgreSQL."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        dbname=base_de_datos or os.getenv("DB_NAME", "recetapp"),
    )


def consultar(sql, parametros=()):
    """
    Ejecuta un SELECT y devuelve una lista de diccionarios.

    Ejemplo:
        consultar("SELECT * FROM recetas WHERE id = %s", (id_receta,))

    IMPORTANTE: los valores SIEMPRE van con %s y en 'parametros'.
    Nunca pegues valores dentro del texto del SQL con f"..." o con +,
    porque eso permite inyección SQL.
    """
    with conectar() as conexion:
        cursor = conexion.cursor(row_factory=dict_row)
        cursor.execute(sql, parametros)
        return cursor.fetchall()


def ejecutar(sql, parametros=()):
    """
    Ejecuta un INSERT, UPDATE o DELETE y guarda los cambios.

    Si el SQL termina en "RETURNING id", devuelve ese id (útil después de un INSERT).

    Ejemplo:
        nuevo_id = ejecutar(
            "INSERT INTO favoritos (usuario_id, receta_id) VALUES (%s, %s) RETURNING id",
            (usuario_id, receta_id),
        )
    """
    with conectar() as conexion:  # al salir del "with" se guardan los cambios
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        if cursor.description:  # el SQL devolvió algo (RETURNING)
            return cursor.fetchone()[0]
        return None
