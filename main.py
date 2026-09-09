from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import mysql.connector

app = FastAPI()

# Configuración de CORS para permitir peticiones desde el navegador
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="recetario_db"
    )

@app.get("/api/recetas/buscar")
def buscar_por_ingredientes(ingredientes: List[str] = Query(...)):
    conexion = conectar_db()
    cursor = conexion.cursor(dictionary=True)
    
    condiciones = []
    params = []
    for ing in ingredientes:
        condiciones.append("ingredientes LIKE %s")
        params.append(f"%{ing}%")
    
    query = "SELECT * FROM recetas WHERE " + " AND ".join(condiciones) + " LIMIT 20"
    
    cursor.execute(query, tuple(params))
    resultados = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    return resultados