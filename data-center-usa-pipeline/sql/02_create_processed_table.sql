
-- Créer le schéma de données préparées.
CREATE SCHEMA IF NOT EXISTS processed;

-- Activer PostGIS si nécessaire.
CREATE EXTENSION IF NOT EXISTS postgis;

-- Créer la table préparée à partir des données brutes.
CREATE TABLE processed.data_centers AS
WITH cleaned AS (
    SELECT
        NULLIF(BTRIM(id), '') AS id,
        NULLIF(BTRIM(state), '') AS state,
        NULLIF(BTRIM(state_abb), '') AS state_abb,
        NULLIF(BTRIM(county), '') AS county,
        NULLIF(BTRIM(operator), '') AS operator,
        NULLIF(BTRIM(name), '') AS name,
        BTRIM(sqft)::NUMERIC AS sqft,
        BTRIM(lat)::DOUBLE PRECISION AS lat,
        BTRIM(lon)::DOUBLE PRECISION AS lon
    FROM staging.pnnl_atlas_records
)
SELECT
    id,
    state,
    state_abb,
    county,
    operator,
    name,
    sqft,
    lat,
    lon,
    ST_SetSRID(
        ST_MakePoint(lon, lat),
        4326
    )::geometry(Point, 4326) AS geom
FROM cleaned;

-- Contraintes d'intégrité.
ALTER TABLE processed.data_centers
    ALTER COLUMN id SET NOT NULL,
    ALTER COLUMN lat SET NOT NULL,
    ALTER COLUMN lon SET NOT NULL,
    ALTER COLUMN sqft SET NOT NULL;

ALTER TABLE processed.data_centers
    ADD CONSTRAINT data_centers_pkey PRIMARY KEY (id);

ALTER TABLE processed.data_centers
    ADD CONSTRAINT data_centers_lat_range
    CHECK (lat BETWEEN -90 AND 90);

ALTER TABLE processed.data_centers
    ADD CONSTRAINT data_centers_lon_range
    CHECK (lon BETWEEN -180 AND 180);

ALTER TABLE processed.data_centers
    ADD CONSTRAINT data_centers_sqft_nonnegative
    CHECK (sqft >= 0);

-- Index pour les recherches géographiques.
CREATE INDEX data_centers_geom_gix
    ON processed.data_centers
    USING GIST (geom);

-- Index utile pour les regroupements par État.
CREATE INDEX data_centers_state_idx
    ON processed.data_centers (state_abb);

ANALYZE processed.data_centers;
