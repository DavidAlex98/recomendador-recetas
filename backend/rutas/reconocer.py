# Reconocer ingredientes en una foto con AWS Rekognition
# Responsable: David
#
# A una sola foto se le hacen varias preguntas a AWS y se junta lo que encuentre:
#   1. La foto completa: AWS marca con un cuadro los platos, tazones, cajas y frutas
#   2. Cada cuadro se recorta, se agranda y se pregunta solo por la comida (máximo 10)
#   3. Si casi no hubo cuadros, la foto se parte en 4
#   4. El texto de los empaques ("LECHE", "MAYONESA")
# Un ingrediente se acepta si AWS está muy seguro (70% o más), o si lo vio en 2 pedazos o más
# con más de 55%. Lo que sale una sola vez con poca seguridad casi siempre es un error.
# Son entre 2 y 12 llamadas por foto, cerca de 1 centavo de dólar.
#
# Las llaves de AWS van en el .env (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY y AWS_DEFAULT_REGION).
# boto3 las lee solo. Nunca escribirlas en el código.

import io

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

import catalogo

router = APIRouter(prefix="/api")

# Rekognition responde en inglés. Aquí se pasa cada nombre a la clave del catálogo.
TRADUCCION = {
    # carnes
    "Chicken": "pollo_granja",
    "Fried Chicken": "pollo_granja",
    "Roast Chicken": "pollo_granja",
    "Poultry": "pollo_granja",
    "Chicken Wing": "alas_pollo",
    "Drumstick": "pierna_pollo",
    "Beef": "res_lomo",
    "Steak": "res_lomo",
    "Ground Beef": "carne_molida",
    "Pork": "cerdo_lomo",
    "Lamb": "cordero",
    "Mutton": "cordero",
    "Turkey": "chompipe",
    # embutidos
    "Ribs": "cerdo_costilla",
    "Bacon": "tocino",
    "Ham": "jamon",
    "Sausage": "salchicha",
    "Hot Dog": "salchicha",
    "Salami": "salami",
    "Pepperoni": "salami",
    # pescados y mariscos
    "Fish": "pescado_blanco",
    "Salmon": "salmon",
    "Tilapia": "tilapia",
    "Tuna": "atun",
    "Sardine": "sardina",
    "Shrimp": "camaron",
    "Prawn": "camaron",
    "Octopus": "pulpo",
    "Squid": "calamar",
    "Calamari": "calamar",
    "Crab": "cangrejo",
    "Lobster": "langosta",
    "Clam": "almeja",
    "Mussel": "mejillon",
    "Oyster": "ostion",
    # huevo y lácteos
    "Egg": "huevo",
    "Milk": "leche",
    "Cheese": "queso_fresco",
    "Mozzarella": "queso_mozzarella",
    "Butter": "mantequilla",
    "Cream": "crema",
    "Yogurt": "yogur",
    # verduras
    "Tomato": "tomate",
    "Cherry Tomato": "tomate_cherry",
    "Onion": "cebolla",
    "Red Onion": "cebolla_morada",
    "Scallion": "cebollin",
    "Spring Onion": "cebollin",
    "Green Onion": "cebollin",
    "Leek": "poro",
    "Garlic": "ajo",
    "Ginger": "jengibre",
    "Potato": "papa",
    "Sweet Potato": "camote",
    "Yam": "camote",
    "Cassava": "yuca",
    "Taro": "malanga",
    "Carrot": "zanahoria",
    "Turnip": "nabo",
    "Radish": "rabano",
    "Beet": "remolacha",
    "Broccoli": "brocoli",
    "Cauliflower": "coliflor",
    "Brussels Sprout": "colecitas_bruselas",
    "Cabbage": "repollo",
    "Red Cabbage": "repollo_morado",
    "Kale": "col_rizada",
    "Lettuce": "lechuga",
    "Arugula": "rucula",
    "Spinach": "espinaca",
    "Celery": "apio",
    "Asparagus": "esparrago",
    "Artichoke": "alcachofa",
    "Eggplant": "berenjena",
    "Cucumber": "pepino",
    "Zucchini": "ayote_tierno",
    "Squash": "ayote_tierno",
    "Pumpkin": "ayote",
    "Chayote": "guisquil",
    "Jicama": "jicama",
    "Bell Pepper": "chile_pimiento",
    "Pepper": "chile_pimiento",
    "Chili Pepper": "chile_verde",
    "Jalapeno": "chile_jalapeno",
    "Habanero": "chile_habanero",
    "Mushroom": "champinon",
    "Corn": "elote_tierno",
    "Sweet Corn": "elote_tierno",
    "Green Bean": "ejote",
    "Pea": "arvejas",
    "Bean Sprout": "brotes_soya",
    "Avocado": "aguacate",
    "Olive": "aceituna",
    # hierbas
    "Cilantro": "cilantro",
    "Parsley": "perejil",
    "Basil": "albahaca",
    "Mint": "hierbabuena",
    "Rosemary": "romero",
    "Thyme": "tomillo",
    "Oregano": "oregano",
    "Bay Leaf": "laurel",
    "Cinnamon": "canela",
    # frutas
    "Lemon": "limon",
    "Lime": "limon",
    "Orange": "naranja",
    "Tangerine": "mandarina",
    "Mandarin": "mandarina",
    "Clementine": "mandarina",
    "Grapefruit": "toronja",
    "Banana": "banano",
    "Plantain": "platano_verde",
    "Apple": "manzana",
    "Pear": "pera",
    "Grape": "uva",
    "Grapes": "uva",
    "Quince": "membrillo",
    "Kiwi": "kiwi",
    "Cherry": "cereza",
    "Plum": "ciruela",
    "Peach": "durazno",
    "Nectarine": "durazno",
    "Mango": "mango",
    "Pineapple": "pina",
    "Papaya": "papaya",
    "Melon": "melon",
    "Cantaloupe": "melon",
    "Honeydew": "melon",
    "Watermelon": "sandia",
    "Strawberry": "fresa",
    "Blueberry": "arandano",
    "Raspberry": "frambuesa",
    "Blackberry": "mora",
    "Pomegranate": "granada",
    "Dragon Fruit": "pitaya",
    "Passion Fruit": "maracuya",
    "Guava": "guayaba",
    "Fig": "higo",
    "Date": "datil",
    "Coconut": "coco",
    "Custard Apple": "anona",
    "Lychee": "lichi",
    # granos, pan y otros
    "Rice": "arroz",
    "Brown Rice": "arroz",
    "Cumin": "comino",
    "Bean": "frijol_negro",
    "Black Bean": "frijol_negro",
    "Kidney Bean": "frijol_rojo",
    "Lentil": "lenteja",
    "Chickpea": "garbanzo",
    "Quinoa": "quinoa",
    "Oatmeal": "avena",
    "Cereal": "cereal_hojuelas",
    "Pasta": "pasta_fideo",
    "Noodle": "pasta_fideo",
    "Spaghetti": "pasta_fideo",
    "Ramen": "sopa_instantanea",
    "Flour": "harina_trigo",
    "Bread": "pan_frances",
    "Tortilla": "tortilla_maiz",
    "Cracker": "galleta_salada",
    "Peanut": "mani",
    "Peanut Butter": "crema_mani",
    "Almond": "almendra",
    "Walnut": "nuez",
    "Cashew": "semilla_maranon",
    "Pistachio": "pistacho",
    "Sesame": "ajonjoli",
    "Raisin": "pasas",
    "Coffee": "cafe_molido",
    "Chocolate": "chocolate_mesa",
    "Cocoa": "cacao",
    "Honey": "miel",
    "Jam": "mermelada",
    "Mayonnaise": "mayonesa",
    "Ketchup": "salsa_tomate",
    "Mustard": "mostaza",
    "Soy Sauce": "salsa_soya",
    "Hot Sauce": "salsa_picante",
    "Vinegar": "vinagre",
    "Olive Oil": "aceite_oliva",
}

