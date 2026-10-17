-- Tablas de RecetApp (PostgreSQL)
-- Responsables: Cristian, Manrique y Rubí
--
-- Correr en pgAdmin, en el Query Tool de la base recetapp.
-- Después: vistas_y_procedimientos.sql e importar_recetas.py

-- Usuarios. rol: usuario o admin
CREATE TABLE usuarios (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    correo           VARCHAR(150) NOT NULL UNIQUE,
    contrasena_hash  VARCHAR(255) NOT NULL,
    rol              VARCHAR(20) NOT NULL DEFAULT 'usuario',
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en        TIMESTAMP DEFAULT NOW()
);

-- Recetas (se llenan con importar_recetas.py)
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

-- Ingredientes de cada receta (clave del catálogo JSON)
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

-- Ingredientes que tiene cada usuario (clave del catálogo JSON)
CREATE TABLE despensa (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    clave       VARCHAR(60) NOT NULL
);

-- Recetas favoritas
CREATE TABLE favoritos (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    receta_id   VARCHAR(10) NOT NULL REFERENCES recetas(id),
    creado_en   TIMESTAMP DEFAULT NOW()
);

-- Recetas que vio cada usuario
CREATE TABLE historial (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    receta_id   VARCHAR(10) NOT NULL REFERENCES recetas(id),
    visto_en    TIMESTAMP DEFAULT NOW()
);

-- Proceso 1: plan semanal. estado: planificado, cocinado u omitido
CREATE TABLE plan_semanal (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    receta_id   VARCHAR(10) NOT NULL REFERENCES recetas(id),
    dia         VARCHAR(10) NOT NULL,
    estado      VARCHAR(20) NOT NULL DEFAULT 'planificado'
);

-- Proceso 2: recetas propuestas. estado: pendiente, aprobada o rechazada
CREATE TABLE recetas_propuestas (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente',
    motivo_rechazo  TEXT,
    creado_en       TIMESTAMP DEFAULT NOW()
);

-- Acciones importantes de los usuarios
CREATE TABLE bitacora (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER REFERENCES usuarios(id),
    accion      VARCHAR(200) NOT NULL,
    fecha       TIMESTAMP DEFAULT NOW()
);
