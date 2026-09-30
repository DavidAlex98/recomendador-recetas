# Recomendación de recetas
# Responsable: David
#
#   POST /api/recomendaciones  ->  recetas que se pueden hacer con lo que tienes
#
# Regla: si te falta un ingrediente importante, esa receta NO sale.
# Los ingredientes opcionales no cuentan, y lo básico (sal, aceite, azúcar)
# se da por hecho que siempre lo hay en casa.

from fastapi import APIRouter
from pydantic import BaseModel

from db import consultar

router = APIRouter(prefix="/api")

# Lo que toda casa tiene
BASICOS = ["sal", "aceite", "azucar"]


class Despensa(BaseModel):
    ingredientes: list[str]


@router.post("/recomendaciones")
def recomendar(despensa: Despensa):
    tengo = despensa.ingredientes + BASICOS

    # La consulta de adentro busca las recetas a las que les falta algo importante.
    # La de afuera trae todas las demás, o sea, las que sí puedes hacer.
    sql = """
        SELECT id, nombre, categoria, dificultad, tiempo_min
        FROM recetas
        WHERE id NOT IN (
            SELECT receta_id FROM receta_ingredientes
            WHERE opcional = FALSE AND clave <> ALL(%s)
        )
        ORDER BY nombre
    """
    return consultar(sql, (tengo,))
