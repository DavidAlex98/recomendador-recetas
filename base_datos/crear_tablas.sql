CREATE TABLE usuarios (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    correo           VARCHAR(150) NOT NULL UNIQUE,
    contrasena_hash  VARCHAR(255) NOT NULL,
    rol              VARCHAR(20) NOT NULL DEFAULT 'usuario',   
    activo           BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en        TIMESTAMP DEFAULT NOW()
);


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



CREATE TABLE despensa (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    clave       VARCHAR(60) NOT NULL
);


CREATE TABLE favoritos (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    receta_id   VARCHAR(10) NOT NULL REFERENCES recetas(id),
    creado_en   TIMESTAMP DEFAULT NOW()
);


CREATE TABLE historial (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    receta_id   VARCHAR(10) NOT NULL REFERENCES recetas(id),
    visto_en    TIMESTAMP DEFAULT NOW()
);


CREATE TABLE plan_semanal (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER NOT NULL REFERENCES usuarios(id),
    receta_id   VARCHAR(10) NOT NULL REFERENCES recetas(id),
    dia         VARCHAR(10) NOT NULL,                        -- lunes a domingo
    estado      VARCHAR(20) NOT NULL DEFAULT 'planificado'   -- planificado, cocinado u omitido
);


CREATE TABLE recetas_propuestas (
    id              SERIAL PRIMARY KEY,
    usuario_id      INTEGER NOT NULL REFERENCES usuarios(id),
    nombre          VARCHAR(150) NOT NULL,
    descripcion     TEXT,
    estado          VARCHAR(20) NOT NULL DEFAULT 'pendiente',  
    motivo_rechazo  TEXT,
    creado_en       TIMESTAMP DEFAULT NOW()
);


CREATE TABLE bitacora (
    id          SERIAL PRIMARY KEY,
    usuario_id  INTEGER REFERENCES usuarios(id),
    accion      VARCHAR(200) NOT NULL,
    fecha       TIMESTAMP DEFAULT NOW()
);