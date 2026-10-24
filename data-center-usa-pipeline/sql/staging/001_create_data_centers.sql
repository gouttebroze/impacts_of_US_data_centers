CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS staging.data_centers (
    site_id TEXT PRIMARY KEY CHECK (length(trim(site_id)) > 0),
    source_layer TEXT,
    state_name TEXT,
    state_abbr TEXT,
    county_name TEXT,
    operator TEXT,
    site_name TEXT,
    area_sqft DOUBLE PRECISION CHECK (area_sqft IS NULL OR area_sqft >= 0),
    latitude DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    geom geometry(Point, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_data_centers_geom
    ON staging.data_centers USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_data_centers_state_abbr
    ON staging.data_centers (state_abbr);

CREATE INDEX IF NOT EXISTS idx_data_centers_county_name
    ON staging.data_centers (county_name);
