# Catálogo de ingredientes (archivo JSON).
# Responsable: David
#
# Los ingredientes no están en la base de datos, están en un archivo JSON.
# Este archivo lo lee una vez y lo deja en la lista INGREDIENTES.
# Cada ingrediente es un diccionario, por ejemplo:
#   {"clave": "cebolla", "nombre": "Cebolla", "categoria": "verduras", ...}

import json

with open("../datos/ingredientes-guatemala.json", encoding="utf-8") as archivo:
    datos = json.load(archivo)

INGREDIENTES = datos["ingredientes"]


def existe(clave):
    """Devuelve True si la clave está en el catálogo."""
    for ingrediente in INGREDIENTES:
        if ingrediente["clave"] == clave:
            return True
    return False


def nombre(clave):
    """Devuelve el nombre bonito de un ingrediente, por ejemplo 'Frijol negro'."""
    for ingrediente in INGREDIENTES:
        if ingrediente["clave"] == clave:
            return ingrediente["nombre"]
    return clave


# Lo que se da por hecho que hay en toda casa: el azúcar, las especias
# (sal, pimienta, orégano... van "al gusto") y las grasas (aceite, manteca).
# Estos no salen en el checklist y nunca hacen que una receta se quede fuera.
BASICOS = ["azucar"]
for ingrediente in INGREDIENTES:
    if ingrediente["categoria"] == "especias" or ingrediente["categoria"] == "grasas":
        BASICOS.append(ingrediente["clave"])


# Los ingredientes que salen en el checklist: solo lo que suele haber en una casa.
# El catálogo tiene más (para las recetas), pero esos no se muestran para no saturar.
EN_CHECKLIST = [
    # carnes y mariscos
    "pollo_granja", "res_lomo", "res_falda", "cerdo_lomo", "cerdo_costilla", "higado_res",
    "chorizo", "longaniza", "salchicha", "camaron", "pescado_blanco", "atun", "sardina",
    "surimi", "pulpo", "concha_negra", "caracol_mar", "camaron_seco",
    # huevo y lácteos
    "huevo", "leche", "crema", "queso_fresco", "queso_seco", "mantequilla",
    # verduras
    "cebolla", "tomate", "ajo", "papa", "zanahoria", "guisquil", "ejote", "chile_pimiento",
    "repollo", "brocoli", "coliflor", "ayote_tierno", "elote_tierno", "espinaca", "lechuga",
    "pepino", "rabano", "remolacha", "champinon", "platano_maduro", "platano_verde", "yuca",
    "camote", "aguacate", "cilantro", "perejil", "chile_jalapeno", "loroco",
    # granos, maíz y pan
    "arroz", "frijol_negro", "pasta_fideo", "avena", "harina_trigo", "tortilla_maiz", "pan_frances",
    # frutas
    "limon", "naranja", "banano", "mango", "pina", "papaya", "melon", "sandia", "fresa", "manzana",
    # otros
    "mayonesa", "consome", "cafe_molido", "chocolate_mesa",
]


# Proteínas: las recetas que llevan alguna de estas salen primero.
PROTEINAS = ["huevo", "frijol_negro", "frijol_blanco", "frijol_piloy"]
for ingrediente in INGREDIENTES:
    if ingrediente["categoria"] in ["carnes", "embutidos", "mariscos"]:
        PROTEINAS.append(ingrediente["clave"])
