"""
Prepara la base de datos completa con un solo comando.
Responsable: David

Qué hace:
  1. Corre base_datos/crear_tablas.sql (crea la base 'recetapp' y sus tablas).
  2. Importa las recetas (lo mismo que importar_recetas.py).

Cómo correrlo (desde la carpeta principal del proyecto, con MySQL encendido):
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

import mysql.connector  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv(CARPETA.parent / ".env")


def correr_sql(ruta):
    """Ejecuta un archivo .sql instrucción por instrucción."""
    texto = ruta.read_text(encoding="utf-8")
    # Quitar comentarios de línea (--) para poder separar por ';'
    lineas = [l for l in texto.splitlines() if not l.strip().startswith("--")]
    instrucciones = [i.strip() for i in "\n".join(lineas).split(";") if i.strip()]

    # Se conecta sin elegir base de datos, porque el script la crea
    conexion = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
    )
    try:
        cursor = conexion.cursor()
        for instruccion in instrucciones:
            cursor.execute(instruccion)
        conexion.commit()
    finally:
        conexion.close()


def main():
    print("1/2 Creando la base de datos y las tablas...")
    try:
        correr_sql(CARPETA / "crear_tablas.sql")
    except mysql.connector.Error as error:
        print(f"No se pudo conectar o crear las tablas: {error}")
        print("Revisa que MySQL esté encendido (XAMPP: Start en MySQL) y los datos de tu archivo .env.")
        sys.exit(1)
    print("    Listo.")

    print("2/2 Importando recetas...")
    import importar_recetas
    importar_recetas.main()


if __name__ == "__main__":
    main()
