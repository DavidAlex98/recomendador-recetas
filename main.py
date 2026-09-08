from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI()

# Permitir que tu HTML (frontend) se comunique con esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a la base de datos de XAMPP
def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="", # Por defecto en XAMPP está sin contraseña
        database="recetario_db",
        port=3306
    )

# Endpoint 1: Obtener la lista de ingredientes para los checkboxes/select
@app.get("/api/ingredientes")
def api_ingredientes():
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM ingredientes ORDER BY nombre ASC")
    filas = cursor.fetchall()
    conn.close()
    return [f[0] for f in filas]

# Endpoint 2: Buscar recetas según los ingredientes seleccionados
@app.get("/api/buscar")
def api_buscar(ingredientes: str):
    lista_ing = [i.strip() for i in ingredientes.split(",") if i.strip()]
    if not lista_ing:
        return []
    
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    format_strings = ','.join(['%s'] * len(lista_ing))
    
    query = f"""
        SELECT r.nombre, r.instrucciones, GROUP_CONCAT(i.nombre SEPARATOR ', ') as ingredientes
        FROM recetas r
        JOIN receta_ingrediente ri ON r.id_receta = ri.id_receta
        JOIN ingredientes i ON ri.id_ingrediente = i.id_ingrediente
        WHERE r.id_receta IN (
            SELECT id_receta 
            FROM receta_ingrediente ri2
            JOIN ingredientes i2 ON ri2.id_ingrediente = i2.id_ingrediente
            WHERE i2.nombre IN ({format_strings})
        )
        GROUP BY r.id_receta
    """
    cursor.execute(query, lista_ing)
    resultados = cursor.fetchall()
    conn.close()
    return resultados