# Pruebas de seguridad del admin y del historial
# Responsable: Brandon
#
# Cómo correrlas (desde la carpeta backend, con PostgreSQL encendido):
#     python -m pytest
#
# Estas pruebas no guardan nada en la base: solo revisan que se rechace
# lo que no se debe permitir.

from fastapi.testclient import TestClient

from main import app

cliente = TestClient(app)

NO_ADMIN = {"admin_id": 999999}   # un id que no existe, así que no es admin


def test_reporte_solo_para_admin():
    respuesta = cliente.get("/api/admin/reporte", params=NO_ADMIN)
    assert respuesta.status_code == 403


def test_no_admin_no_puede_borrar_recetas():
    respuesta = cliente.delete("/api/admin/recetas/gt-0001", params=NO_ADMIN)
    assert respuesta.status_code == 403
    # y la receta sigue ahí
    assert cliente.get("/api/recetas/gt-0001").status_code == 200


def test_admin_sin_admin_id_da_error():
    respuesta = cliente.get("/api/admin/propuestas")
    assert respuesta.status_code == 422


def test_historial_de_usuario_que_no_existe():
    respuesta = cliente.post("/api/historial/999999/gt-0001")
    assert respuesta.status_code == 404


def test_catalogo_completo_tiene_mas_que_el_checklist():
    comunes = cliente.get("/api/ingredientes").json()
    todos = cliente.get("/api/ingredientes", params={"todos": True}).json()
    contar = lambda grupos: sum(len(lista) for lista in grupos.values())
    assert contar(todos) > contar(comunes)
