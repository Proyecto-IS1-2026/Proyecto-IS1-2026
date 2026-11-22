GRANT CONNECT ON DATABASE proyecto_is1_2026 TO is1_app;

GRANT USAGE, CREATE ON SCHEMA is1 TO is1_app;

SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'is1'
ORDER BY table_name;