# Reconocer ingredientes en una foto con AWS Rekognition
# Responsable: David
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
    # carnes y mariscos
    "Chicken": "pollo_granja",
    "Poultry": "pollo_granja",
    "Beef": "res_lomo",
    "Steak": "res_lomo",
    "Pork": "cerdo_lomo",
    "Bacon": "cerdo_panza",
    "Sausage": "salchicha",
    "Hot Dog": "salchicha",
    "Fish": "pescado_blanco",
    "Shrimp": "camaron",
    "Prawn": "camaron",
    "Octopus": "pulpo",
    "Crab": "cangrejo",
    "Tuna": "atun",
    "Sardine": "sardina",
    # huevo y lácteos
    "Egg": "huevo",
    "Milk": "leche",
    "Cheese": "queso_fresco",
    "Butter": "mantequilla",
    "Cream": "crema",
    # verduras
    "Tomato": "tomate",
    "Onion": "cebolla",
    "Garlic": "ajo",
    "Potato": "papa",
    "Carrot": "zanahoria",
    "Broccoli": "brocoli",
    "Cauliflower": "coliflor",
    "Cabbage": "repollo",
    "Lettuce": "lechuga",
    "Spinach": "espinaca",
    "Cucumber": "pepino",
    "Bell Pepper": "chile_pimiento",
    "Jalapeno": "chile_jalapeno",
    "Radish": "rabano",
    "Beet": "remolacha",
    "Mushroom": "champinon",
    "Zucchini": "ayote_tierno",
    "Squash": "ayote_tierno",
    "Corn": "elote_tierno",
    "Sweet Potato": "camote",
    "Yam": "camote",
    "Cassava": "yuca",
    "Green Bean": "ejote",
    "Pea": "arvejas",
    "Avocado": "aguacate",
    "Plantain": "platano_verde",
    "Parsley": "perejil",
    "Cilantro": "cilantro",
    # frutas
    "Lemon": "limon",
    "Lime": "limon",
    "Orange": "naranja",
    "Banana": "banano",
    "Mango": "mango",
    "Pineapple": "pina",
    "Papaya": "papaya",
    "Melon": "melon",
    "Cantaloupe": "melon",
    "Watermelon": "sandia",
    "Strawberry": "fresa",
    "Apple": "manzana",
    "Peach": "durazno",
    "Coconut": "coco",
    # granos, pan y otros
    "Rice": "arroz",
    "Bean": "frijol_negro",
    "Pasta": "pasta_fideo",
    "Noodle": "pasta_fideo",
    "Spaghetti": "pasta_fideo",
    "Oatmeal": "avena",
    "Flour": "harina_trigo",
    "Bread": "pan_frances",
    "Tortilla": "tortilla_maiz",
    "Coffee": "cafe_molido",
    "Chocolate": "chocolate_mesa",
    "Mayonnaise": "mayonesa",
    "Honey": "miel",
    "Peanut": "mani",
    "Ketchup": "salsa_tomate",
    "Mustard": "mostaza",
    "Vinegar": "vinagre",
}

# Nombres generales que no son un ingrediente en sí
GENERALES = ["Food", "Produce", "Vegetable", "Fruit", "Plant", "Meal", "Dish", "Ingredient",
             "Citrus Fruit", "Meat", "Seafood", "Dairy", "Herbs", "Bowl", "Plate", "Grocery Store", "Market"]


# Rekognition acepta fotos de máximo 5 MB, por eso se achica la foto antes de mandarla
def achicar(contenido):
    imagen = Image.open(io.BytesIO(contenido))
    imagen = imagen.convert("RGB")
    imagen.thumbnail((1600, 1600))
    salida = io.BytesIO()
    imagen.save(salida, format="JPEG", quality=85)
    return salida.getvalue()


@router.post("/reconocer")
async def reconocer(foto: UploadFile):
    contenido = await foto.read()
    if len(contenido) == 0:
        raise HTTPException(status_code=400, detail="No se recibió ninguna foto.")

    try:
        contenido = achicar(contenido)
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="El archivo no es una foto.")

    try:
        cliente = boto3.client("rekognition")
        respuesta = cliente.detect_labels(Image={"Bytes": contenido}, MaxLabels=50, MinConfidence=70)
    except (BotoCoreError, ClientError):
        raise HTTPException(status_code=503, detail="No se pudo usar el reconocimiento de fotos. Intenta más tarde.")

    ingredientes = []
    claves_vistas = []
    no_reconocidos = 0

    for etiqueta in respuesta["Labels"]:
        nombre_ingles = etiqueta["Name"]

        if nombre_ingles in TRADUCCION:
            clave = TRADUCCION[nombre_ingles]
            # Si dos nombres dan la misma clave (Lemon y Lime), se pone una sola vez
            if clave not in claves_vistas:
                claves_vistas.append(clave)
                ingredientes.append({
                    "clave": clave,
                    "nombre": catalogo.nombre(clave),
                    "confianza": round(etiqueta["Confidence"] / 100, 2),
                })
        elif nombre_ingles not in GENERALES:
            # Es comida pero no está en nuestro catálogo
            for categoria in etiqueta.get("Categories", []):
                if categoria["Name"] == "Food and Beverage":
                    no_reconocidos = no_reconocidos + 1

    return {"ingredientes": ingredientes, "no_reconocidos": no_reconocidos}
