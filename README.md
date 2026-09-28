# RecetApp

Aplicación web que recomienda recetas guatemaltecas según los ingredientes que tienes en casa.
Proyecto del curso de Ingeniería de Software, Universidad Regional de Guatemala.

**Tecnologías:** Python (FastAPI) · PostgreSQL · HTML, CSS y JavaScript.

## Integrantes

<!-- Primera tarea de cada integrante: agregar su nombre aquí con su propia rama y Pull Request -->
- David Montenegro (líder técnico)

## Estructura del proyecto

Cada archivo tiene un responsable. Trabaja solo en tus archivos para no chocar con los demás.

```
RecetApp/
├── backend/                  ← servidor (FastAPI)
│   ├── main.py               David    · une todas las rutas; casi no se toca
│   ├── db.py                 David    · conexión a PostgreSQL: consultar() y ejecutar()
│   ├── catalogo.py           David    · lee el catálogo JSON de ingredientes
│   └── rutas/
│       ├── ejemplo.py        David    · EJEMPLO: cópialo como modelo
│       ├── ingredientes.py   Shanda
│       ├── recetas.py        Shanda
│       ├── despensa.py       Shanda
│       ├── usuarios.py       Rubí
│       ├── recomendacion.py  David
│       ├── favoritos.py      Cristian
│       └── admin.py          Brandon
├── frontend/                 ← páginas web
│   ├── index.html + js/inicio.js       David    · EJEMPLO: cópialo como modelo
│   ├── checklist.html + js/checklist.js Manrique
│   ├── receta.html + js/receta.js      Brandon
│   ├── login.html + js/login.js        Brandon
│   ├── js/api.js             David    · funciones compartidas: pedirGET, enviarPOST, escapar
│   └── css/estilos.css       Brandon  · estilos de todas las páginas
├── base_datos/
│   ├── crear_tablas.sql      Cristian, Manrique, Rubí
│   ├── importar_recetas.py   David    · carga las recetas en la base de datos
│   └── preparar_bd.py        David    · crea todo y carga las recetas con un comando
├── datos/
│   ├── ingredientes-guatemala.json     catálogo de 197 ingredientes
│   └── recetas-guatemala.ndjson        3,248 recetas (se importan 2,665 sin repetidas)
├── .env.example              modelo de la configuración (sin contraseñas)
└── requirements.txt          librerías de Python
```

**Enfoque híbrido:** los ingredientes viven en el archivo JSON, no en PostgreSQL. En la base de datos
un ingrediente se guarda por su **clave** (`cebolla`, `pollo_granja`), nunca por su nombre escrito.

## Instalación (una sola vez)

Necesitas tener instalados **Python 3.11 o más nuevo**, **PostgreSQL**, **Git** y **VS Code**.

**Instalar PostgreSQL (gratis):** descárgalo de https://www.postgresql.org/download/windows/
(botón *Download the installer*). En el instalador deja todo por defecto (incluye **pgAdmin**,
el programa para ver la base de datos). Cuando pida una **contraseña** para el usuario `postgres`,
escribe una que recuerdes: la vas a poner en el archivo `.env`. El puerto déjalo en **5432**.
PostgreSQL queda encendido solo cada vez que prendes la computadora; no hay que abrir nada.
Los comandos van en la terminal de VS Code (menú *Terminal → New Terminal*), dentro de la carpeta del proyecto.

**1. Crear el entorno virtual e instalar las librerías**

```bash
python -m venv venv
venv\Scripts\activate          # en Windows
# source venv/bin/activate     # en Mac o Linux
python -m pip install -r requirements.txt
```

Cada vez que abras VS Code, activa el entorno con `venv\Scripts\activate`. Sabrás que está activo
porque la terminal muestra `(venv)` al inicio.

Si Windows dice *"la ejecución de scripts está deshabilitada en este sistema"*, corre esto una sola vez
(responde `S` si pregunta) y vuelve a activar el entorno:

