-- Vistas, funciones y procedimientos almacenados de RecetApp.
-- Responsable: David
--
-- Cómo correrlo (pgAdmin): clic derecho en recetapp > Query Tool >
-- abrir este archivo > botón Play.
-- Va DESPUÉS de crear_tablas.sql. Se puede correr las veces que quieras:
-- cada objeto se borra y se vuelve a crear.


-- =====================================================================
-- 1. VISTAS (consultas guardadas con nombre; se usan como si fueran tablas)
-- =====================================================================

-- Recetas con cuántas veces se guardaron en favoritos y cuántas se vieron.
-- La usa GET /api/admin/reporte para el top de recetas.
DROP VIEW IF EXISTS vista_recetas_populares;
CREATE VIEW vista_recetas_populares AS
SELECT
    recetas.id,
    recetas.nombre,
    recetas.categoria,
    (SELECT COUNT(*) FROM favoritos WHERE favoritos.receta_id = recetas.id) AS veces_favorita,
    (SELECT COUNT(*) FROM historial WHERE historial.receta_id = recetas.id) AS veces_vista
FROM recetas;


-- Propuestas que todavía no revisa el admin, con el nombre de quien la propuso.
-- La usa GET /api/admin/propuestas.
DROP VIEW IF EXISTS vista_propuestas_pendientes;
CREATE VIEW vista_propuestas_pendientes AS
SELECT
    recetas_propuestas.id,
    recetas_propuestas.usuario_id,
    usuarios.nombre AS usuario,
    recetas_propuestas.nombre,
    recetas_propuestas.descripcion,
    recetas_propuestas.creado_en
FROM recetas_propuestas
JOIN usuarios ON usuarios.id = recetas_propuestas.usuario_id
WHERE recetas_propuestas.estado = 'pendiente';


-- Un resumen de cada usuario: cuánto tiene en despensa, favoritos y plan.
-- La usa GET /api/admin/reporte.
DROP VIEW IF EXISTS vista_resumen_usuarios;
CREATE VIEW vista_resumen_usuarios AS
SELECT
    usuarios.id,
    usuarios.nombre,
    usuarios.correo,
    usuarios.rol,
    (SELECT COUNT(*) FROM despensa WHERE despensa.usuario_id = usuarios.id) AS en_despensa,
    (SELECT COUNT(*) FROM favoritos WHERE favoritos.usuario_id = usuarios.id) AS favoritos,
    (SELECT COUNT(*) FROM plan_semanal WHERE plan_semanal.usuario_id = usuarios.id) AS en_plan
FROM usuarios;


-- =====================================================================
-- 2. FUNCIÓN: siguiente id para una receta nueva
-- =====================================================================

-- Las recetas del archivo usan "gt-0001", "gt-0002"...
-- Las que crea el admin usan "nu-0001", "nu-0002"... para no chocar.
-- Uso:  SELECT siguiente_id_receta();   ->  'nu-0003'
DROP FUNCTION IF EXISTS siguiente_id_receta();
CREATE FUNCTION siguiente_id_receta() RETURNS VARCHAR AS $$
DECLARE
    ultimo INTEGER;
BEGIN
    SELECT COALESCE(MAX(CAST(SUBSTRING(id FROM 4) AS INTEGER)), 0)
    INTO ultimo
    FROM recetas
    WHERE id LIKE 'nu-%';

    RETURN 'nu-' || LPAD(CAST(ultimo + 1 AS VARCHAR), 4, '0');
END;
$$ LANGUAGE plpgsql;


-- =====================================================================
-- 3. PROCEDIMIENTOS ALMACENADOS
-- =====================================================================

-- Borra una receta y todo lo que depende de ella (ingredientes, pasos,
-- favoritos, historial y plan). Sin esto la base no deja borrarla.
-- Uso:  CALL borrar_receta('nu-0001');
DROP PROCEDURE IF EXISTS borrar_receta(VARCHAR);
CREATE PROCEDURE borrar_receta(p_receta_id VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM receta_ingredientes WHERE receta_id = p_receta_id;
    DELETE FROM pasos WHERE receta_id = p_receta_id;
    DELETE FROM favoritos WHERE receta_id = p_receta_id;
    DELETE FROM historial WHERE receta_id = p_receta_id;
    DELETE FROM plan_semanal WHERE receta_id = p_receta_id;
    DELETE FROM recetas WHERE id = p_receta_id;
END;
$$;


-- Revisa una propuesta: la marca como aprobada o rechazada y lo anota
-- en la bitácora. Uso:
--   CALL revisar_propuesta(3, 'aprobada', NULL, 1);
--   CALL revisar_propuesta(4, 'rechazada', 'Le faltan los pasos', 1);
DROP PROCEDURE IF EXISTS revisar_propuesta(INTEGER, VARCHAR, TEXT, INTEGER);
CREATE PROCEDURE revisar_propuesta(
    p_propuesta_id INTEGER,
    p_estado VARCHAR,
    p_motivo TEXT,
    p_admin_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE recetas_propuestas
    SET estado = p_estado, motivo_rechazo = p_motivo
    WHERE id = p_propuesta_id;

    INSERT INTO bitacora (usuario_id, accion)
    VALUES (p_admin_id, 'Propuesta ' || p_propuesta_id || ' ' || p_estado);
END;
$$;
