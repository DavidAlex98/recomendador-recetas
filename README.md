# RecetApp

Aplicación web que recomienda recetas guatemaltecas según los ingredientes que tienes en casa.
Proyecto del curso de Ingeniería de Software, Universidad Regional de Guatemala.

Tecnologías: Python (FastAPI), PostgreSQL, HTML, CSS y JavaScript.

## Integrantes

- David Montenegro

## Carpetas

```
backend/        el servidor (Python)
  main.py         une todo
  db.py           conexión a la base de datos
  catalogo.py     lee el archivo de ingredientes
  rutas/          los endpoints, un archivo por persona
frontend/       las páginas (HTML, CSS y JavaScript)
base_datos/     crear_tablas.sql e importar_recetas.py
datos/          ingredientes-guatemala.json y recetas.json
```

Cada archivo dice arriba quién es el responsable. Trabaja solo en tus archivos.

Los ingredientes no están en la base de datos, están en `datos/ingredientes-guatemala.json`.
En la base solo se guarda su clave, por ejemplo `cebolla`.

## Instalar (una sola vez)

Necesitas Python, PostgreSQL, Git y VS Code.

**1. PostgreSQL:** descárgalo de https://www.postgresql.org/download/windows/ y deja todo por defecto.
Anota la contraseña que pongas.

**2. Librerías:** en la terminal de VS Code, dentro de la carpeta del proyecto:

```bash
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
```

Si sale "la ejecución de scripts está deshabilitada", corre una vez
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y vuelve a activar.

**3. Archivo .env:**

```bash
Copy-Item .env.example .env
```

Ábrelo y en `DB_PASSWORD=` pon tu contraseña de PostgreSQL.

**4. Crear la base de datos (pgAdmin):** clic derecho en *Databases* > *Create* > *Database* > nombre `recetapp`.

**5. Crear las tablas (pgAdmin):** clic derecho en `recetapp` > *Query Tool* > abrir `base_datos/crear_tablas.sql` > botón Play.

**6. Cargar las recetas:**

```bash
python base_datos/importar_recetas.py
```

Si cambian las tablas, repite los pasos 5 y 6.

## Encender la app

```bash
cd backend
python -m uvicorn main:app --reload
```

- http://localhost:8000 : la aplicación
- http://localhost:8000/docs : para probar los endpoints

Para apagarla: `Ctrl + C`.

## Subir tus cambios

```bash
git checkout main
git pull
git checkout -b tunombre/tarea
git add .
git commit -m "Qué hiciste"
git push -u origin tunombre/tarea
```

Luego abre un Pull Request en GitHub.

## Reglas

- En SQL los valores van con `%s`, nunca pegados en el texto.
- El archivo `.env` no se sube a GitHub.
- Si instalas una librería nueva, agrégala a `requirements.txt`.

## Errores comunes

| Error | Solución |
|---|---|
| `password authentication failed` | La contraseña del `.env` está mal. |
| `relation "recetas" does not exist` | Haz los pasos 5 y 6. |
| `ModuleNotFoundError` | Activa el venv y corre `python -m pip install -r requirements.txt`. |
| `Could not import module "main"` | Tienes que estar en la carpeta `backend`. |
| La página no cambia | Recarga con `Ctrl + F5`. |
