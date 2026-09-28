-- RecetApp: tablas de la base de datos (PostgreSQL)
-- Responsables: Cristian, Manrique y Rubí
--
-- Cómo correrlo: en pgAdmin, clic derecho en la base recetapp > Query Tool >
-- abrir este archivo > botón Play.
--
-- Los ingredientes NO tienen tabla: están en datos/ingredientes-guatemala.json.
-- Aquí solo se guarda su clave, por ejemplo 'cebolla'.

-- Borrar las tablas si ya existen
DROP TABLE IF EXISTS pasos;
DROP TABLE IF EXISTS receta_ingredientes;
DROP TABLE IF EXISTS recetas;

-- Recetas
CREATE TABLE recetas (
    id           VARCHAR(10) PRIMARY KEY,
    nombre       VARCHAR(150) NOT NULL,
    categoria    VARCHAR(60) NOT NULL,
    descripcion  TEXT,
    dificultad   VARCHAR(10) NOT NULL,
    tiempo_min   INTEGER NOT NULL,
    porciones    INTEGER NOT NULL,
    vegetariano  BOOLEAN NOT NULL,
    vegano       BOOLEAN NOT NULL,
    sin_gluten   BOOLEAN NOT NULL
);

-- Ingredientes de cada receta (clave del archivo JSON)
CREATE TABLE receta_ingredientes (
    id         SERIAL PRIMARY KEY,
    receta_id  VARCHAR(10) NOT NULL REFERENCES recetas(id),
    clave      VARCHAR(60) NOT NULL,
    cantidad   DECIMAL(8,2),
    unidad     VARCHAR(30),
    opcional   BOOLEAN NOT NULL
);

-- Pasos de cada receta
CREATE TABLE pasos (
    id           SERIAL PRIMARY KEY,
    receta_id    VARCHAR(10) NOT NULL REFERENCES recetas(id),
    numero       INTEGER NOT NULL,
    instruccion  TEXT NOT NULL
);

-- POR HACER (equipo de base de datos):
-- agregar aquí las tablas usuarios, despensa, favoritos, historial,
-- lista_compras, recetas_propuestas y bitacora, según el diagrama.
-- Recuerden agregar también su DROP TABLE arriba.
