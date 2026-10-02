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

# Busca el archivo .env tanto en la carpeta actual como en la carpeta superior
env_path_local = Path(__file__).parent / ".env"
env_path_parent = Path(__file__).parent.parent / ".env"

if env_path_local.exists():
    load_dotenv(dotenv_path=env_path_local, override=True)
elif env_path_parent.exists():
    load_dotenv(dotenv_path=env_path_parent, override=True)
else:
    load_dotenv(override=True)


def conectar():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
        dbname=os.getenv("DB_NAME", "postgres"),
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