-- Vistas, función y procedimientos almacenados
-- Responsable: David
--
-- Correr en pgAdmin después de crear_tablas.sql. Se puede correr varias veces.


-- VISTAS

-- Cuántas veces se guardó en favoritos y cuántas se vio cada receta
DROP VIEW IF EXISTS vista_recetas_populares;
CREATE VIEW vista_recetas_populares AS
SELECT
    recetas.id,
    recetas.nombre,
    recetas.categoria,
    (SELECT COUNT(*) FROM favoritos WHERE favoritos.receta_id = recetas.id) AS veces_favorita,
    (SELECT COUNT(*) FROM historial WHERE historial.receta_id = recetas.id) AS veces_vista
FROM recetas;


-- Propuestas pendientes, con el nombre de quien la propuso
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


-- Resumen de cada usuario: despensa, favoritos y plan
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


-- FUNCIÓN

-- Siguiente id para una receta creada por el admin: nu-0001, nu-0002...
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


-- PROCEDIMIENTOS

-- Borra una receta y todo lo que depende de ella.  CALL borrar_receta('nu-0001');
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


-- Aprueba o rechaza una propuesta y lo anota en la bitácora.
-- CALL revisar_propuesta(4, 'rechazada', 'Le faltan los pasos', 1);
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
