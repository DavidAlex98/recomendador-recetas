# RecetApp

Aplicación web que recomienda recetas guatemaltecas según los ingredientes que tienes en casa.
Proyecto del curso de Ingeniería de Software, Universidad Regional de Guatemala.

Tecnologías: Python (FastAPI), PostgreSQL, HTML, CSS y JavaScript.

## Integrantes

| Integrante | Parte del proyecto |
|---|---|
| David Montenegro | Servidor, base de datos, recetas, recomendación, historial, diagramas |
| Brandon Stiven Contreras López | Administración (propuestas, recetas, reporte), login, estilos |
| Rubí Simon | Registro e inicio de sesión (usuarios) |
| Shanda López | Ingredientes y despensa |
| Cristian | Favoritos y plan semanal |
| Manrique | Página "¿Qué tengo en casa?" |

## Páginas

| Página | Qué hace | Necesita sesión |
|---|---|---|
| `index.html` | Inicio; con sesión muestra lo último que viste | No |
| `checklist.html` | Marcar ingredientes y ver qué recetas salen | No |
| `receta.html` | Una receta; con sesión: favoritos y plan | No |
| `login.html` / `registro.html` | Entrar o crear cuenta | No |
| `despensa.html` | Guardar lo que tienes en casa | Sí |
| `favoritos.html` | Recetas guardadas | Sí |
| `plan.html` | Plan de comidas de la semana | Sí |
| `proponer.html` | Proponer una receta nueva | Sí |
| `admin.html` | Propuestas, recetas, reporte y bitácora | Sí, rol admin |

## Carpetas

```
backend/        el servidor (Python)
  main.py         une todo
  db.py           conexión a la base de datos
  catalogo.py     lee el archivo de ingredientes
  rutas/          los endpoints, un archivo por persona
frontend/       las páginas (HTML, CSS y JavaScript)
base_datos/     crear_tablas.sql, vistas_y_procedimientos.sql e importar_recetas.py
datos/          ingredientes-guatemala.json y recetas.json
docs/diagramas/ diagramas PlantUML (.puml) y sus imágenes (.png)
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

**5b. Crear las vistas y procedimientos (pgAdmin):** en el mismo *Query Tool*, abrir
`base_datos/vistas_y_procedimientos.sql` > botón Play. Va siempre después del paso 5.

**6. Cargar las recetas:**

```bash
python base_datos/importar_recetas.py
```

Si cambian las tablas, repite los pasos 5, 5b y 6.

`importar_recetas.py` se puede correr las veces que quieras: actualiza las recetas
sin borrar los favoritos, el plan ni el historial de los usuarios.

## Encender la app

```bash
cd backend
python -m uvicorn main:app --reload
```

- http://localhost:8000 : la aplicación
- http://localhost:8000/docs : para probar los endpoints

Para apagarla: `Ctrl + C`.

## Crear un administrador

Regístrate normal en `registro.html` y luego, en pgAdmin (*Query Tool* sobre `recetapp`):

```sql
UPDATE usuarios SET rol = 'admin' WHERE correo = 'tu@correo.com';
```

Cierra sesión y vuelve a entrar: aparece el enlace **Admin** en la barra.

## Diagramas

En `docs/diagramas/` están en PlantUML y como imagen:

- `arquitectura` : cómo se conectan navegador, FastAPI, PostgreSQL y el JSON
- `casos_de_uso` : qué puede hacer el visitante, el usuario y el admin
- `base_de_datos` : tablas y relaciones
- `secuencia_recomendacion` : paso a paso de cómo se recomiendan recetas

Para editarlos: extensión **PlantUML** de VS Code (Alt + D para ver la vista previa).

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
| `relation "vista_..." does not exist` o `procedure ... does not exist` | Haz el paso 5b. |
| `Could not import module "main"` | Estar en la carpeta `backend`, o usar `--app-dir backend` desde la principal. |
| `Solo un administrador puede hacer esto` | Tu usuario no es admin; mira "Crear un administrador". |
| Error 500 al registrarse o entrar | Tablas viejas: repite los pasos 5, 5b y 6. |
| La página no cambia | Recarga con `Ctrl + F5`. |
