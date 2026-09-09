import pandas as pd
from sqlalchemy import create_engine

# Configura la conexión a tu base de datos local
# Formato: mysql+pymysql://usuario:contraseña@localhost/nombre_base_de_datos
usuario = "root"
password = ""  # Déjalo vacío si XAMPP no te pide contraseña
host = "localhost"
database = "recetario_db"

conexion_str = f"mysql+pymysql://{usuario}:{password}@{host}/{database}"
engine = create_engine(conexion_str)

print("Leyendo el archivo CSV...")
df = pd.read_csv("main.csv")

# Limpiamos posibles columnas vacías o nulas que causan conflictos
df = df.dropna(how="all")
if "Unnamed: 0" in df.columns:
 df = df.drop(columns=["Unnamed: 0"])
if "id" in df.columns:
  # Dejamos que MySQL maneje el ID autoincrementable
  df = df.drop(columns=["id"])

print("Importando datos a la base de datos...")
# 'recetas' es el nombre de tu tabla en MySQL
df.to_sql("recetas", con=engine, if_exists="append", index=False)

print("¡Importación completada con éxito!")