# Catálogo de ingredientes (archivo JSON)
# Responsable: David

import json
from pathlib import Path

CARPETA_PROYECTO = Path(__file__).resolve().parent.parent

with open(CARPETA_PROYECTO / "datos" / "ingredientes-guatemala.json", encoding="utf-8") as archivo:
    datos = json.load(archivo)

INGREDIENTES = datos["ingredientes"]


def existe(clave):
    for ingrediente in INGREDIENTES:
        if ingrediente["clave"] == clave:
            return True
    return False


def nombre(clave):
    for ingrediente in INGREDIENTES:
        if ingrediente["clave"] == clave:
            return ingrediente["nombre"]
    return clave


# Lo que toda casa tiene: azúcar, especias y grasas. No se marcan en el checklist.
BASICOS = ["azucar"]
for ingrediente in INGREDIENTES:
    if ingrediente["categoria"] == "especias" or ingrediente["categoria"] == "grasas":
        BASICOS.append(ingrediente["clave"])


# Ingredientes comunes que salen en el checklist
EN_CHECKLIST = [
    # carnes y mariscos
    "pollo_granja", "pechuga_pollo", "alas_pollo", "pierna_pollo", "muslo_pollo",
    "res_lomo", "res_falda", "cerdo_lomo", "cerdo_costilla", "higado_res",
    "chorizo", "longaniza", "salchicha", "camaron", "pescado_blanco", "atun", "sardina",
    "surimi", "pulpo", "concha_negra", "caracol_mar", "camaron_seco", "carne_molida", "jamon", "tocino",
    # huevo y lácteos
    "huevo", "leche", "crema", "queso_fresco", "queso_seco", "mantequilla", "yogur",
    # verduras
    "cebolla", "tomate", "ajo", "papa", "zanahoria", "guisquil", "ejote", "chile_pimiento",
    "repollo", "brocoli", "coliflor", "ayote_tierno", "elote_tierno", "espinaca", "lechuga",
    "pepino", "rabano", "remolacha", "champinon", "platano_maduro", "platano_verde", "yuca",
    "camote", "aguacate", "cilantro", "perejil", "chile_jalapeno", "loroco",
    # granos, maíz y pan
    "arroz", "frijol_negro", "pasta_fideo", "avena", "harina_trigo", "tortilla_maiz", "pan_frances",
    # frutas
    "limon", "naranja", "banano", "mango", "pina", "papaya", "melon", "sandia", "fresa", "manzana",
    "pera", "uva", "mandarina", "arandano", "cereza", "lichi",
    # otros
    "mayonesa", "consome", "cafe_molido", "chocolate_mesa",
]


# Las partes del pollo cuentan como pollo para las recetas
PARTES_POLLO = ["pechuga_pollo", "alas_pollo", "pierna_pollo", "muslo_pollo", "patas_pollo"]


# Las recetas con proteína salen primero en la recomendación
PROTEINAS = ["huevo", "frijol_negro", "frijol_blanco", "frijol_piloy"]
for ingrediente in INGREDIENTES:
    if ingrediente["categoria"] in ["carnes", "embutidos", "mariscos"]:
        PROTEINAS.append(ingrediente["clave"])