```bash
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**2. Crear tu archivo de configuración**

```bash
Copy-Item .env.example .env
```

Abre el `.env` y en `DB_PASSWORD=` escribe la contraseña que pusiste al instalar PostgreSQL.

**3. Crear la base de datos y cargar las recetas**

Corre:

```bash
python base_datos/preparar_bd.py
```

Debe terminar con `¡Importación completada!`. Este comando crea la base `recetapp`, sus tablas y
carga las recetas. Se puede volver a correr cuando el equipo cambie `crear_tablas.sql`
(borra y vuelve a crear todo).

## Correr la aplicación

```bash
cd backend
python -m uvicorn main:app --reload
```

Abre en el navegador:

- **http://localhost:8000**: la aplicación. Si dice "Base de datos conectada: 2665 recetas", todo está bien.
- **http://localhost:8000/docs**: la lista de endpoints, donde puedes probarlos sin escribir frontend.

Con `--reload`, el servidor se reinicia solo cada vez que guardas un archivo de Python.
Para detenerlo: `Ctrl + C`.

## Cómo agregar un endpoint (backend)

1. Abre tu archivo en `backend/rutas/` (por ejemplo `recetas.py`). Ya tiene tus tareas escritas arriba.
2. Copia la forma de un endpoint de `rutas/ejemplo.py` y adáptalo.
3. Guarda y pruébalo en http://localhost:8000/docs

```python
@router.get("/recetas/{id_receta}")
def detalle_receta(id_receta: str):
    filas = consultar("SELECT * FROM recetas WHERE id = %s", (id_receta,))
    if not filas:
        raise HTTPException(status_code=404, detail="Receta no encontrada")
    return filas[0]
```

## Cómo agregar una página (frontend)

1. Abre tu página (`checklist.html`, `receta.html`...) y su archivo `.js`.
2. Sigue el modelo de `index.html` y `js/inicio.js`: pedir datos con `pedirGET` o `enviarPOST`,
   mostrarlos y avisar si algo falla.
3. Mientras el endpoint no exista, trabaja con datos de prueba escritos en tu `.js`.
   Cuando esté listo, cambia los datos de prueba por la llamada a la API.

## Ver la base de datos (pgAdmin)

Abre **pgAdmin** (se instaló con PostgreSQL) → *Servers* → *PostgreSQL* (pide tu contraseña) →
*Databases* → **recetapp** → *Schemas* → *public* → *Tables*. Clic derecho en una tabla →
*View/Edit Data* → *All Rows*. Para escribir consultas: clic derecho en **recetapp** → *Query Tool*.

## Cómo subir tus cambios (Git)

Nunca trabajes directo en `main`. Usa siempre una rama con tu nombre y la tarea:

```bash
git checkout main
git pull                              # 1. traer lo último
git checkout -b rubi/login            # 2. crear tu rama: nombre/tarea
# ... trabajar y guardar ...
git add .
git commit -m "Agrega inicio de sesión"   # 3. guardar con un mensaje claro
git push -u origin rubi/login         # 4. subir tu rama
```

5. En GitHub, abre un **Pull Request** de tu rama hacia `main`. David lo revisa y lo une.

## Reglas del equipo

- **SQL:** los valores siempre van con `%s`, nunca pegados con `f"..."` o `+`. Así se evita la inyección SQL.
- **Frontend:** cualquier texto que venga de la API o del usuario pasa por `escapar()` antes de ir a `innerHTML`.
- **Contraseñas:** el archivo `.env` nunca se sube. Las contraseñas de usuarios se guardan con hash.
- **Datos personales:** para pruebas, solo usuarios ficticios.
- **Bloqueos:** si llevas más de un día trabado, avisa en el grupo.

## Problemas comunes

| Mensaje | Solución |
|---|---|
| `password authentication failed` | La contraseña en `.env` no es la que pusiste al instalar PostgreSQL. |
| `Connection refused` | PostgreSQL está apagado. Busca *Servicios* en Windows y enciende `postgresql`. |
| `relation "recetas" does not exist` | Corre `python base_datos/preparar_bd.py`. |
| `ModuleNotFoundError` | Activa el entorno (`venv\Scripts\activate`) y corre `python -m pip install -r requirements.txt`. |
| `la ejecución de scripts está deshabilitada` | Corre `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` una vez. |
| `uvicorn` no se reconoce | Usa `python -m uvicorn main:app --reload` dentro de la carpeta `backend`. |
| La página no cambia | Recarga con `Ctrl + F5` para que el navegador no use la versión guardada. |

## Datos

El catálogo de recetas y de ingredientes se generó a partir de 105 preparaciones tradicionales
guatemaltecas y sus variantes. Costos y calorías son **estimaciones**. Algunas variantes tienen
errores conocidos (por ejemplo, "Huevos con chorizo" no incluye chorizo en su lista de ingredientes).