# Nombres generales que no son un ingrediente en sí
GENERALES = ["Food", "Produce", "Vegetable", "Fruit", "Plant", "Meal", "Dish", "Ingredient",
             "Citrus Fruit", "Meat", "Seafood", "Dairy", "Herbs", "Bowl", "Plate", "Grocery Store", "Market",
             "Breakfast", "Brunch", "Lunch", "Dinner", "Food Presentation", "Cup", "Cookware", "Pot",
             "Cereal Bowl", "Dessert", "Grain", "Seed", "Snack", "Salad", "Platter", "Kitchen", "Table",
             "Beverage", "Drink", "Sweets", "Confectionery", "Cooking", "Baking", "Fast Food", "Sauce",
             "Condiments", "Spice", "Nut", "Berry", "Leaf", "Root", "Vegetation", "Flora"]


MAXIMO_RECORTES = 10
MUY_SEGURO = 70      # con este porcentaje basta que AWS lo vea una vez
DUDOSO = 55          # si lo vio en 2 pedazos, tiene que pasar de este porcentaje
MINIMO = 50          # menos que esto no se toma en cuenta

# Para los pedazos se le pide a AWS solo comida
SOLO_COMIDA = {"GeneralLabels": {"LabelCategoryInclusionFilters": ["Food and Beverage"]}}


