# Conexión a PostgreSQL
# Responsable: David
#
# consultar() para SELECT y ejecutar() para INSERT, UPDATE y DELETE.
# Los valores siempre van con %s, nunca pegados en el SQL.

import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

# Datos de conexión del archivo .env
CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
load_dotenv(CARPETA_PROYECTO / ".env")


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME"),
        connect_timeout=5,
        row_factory=dict_row,
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


# Guarda una acción en la bitácora. Si falla, no detiene lo demás.
def anotar(usuario_id, accion):
    try:
        ejecutar("INSERT INTO bitacora (usuario_id, accion) VALUES (%s, %s)", (usuario_id, accion))
    except Exception:
        pass
