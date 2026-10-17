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
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Leer los datos de conexión del archivo .env (está en la carpeta principal).
# La ruta se arma desde este archivo, así funciona desde cualquier carpeta.
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
load_dotenv(CARPETA_PROYECTO / ".env")


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        connect_timeout=5,  # si no conecta en 5 segundos, muestra el error
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


# Guarda una acción en la bitácora, por ejemplo: anotar(5, "Inició sesión").
# Si falla, no detiene lo demás: la bitácora es solo un registro.
def anotar(usuario_id, accion):
    try:
        ejecutar("INSERT INTO bitacora (usuario_id, accion) VALUES (%s, %s)", (usuario_id, accion))
    except Exception:
        pass
