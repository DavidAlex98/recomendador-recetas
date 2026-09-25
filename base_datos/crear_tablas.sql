-- =====================================================================
-- RecetApp: creación de la base de datos
-- Responsables: Cristian, Manrique y Rubí (equipo de base de datos)
--
-- Cómo correrlo:
--   MySQL Workbench: File > Open SQL Script > este archivo > botón del rayo
--   XAMPP / phpMyAdmin: pestaña Importar > elegir este archivo > Continuar
--
-- Enfoque híbrido: los INGREDIENTES no tienen tabla. Viven en el archivo
-- datos/ingredientes-guatemala.json y aquí solo se guarda su CLAVE
-- (por ejemplo 'cebolla' o 'pollo_granja').
--
-- OJO: correr este archivo BORRA las tablas y sus datos. Después hay que
-- volver a importar las recetas con base_datos/importar_recetas.py
-- =====================================================================

CREATE DATABASE IF NOT EXISTS recetapp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE recetapp;

-- Se borran en orden inverso por las llaves foráneas
DROP TABLE IF EXISTS pasos;
DROP TABLE IF EXISTS receta_ingredientes;
DROP TABLE IF EXISTS recetas;

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
    tiempo_total_min   INT          NOT NULL,
    porciones          INT          NOT NULL,
    picante_nivel      TINYINT      NOT NULL DEFAULT 0,   -- 0 a 4
    vegetariano        BOOLEAN      NOT NULL DEFAULT FALSE,
    vegano             BOOLEAN      NOT NULL DEFAULT FALSE,
    sin_gluten         BOOLEAN      NOT NULL DEFAULT FALSE,
    sin_lacteos        BOOLEAN      NOT NULL DEFAULT FALSE,
    costo_porcion_gtq  DECIMAL(8,2),
    calorias_porcion   INT,
    INDEX idx_categoria (categoria),
    INDEX idx_receta_base (receta_base)
);

-- Ingredientes de cada receta: se guarda la CLAVE del catálogo JSON
CREATE TABLE receta_ingredientes (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    receta_id    VARCHAR(10)  NOT NULL,
    clave        VARCHAR(60)  NOT NULL,                   -- clave del JSON, ej. 'cebolla'
    cantidad     DECIMAL(8,2),
    unidad       VARCHAR(30),
    preparacion  VARCHAR(150),
    opcional     BOOLEAN      NOT NULL DEFAULT FALSE,
    FOREIGN KEY (receta_id) REFERENCES recetas(id) ON DELETE CASCADE,
    INDEX idx_clave (clave)                               -- acelera la recomendación
);

-- Pasos de preparación en orden
CREATE TABLE pasos (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    receta_id    VARCHAR(10)  NOT NULL,
    numero       INT          NOT NULL,
    instruccion  TEXT         NOT NULL,
    FOREIGN KEY (receta_id) REFERENCES recetas(id) ON DELETE CASCADE
);

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
-- Recuerden agregar también sus DROP TABLE arriba, en el orden correcto.
-- =====================================================================
