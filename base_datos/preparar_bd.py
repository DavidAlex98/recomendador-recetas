"""
Prepara la base de datos completa con un solo comando.
Responsable: David

Qué hace:
  1. Crea la base de datos 'recetapp' en PostgreSQL (si no existe).
  2. Corre base_datos/crear_tablas.sql (crea las tablas).
  3. Importa las recetas (lo mismo que importar_recetas.py).

Cómo correrlo (desde la carpeta principal del proyecto, con PostgreSQL instalado):
    python base_datos/preparar_bd.py

OJO: borra las tablas y las vuelve a crear. Úsalo al instalar el proyecto o
cuando el equipo de base de datos cambie crear_tablas.sql.
"""
import os
import sys
from pathlib import Path

CARPETA = Path(__file__).resolve().parent
sys.path.insert(0, str(CARPETA.parent / "backend"))
sys.path.insert(0, str(CARPETA))

import psycopg  # noqa: E402
from db import conectar  # noqa: E402


def crear_base_de_datos():
    """Crea la base de datos si todavía no existe."""
    nombre = os.getenv("DB_NAME", "recetapp")
    # Nos conectamos a la base 'postgres', que siempre existe, para crear la nuestra
    conexion = conectar("postgres")
    conexion.autocommit = True  # CREATE DATABASE no se puede hacer dentro de una transacción
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (nombre,))
        if cursor.fetchone() is None:
            cursor.execute(f'CREATE DATABASE "{nombre}"')
            print(f"    Base de datos '{nombre}' creada.")
        else:
            print(f"    La base de datos '{nombre}' ya existía.")
    finally:
        conexion.close()


def crear_tablas():
    """Corre el archivo crear_tablas.sql completo."""
    sql = (CARPETA / "crear_tablas.sql").read_text(encoding="utf-8")
    with conectar() as conexion:
        conexion.cursor().execute(sql)


def main():
    print("1/3 Creando la base de datos...")
    try:
        crear_base_de_datos()
    except psycopg.OperationalError as error:
        print(f"No se pudo conectar a PostgreSQL: {error}")
        print("Revisa que PostgreSQL esté instalado y encendido, y la contraseña en tu archivo .env.")
        sys.exit(1)

    print("2/3 Creando las tablas...")
    crear_tablas()
    print("    Listo.")

    print("3/3 Importando recetas...")
    import importar_recetas
    importar_recetas.main()


if __name__ == "__main__":
    main()
