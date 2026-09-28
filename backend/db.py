# Conexión a la base de datos PostgreSQL.
# Responsable: David
#
# Todos usan estas dos funciones:
#   consultar(...)  para SELECT  -> devuelve una lista de filas
#   ejecutar(...)   para INSERT, UPDATE y DELETE -> guarda los cambios
#
# IMPORTANTE: los valores siempre van con %s, nunca pegados en el texto del SQL.
# Ejemplo:  consultar("SELECT * FROM recetas WHERE id = %s", ("gt-0001",))

import os

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Leer los datos de conexión del archivo .env (está en la carpeta principal)
load_dotenv("../.env")


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        row_factory=dict_row,  # para que cada fila sea un diccionario
    )


def consultar(sql, datos=()):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    filas = cursor.fetchall()
    conexion.close()
    return filas


def ejecutar(sql, datos=()):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()
    conexion.close()
