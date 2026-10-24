# Pruebas de recetas y recomendación
# Responsable: David
#
# Correr desde la carpeta backend:  python -m pytest

from fastapi.testclient import TestClient

from main import app

cliente = TestClient(app)


def recomendar(ingredientes):
    respuesta = cliente.post("/api/recomendaciones", json={"ingredientes": ingredientes})
    nombres = []
    for receta in respuesta.json():
        nombres.append(receta["nombre"])
    return nombres


def test_base_de_datos_conectada():
    respuesta = cliente.get("/api/estado")
    assert respuesta.json()["base_de_datos"] == "conectada"


def test_buscar_recetas_por_nombre():
    respuesta = cliente.get("/api/recetas", params={"buscar": "pollo"})
    recetas = respuesta.json()
    assert len(recetas) > 0
    for receta in recetas:
        assert "pollo" in receta["nombre"].lower()


def test_ver_una_receta_completa():
    respuesta = cliente.get("/api/recetas/gt-0001")
    receta = respuesta.json()
    assert receta["nombre"] == "Pepián de pollo criollo"
    assert len(receta["ingredientes"]) > 0
    assert len(receta["pasos"]) > 0
    # cada ingrediente trae su nombre bonito
    assert receta["ingredientes"][0]["nombre"] != ""


def test_receta_que_no_existe():
    respuesta = cliente.get("/api/recetas/no-existe")
    assert respuesta.status_code == 404


def test_sale_ceviche_con_lo_necesario():
    nombres = recomendar(["camaron", "tomate", "cebolla", "limon"])
    assert "Ceviche de camarón guatemalteco" in nombres


def test_no_sale_si_falta_algo_importante():
    # Solo camarón: al ceviche le falta limón, tomate y cebolla
    nombres = recomendar(["camaron"])
    assert "Ceviche de camarón guatemalteco" not in nombres


def test_lo_basico_no_hace_falta_marcarlo():
    # Los camarones a la plancha llevan aceite y sal, pero no hace falta marcarlos
    nombres = recomendar(["camaron"])
    assert "Camarones a la plancha" in nombres


def test_primero_las_recetas_con_proteina():
    nombres = recomendar(["brocoli", "zanahoria", "pollo_granja"])
    assert "ollo" in nombres[0]


def test_sin_ingredientes_no_sale_nada():
    assert recomendar([]) == []


def test_checklist_no_muestra_lo_basico():
    categorias = cliente.get("/api/ingredientes").json()
    claves = []
    for categoria in categorias:
        for ingrediente in categorias[categoria]:
            claves.append(ingrediente["clave"])
    assert "sal" not in claves
    assert "aceite" not in claves
    assert "cebolla" in claves


def test_alitas_cuentan_como_pollo():
    con_pollo = recomendar(["pollo_granja", "cebolla", "tomate"])
    con_alitas = recomendar(["alas_pollo", "cebolla", "tomate"])
    assert len(con_alitas) > 0
    assert con_alitas == con_pollo
