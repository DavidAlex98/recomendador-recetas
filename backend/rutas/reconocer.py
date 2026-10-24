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
    # carnes
    "Chicken": "pollo_granja",
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
             "Cereal Bowl", "Dessert", "Grain", "Seed", "Snack", "Salad", "Platter", "Kitchen", "Table"]


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
    etiquetas = []

    for etiqueta in respuesta["Labels"]:
        nombre_ingles = etiqueta["Name"]
        # Lo que respondió AWS tal cual, para revisar el diccionario
        etiquetas.append(nombre_ingles + " " + str(round(etiqueta["Confidence"])) + "%")

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

    return {"ingredientes": ingredientes, "no_reconocidos": no_reconocidos, "etiquetas_aws": etiquetas}
