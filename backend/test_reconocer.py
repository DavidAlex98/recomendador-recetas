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
    def __init__(self):
        self.llamadas = 0
        self.filtros = []

    def detect_labels(self, Image, MaxLabels, MinConfidence, Settings=None):
        self.llamadas = self.llamadas + 1
        self.filtros.append(Settings)
        return {"Labels": [
            {"Name": "Tomato", "Confidence": 96.4, "Categories": [{"Name": "Food and Beverage"}],
             "Instances": [{"BoundingBox": {"Left": 0.1, "Top": 0.1, "Width": 0.5, "Height": 0.5}}]},
            {"Name": "Lemon", "Confidence": 91.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Lime", "Confidence": 80.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Vegetable", "Confidence": 99.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Durian", "Confidence": 75.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Seafood Platter", "Confidence": 82.0, "Aliases": [{"Name": "Shrimp"}]},
            {"Name": "Radish", "Confidence": 60.0, "Categories": [{"Name": "Food and Beverage"}]},
            {"Name": "Table", "Confidence": 88.0, "Categories": [{"Name": "Furniture"}]},
        ]}

    def detect_text(self, Image):
        return {"TextDetections": [
            {"Type": "LINE", "DetectedText": "LECHE ENTERA"},
            {"Type": "LINE", "DetectedText": "Salsa de tomate"},
            {"Type": "WORD", "DetectedText": "LECHE"},
        ]}


falso = RekognitionFalso()


def cliente_falso(servicio):
    return falso


def foto(ancho, alto):
    imagen = Image.new("RGB", (ancho, alto), "red")
    archivo = io.BytesIO()
    imagen.save(archivo, format="JPEG")
    return archivo.getvalue()


def mandar(contenido, monkeypatch):
    falso.llamadas = 0
    falso.filtros = []
    monkeypatch.setattr(reconocer.boto3, "client", cliente_falso)
    return cliente.post("/api/reconocer", files={"foto": ("foto.jpg", contenido, "image/jpeg")})


def claves_de(datos):
    claves = []
    for ingrediente in datos["ingredientes"]:
        claves.append(ingrediente["clave"])
    return claves


def test_todas_las_traducciones_existen_en_el_catalogo():
    for clave in reconocer.TRADUCCION.values():
        assert catalogo.existe(clave), clave


def test_reconoce_ingredientes_y_texto(monkeypatch):
    respuesta = mandar(foto(50, 50), monkeypatch)
    datos = respuesta.json()
    claves = claves_de(datos)

    assert respuesta.status_code == 200
    assert "tomate" in claves
    assert "limon" in claves
    # Del texto: "LECHE ENTERA" y "Salsa de tomate"
    assert "leche" in claves
    assert "salsa_tomate" in claves
    # Durian es comida clara (75%) pero no está en el catálogo
    assert datos["no_reconocidos"] == 1
    # Foto pequeña: el cuadro sale muy chico y no se parte en 4
    assert falso.llamadas == 1


def test_usa_los_otros_nombres_de_aws(monkeypatch):
    datos = mandar(foto(50, 50), monkeypatch).json()
    # "Seafood Platter" no está en el diccionario, pero su alias "Shrimp" sí
    assert "camaron" in claves_de(datos)


def test_lo_dudoso_visto_una_vez_no_sale(monkeypatch):
    # Rábano con 60%: en una foto pequeña AWS lo ve una sola vez
    datos = mandar(foto(50, 50), monkeypatch).json()
    assert "rabano" not in claves_de(datos)


def test_lo_dudoso_visto_varias_veces_si_sale(monkeypatch):
    # En una foto grande se pregunta varias veces y el rábano aparece en varios pedazos
    datos = mandar(foto(800, 800), monkeypatch).json()
    assert "rabano" in claves_de(datos)


def test_recorta_y_parte_la_foto_grande(monkeypatch):
    datos = mandar(foto(800, 800), monkeypatch).json()
    claves = claves_de(datos)

    # Completa + 1 recorte + 4 partes (porque hubo menos de 3 recortes)
    assert falso.llamadas == 6
    for clave in claves:
        assert claves.count(clave) == 1


def test_la_completa_sin_filtro_y_los_pedazos_solo_comida(monkeypatch):
    mandar(foto(800, 800), monkeypatch)
    assert falso.filtros[0] is None
    for filtro in falso.filtros[1:]:
        assert filtro["GeneralLabels"]["LabelCategoryInclusionFilters"] == ["Food and Beverage"]


def test_no_recorta_lo_que_ocupa_media_foto(monkeypatch):
    original = RekognitionFalso.detect_labels

    def con_refrigerador(self, Image, MaxLabels, MinConfidence, Settings=None):
        respuesta = original(self, Image, MaxLabels, MinConfidence, Settings)
        respuesta["Labels"].append({"Name": "Refrigerator", "Confidence": 90.0,
                                    "Instances": [{"BoundingBox": {"Left": 0, "Top": 0, "Width": 0.9, "Height": 0.9}}]})
        return respuesta

    monkeypatch.setattr(RekognitionFalso, "detect_labels", con_refrigerador)
    mandar(foto(800, 800), monkeypatch)
    # Igual que sin el refrigerador: completa + 1 recorte + 4 partes
    assert falso.llamadas == 6


def test_lo_mas_seguro_sale_primero(monkeypatch):
    datos = mandar(foto(50, 50), monkeypatch).json()
    assert datos["ingredientes"][0]["clave"] == "tomate"


def test_etiquetas_sin_repetir(monkeypatch):
    datos = mandar(foto(800, 800), monkeypatch).json()
    assert len(datos["etiquetas_aws"]) == len(set(datos["etiquetas_aws"]))


def test_archivo_que_no_es_foto():
    respuesta = cliente.post("/api/reconocer", files={"foto": ("nota.txt", b"hola", "text/plain")})
    assert respuesta.status_code == 400