# Rekognition acepta fotos de máximo 5 MB, por eso se achica la foto antes de mandarla
def abrir_foto(contenido):
    imagen = Image.open(io.BytesIO(contenido))
    imagen = imagen.convert("RGB")
    imagen.thumbnail((1600, 1600))
    return imagen


def a_bytes(imagen):
    salida = io.BytesIO()
    imagen.save(salida, format="JPEG", quality=90)
    return salida.getvalue()


# Los pedazos pequeños se agrandan, AWS reconoce mejor así
def agrandar(imagen):
    if imagen.width < 600:
        alto = int(imagen.height * 600 / imagen.width)
        imagen = imagen.resize((600, alto))
    return imagen


# Corta un pedazo de la foto con un poco de margen. La caja de AWS viene en porcentajes (0 a 1)
def recortar(imagen, caja):
    margen = 0.03
    izquierda = max(0, int((caja["Left"] - margen) * imagen.width))
    arriba = max(0, int((caja["Top"] - margen) * imagen.height))
    derecha = min(imagen.width, int((caja["Left"] + caja["Width"] + margen) * imagen.width))
    abajo = min(imagen.height, int((caja["Top"] + caja["Height"] + margen) * imagen.height))
    return imagen.crop((izquierda, arriba, derecha, abajo))


# La foto partida en 4 cuadros iguales
def partir_en_cuatro(imagen):
    mitad_ancho = imagen.width // 2
    mitad_alto = imagen.height // 2
    cajas = [
        (0, 0, mitad_ancho, mitad_alto),
        (mitad_ancho, 0, imagen.width, mitad_alto),
        (0, mitad_alto, mitad_ancho, imagen.height),
        (mitad_ancho, mitad_alto, imagen.width, imagen.height),
    ]
    partes = []
    for caja in cajas:
        partes.append(imagen.crop(caja))
    return partes


# Le pregunta a AWS qué ve en una imagen
def preguntar(cliente, imagen, solo_comida):
    if solo_comida:
        return cliente.detect_labels(Image={"Bytes": a_bytes(imagen)}, MaxLabels=50,
                                     MinConfidence=MINIMO, Settings=SOLO_COMIDA)
    return cliente.detect_labels(Image={"Bytes": a_bytes(imagen)}, MaxLabels=100, MinConfidence=MINIMO)


# Quita tildes y pasa a minúsculas: "Limón" queda "limon"
def sin_tildes(texto):
    texto = texto.lower()
    cambios = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n"}
    for letra in cambios:
        texto = texto.replace(letra, cambios[letra])
    return texto


# Guarda un ingrediente: su confianza más alta y en cuántos pedazos apareció
def guardar(encontrados, clave, confianza):
    if clave not in encontrados:
        encontrados[clave] = {"confianza": 0, "votos": 0}
    encontrados[clave]["votos"] = encontrados[clave]["votos"] + 1
    if confianza > encontrados[clave]["confianza"]:
        encontrados[clave]["confianza"] = confianza


# Pasa un nombre en inglés a una clave del catálogo. Revisa también los otros nombres (Aliases)
def traducir(etiqueta):
    if etiqueta["Name"] in TRADUCCION:
        return TRADUCCION[etiqueta["Name"]]
    for alias in etiqueta.get("Aliases", []):
        if alias["Name"] in TRADUCCION:
            return TRADUCCION[alias["Name"]]
    return None


# Revisa lo que dijo AWS de un pedazo. Cada ingrediente cuenta un solo voto por pedazo
def revisar_etiquetas(respuesta, encontrados, no_reconocidos, etiquetas):
    mejores = {}   # {"tomate": 57.0} solo de este pedazo
    for etiqueta in respuesta["Labels"]:
        nombre_ingles = etiqueta["Name"]
        if nombre_ingles not in etiquetas or etiqueta["Confidence"] > etiquetas[nombre_ingles]:
            etiquetas[nombre_ingles] = etiqueta["Confidence"]

        clave = traducir(etiqueta)
        if clave is not None:
            if clave not in mejores or etiqueta["Confidence"] > mejores[clave]:
                mejores[clave] = etiqueta["Confidence"]
        elif nombre_ingles not in GENERALES and etiqueta["Confidence"] >= MUY_SEGURO:
            # Comida que AWS ve claro pero no está en nuestro catálogo
            for categoria in etiqueta.get("Categories", []):
                if categoria["Name"] == "Food and Beverage" and nombre_ingles not in no_reconocidos:
                    no_reconocidos.append(nombre_ingles)

    for clave in mejores:
        guardar(encontrados, clave, mejores[clave])


