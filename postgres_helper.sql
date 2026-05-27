
-- Función helper para emular GROUP_CONCAT en PostgreSQL
-- Ejecutar en la base de datos PostgreSQL una sola vez

CREATE OR REPLACE FUNCTION group_concat(text, text)
RETURNS text AS $$
    SELECT string_agg($1, $2)
$$ LANGUAGE sql IMMUTABLE;

CREATE AGGREGATE group_concat(text) (
    SFUNC = textcat,
    STYPE = text,
    INITCOND = ''
);

-- Nota: Recomendamos usar STRING_AGG directamente en el código
-- Esta función es solo para compatibilidad temporal
