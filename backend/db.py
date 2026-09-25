"""
Conexión a la base de datos MySQL.
Responsable: David

Todas las rutas usan las funciones de este archivo. Nadie más necesita
escribir código de conexión.

Los datos de conexión (usuario, contraseña...) se leen del archivo .env que
está en la carpeta principal del proyecto. Ese archivo NO se sube a GitHub:
cada quien crea el suyo copiando .env.example.
"""
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

# Carga las variables del archivo .env (está una carpeta arriba de backend/)
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def conectar():
    """Abre una conexión nueva a MySQL."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "recetapp"),
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
    conexion = conectar()
    try:
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, parametros)
        return cursor.fetchall()
    finally:
        conexion.close()


def ejecutar(sql, parametros=()):
    """
    Ejecuta un INSERT, UPDATE o DELETE y guarda los cambios.
    Devuelve el id del último registro insertado (útil después de un INSERT).

    Ejemplo:
        nuevo_id = ejecutar("INSERT INTO favoritos (usuario_id, receta_id) VALUES (%s, %s)",
                            (usuario_id, receta_id))
    """
    conexion = conectar()
    try:
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        conexion.commit()
        return cursor.lastrowid
    finally:
        conexion.close()