# Busca en el texto de la foto nombres de ingredientes del catálogo
def revisar_texto(respuesta, encontrados):
    palabras = []
    for texto in respuesta["TextDetections"]:
        if texto["Type"] == "LINE":
            palabras.append(sin_tildes(texto["DetectedText"]))
    # Se dejan espacios a los lados para buscar palabras completas ("sal" no está en "salsa")
    todo = " " + " ".join(palabras) + " "

    # Primero los nombres largos: si dice "salsa de tomate" no debe contar también "tomate"
    ingredientes = []
    for ingrediente in catalogo.INGREDIENTES:
        if ingrediente["clave"] not in catalogo.BASICOS:
            ingredientes.append(ingrediente)
    ingredientes.sort(key=largo_del_nombre, reverse=True)

    for ingrediente in ingredientes:
        nombre = " " + sin_tildes(ingrediente["nombre"]) + " "
        if nombre in todo:
            guardar(encontrados, ingrediente["clave"], 90.0)
            todo = todo.replace(nombre, " ")


def largo_del_nombre(ingrediente):
    return len(ingrediente["nombre"])


@router.post("/reconocer")
async def reconocer(foto: UploadFile):
    contenido = await foto.read()
    if len(contenido) == 0:
        raise HTTPException(status_code=400, detail="No se recibió ninguna foto.")

    try:
        imagen = abrir_foto(contenido)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="El archivo no es una foto.")

    encontrados = {}       # {"tomate": {"confianza": 96.4, "votos": 2}}
    no_reconocidos = []    # nombres en inglés de comida que no tenemos
    etiquetas = {}         # todo lo que dijo AWS, para revisar el diccionario

    try:
        cliente = boto3.client("rekognition")

        # 1. La foto completa, sin filtro, para que marque platos, tazones y cajas
        completa = preguntar(cliente, imagen, False)
        revisar_etiquetas(completa, encontrados, no_reconocidos, etiquetas)

        # 2. Cada objeto marcado con un cuadro, recortado y agrandado
        recortes = 0
        for etiqueta in completa["Labels"]:
            for objeto in etiqueta.get("Instances", []):
                caja = objeto["BoundingBox"]
                # Los objetos que ocupan más de media foto (como el refrigerador) no se recortan
                if caja["Width"] * caja["Height"] > 0.5:
                    continue
                if recortes < MAXIMO_RECORTES:
                    pedazo = recortar(imagen, objeto["BoundingBox"])
                    if pedazo.width >= 40 and pedazo.height >= 40:
                        respuesta = preguntar(cliente, agrandar(pedazo), True)
                        revisar_etiquetas(respuesta, encontrados, no_reconocidos, etiquetas)
                        recortes = recortes + 1

        # 3. Si casi no hubo cuadros, la foto partida en 4
        if recortes < 3 and imagen.width >= 400 and imagen.height >= 400:
            for parte in partir_en_cuatro(imagen):
                respuesta = preguntar(cliente, agrandar(parte), True)
                revisar_etiquetas(respuesta, encontrados, no_reconocidos, etiquetas)

        # 4. El texto de los empaques
        texto = cliente.detect_text(Image={"Bytes": a_bytes(imagen)})
        revisar_texto(texto, encontrados)
    except (BotoCoreError, ClientError):
        raise HTTPException(status_code=503, detail="No se pudo usar el reconocimiento de fotos. Intenta más tarde.")

    # Solo se queda lo que AWS vio muy claro o lo que vio en 2 pedazos o más
    ingredientes = []
    for clave in encontrados:
        datos = encontrados[clave]
        if datos["confianza"] >= MUY_SEGURO or (datos["votos"] >= 2 and datos["confianza"] > DUDOSO):
            ingredientes.append({
                "clave": clave,
                "nombre": catalogo.nombre(clave),
                "confianza": round(datos["confianza"] / 100, 2),
            })
    # Los más seguros primero
    ingredientes.sort(key=sacar_confianza, reverse=True)

    lista_aws = []
    for nombre_ingles in etiquetas:
        lista_aws.append(nombre_ingles + " " + str(round(etiquetas[nombre_ingles])) + "%")

    return {"ingredientes": ingredientes, "no_reconocidos": len(no_reconocidos), "etiquetas_aws": lista_aws}


def sacar_confianza(ingrediente):
    return ingrediente["confianza"]
