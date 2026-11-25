GRANT CONNECT ON DATABASE proyecto_is1_2026 TO is1_app;

GRANT USAGE, CREATE ON SCHEMA is1 TO is1_app;

INSERT INTO
    is1.etiqueta (id, nombre)
SELECT gen_random_uuid (), e.nombre
FROM (
        VALUES ('Python'), ('SQL'), ('Flask'), ('PostgreSQL'), ('Otros'), ('C')
    ) AS e (nombre)
WHERE
    NOT EXISTS (
        SELECT 1
        FROM is1.etiqueta
        WHERE
            nombre = e.nombre
    );

SELECT table_name
FROM information_schema.tables
WHERE
    table_schema = 'is1'
ORDER BY table_name;

SELECT nombre, email, rol FROM is1.autor JOIN is1.usuario USING (id);

SELECT id, nombre FROM is1.etiqueta ORDER BY nombre;

SELECT p.titulo, e.nombre AS etiqueta
FROM is1.pregunta p
    JOIN is1.pregunta_etiqueta pe ON p.id = pe.pregunta_id
    JOIN is1.etiqueta e ON e.id = pe.etiqueta_id;

BEGIN;

WITH
    etiquetas AS (
        SELECT id, FIRST_VALUE(id) OVER (
                PARTITION BY
                    nombre
                ORDER BY id
            ) AS id_correcto
        FROM is1.etiqueta
    )
INSERT INTO
    is1.pregunta_etiqueta (pregunta_id, etiqueta_id)
SELECT DISTINCT
    pe.pregunta_id,
    e.id_correcto
FROM is1.pregunta_etiqueta pe
    JOIN etiquetas e ON pe.etiqueta_id = e.id
WHERE
    e.id <> e.id_correcto ON CONFLICT (pregunta_id, etiqueta_id) DO NOTHING;

WITH
    duplicadas AS (
        SELECT id, ROW_NUMBER() OVER (
                PARTITION BY
                    nombre
                ORDER BY id
            ) AS numero
        FROM is1.etiqueta
    )
DELETE FROM is1.pregunta_etiqueta pe USING duplicadas d
WHERE
    pe.etiqueta_id = d.id
    AND d.numero > 1;

WITH
    duplicadas AS (
        SELECT id, ROW_NUMBER() OVER (
                PARTITION BY
                    nombre
                ORDER BY id
            ) AS numero
        FROM is1.etiqueta
    )
DELETE FROM is1.etiqueta e USING duplicadas d
WHERE
    e.id = d.id
    AND d.numero > 1;

COMMIT;

SELECT nombre, COUNT(*) AS cantidad
FROM is1.etiqueta
GROUP BY
    nombre
HAVING
    COUNT(*) > 1;