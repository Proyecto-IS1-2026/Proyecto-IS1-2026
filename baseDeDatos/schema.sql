
GRANT CONNECT ON DATABASE proyecto_is1_2026 TO is1_app;

GRANT USAGE, CREATE ON SCHEMA is1 TO is1_app;

INSERT INTO is1.categoria (id, nombre, descrip)
SELECT gen_random_uuid(), c.nombre, c.descrip
FROM (
    VALUES
        ('Python', 'Preguntas sobre Python'),
        ('SQL', 'Preguntas sobre SQL'),
        ('Flask', 'Preguntas sobre Flask'),
        ('PostgreSQL', 'Preguntas sobre PostgreSQL'),
        ('Otros', 'Preguntas de otros temas'),
        ('C', 'Preguntas sobre lenguaje C')
) AS c(nombre, descrip)
WHERE NOT EXISTS (
    SELECT 1
    FROM is1.categoria
    WHERE nombre = c.nombre
);

INSERT INTO is1.etiqueta (id, nombre)
SELECT gen_random_uuid(), e.nombre
FROM (
    VALUES
        ('Python'),
        ('SQL'),
        ('Flask'),
        ('PostgreSQL'),
        ('Otros'),
        ('C')
) AS e(nombre)
WHERE NOT EXISTS (
    SELECT 1
    FROM is1.etiqueta
    WHERE nombre = e.nombre
);

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'is1'
ORDER BY table_name;

SELECT nombre, email, rol
FROM is1.autor
JOIN is1.usuario USING (id);

SELECT id, nombre, descrip
FROM is1.categoria
ORDER BY nombre;

SELECT id, nombre
FROM is1.etiqueta
ORDER BY nombre;

SELECT p.titulo, c.nombre AS categoria
FROM is1.pregunta p
JOIN is1.categoria c
    ON p.categoria_id = c.id;

SELECT p.titulo, e.nombre AS etiqueta
FROM is1.pregunta p
JOIN is1.pregunta_etiqueta pe
    ON p.id = pe.pregunta_id
JOIN is1.etiqueta e
    ON e.id = pe.etiqueta_id;

SELECT nombre, COUNT(*) AS cantidad
FROM is1.categoria
GROUP BY nombre
HAVING COUNT(*) > 1;

SELECT nombre, COUNT(*) AS cantidad
FROM is1.etiqueta
GROUP BY nombre
HAVING COUNT(*) > 1;

SELECT id, nombre, descrip
FROM is1.categoria
ORDER BY nombre;

SELECT
    p.titulo AS pregunta,
    r.cuerpo AS respuesta,
    a.nombre AS autor
FROM is1.respuesta r
JOIN is1.pregunta p ON r.pregunta_id = p.id
JOIN is1.autor a ON r.autor_id = a.id;








