-- =====================================================================
-- RecetApp: creación de las tablas (PostgreSQL)
-- Responsables: Cristian, Manrique y Rubí (equipo de base de datos)
--
-- Cómo correrlo:
--   Lo más fácil:  python base_datos/preparar_bd.py
--   (crea la base de datos 'recetapp', corre este archivo y carga las recetas)
--
--   O a mano en pgAdmin: clic derecho en la base 'recetapp' > Query Tool >
--   abrir este archivo > botón ▶ (Execute)
--
-- Enfoque híbrido: los INGREDIENTES no tienen tabla. Viven en el archivo
-- datos/ingredientes-guatemala.json y aquí solo se guarda su CLAVE
-- (por ejemplo 'cebolla' o 'pollo_granja').
--
-- OJO: correr este archivo BORRA las tablas y sus datos. Después hay que
-- volver a importar las recetas con base_datos/importar_recetas.py
-- =====================================================================

-- CASCADE borra también lo que dependa de cada tabla
DROP TABLE IF EXISTS pasos CASCADE;
DROP TABLE IF EXISTS receta_ingredientes CASCADE;
DROP TABLE IF EXISTS recetas CASCADE;

-- ---------------------------------------------------------------------
-- Recetas (se llenan con importar_recetas.py)
-- ---------------------------------------------------------------------
CREATE TABLE recetas (
    id                 VARCHAR(10)  PRIMARY KEY,          -- ej. 'gt-0001'
    nombre             VARCHAR(150) NOT NULL,
    nombre_completo    VARCHAR(255) NOT NULL,
    receta_base        VARCHAR(60)  NOT NULL,             -- agrupa variantes del mismo plato
    categoria          VARCHAR(60)  NOT NULL,             -- ej. 'Sopas y caldos'
    descripcion        TEXT,
    departamento       VARCHAR(60),
    dificultad         VARCHAR(10)  NOT NULL,             -- facil, media, alta
    tiempo_total_min   INTEGER      NOT NULL,
    porciones          INTEGER      NOT NULL,
    picante_nivel      SMALLINT     NOT NULL DEFAULT 0,   -- 0 a 4
    vegetariano        BOOLEAN      NOT NULL DEFAULT FALSE,
    vegano             BOOLEAN      NOT NULL DEFAULT FALSE,
    sin_gluten         BOOLEAN      NOT NULL DEFAULT FALSE,
    sin_lacteos        BOOLEAN      NOT NULL DEFAULT FALSE,
    costo_porcion_gtq  NUMERIC(8,2),
    calorias_porcion   INTEGER
);

-- Ingredientes de cada receta: se guarda la CLAVE del catálogo JSON
CREATE TABLE receta_ingredientes (
    id           SERIAL       PRIMARY KEY,                -- SERIAL = número automático
    receta_id    VARCHAR(10)  NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    clave        VARCHAR(60)  NOT NULL,                   -- clave del JSON, ej. 'cebolla'
    cantidad     NUMERIC(8,2),
    unidad       VARCHAR(30),
    preparacion  VARCHAR(150),
    opcional     BOOLEAN      NOT NULL DEFAULT FALSE
);

-- Pasos de preparación en orden
CREATE TABLE pasos (
    id           SERIAL       PRIMARY KEY,
    receta_id    VARCHAR(10)  NOT NULL REFERENCES recetas(id) ON DELETE CASCADE,
    numero       INTEGER      NOT NULL,
    instruccion  TEXT         NOT NULL
);

-- Índices: aceleran las búsquedas por esas columnas
CREATE INDEX idx_recetas_categoria ON recetas (categoria);
CREATE INDEX idx_ingredientes_clave ON receta_ingredientes (clave);
CREATE INDEX idx_ingredientes_receta ON receta_ingredientes (receta_id);

-- =====================================================================
-- POR HACER (equipo de base de datos, Semana 2 del cronograma)
-- Escriban aquí las tablas que faltan, siguiendo el diseño de Brandon.
-- Pistas de columnas para empezar:
--
--   usuarios   : id, nombre, correo (único), contrasena_hash, rol, activo, creado_en
--   despensa   : id, usuario_id -> usuarios, clave (del JSON)
--   favoritos  : id, usuario_id -> usuarios, receta_id -> recetas, creado_en
--   historial  : id, usuario_id -> usuarios, receta_id -> recetas, visto_en
--
-- En PostgreSQL: id SERIAL PRIMARY KEY, fechas con TIMESTAMP DEFAULT NOW().
-- Recuerden agregar también sus DROP TABLE arriba.
-- =====================================================================
