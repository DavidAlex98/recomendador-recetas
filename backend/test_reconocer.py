# Pruebas de reconocer ingredientes en una foto
# Responsable: David
#
# No se conectan a AWS: usan un cliente falso que responde como Rekognition.

import io

from fastapi.testclient import TestClient
from PIL import Image

import catalogo
from main import app
from rutas import reconocer

cliente = TestClient(app)


class RekognitionFalso:
    def detect_labels(self, Image, MaxLabels, MinConfidence):
        return {"Labels": [
            {"Name": "Tomato", "Confidence": 96.4, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Lemon", "Confidence": 91.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Lime", "Confidence": 80.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Vegetable", "Confidence": 99.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Durian", "Confidence": 75.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Table", "Confidence": 88.0, "Categories": [{"Name": "Furniture"}]},
        ]}


def cliente_falso(servicio):
    return RekognitionFalso()


def foto_de_prueba():
    imagen = Image.new("RGB", (50, 50), "red")
    archivo = io.BytesIO()
    imagen.save(archivo, format="JPEG")
    return archivo.getvalue()


def test_todas_las_traducciones_existen_en_el_catalogo():
    for clave in reconocer.TRADUCCION.values():
        assert catalogo.existe(clave), clave


def test_reconoce_ingredientes(monkeypatch):
    monkeypatch.setattr(reconocer.boto3, "client", cliente_falso)
    respuesta = cliente.post("/api/reconocer", files={"foto": ("foto.jpg", foto_de_prueba(), "image/jpeg")})
    datos = respuesta.json()

    claves = []
    for ingrediente in datos["ingredientes"]:
        claves.append(ingrediente["clave"])

    assert respuesta.status_code == 200
    assert claves == ["tomate", "limon"]
    assert datos["ingredientes"][0]["confianza"] == 0.96
    assert datos["no_reconocidos"] == 1


def test_archivo_que_no_es_foto():
    respuesta = cliente.post("/api/reconocer", files={"foto": ("nota.txt", b"hola", "text/plain")})
    assert respuesta.status_code == 400
