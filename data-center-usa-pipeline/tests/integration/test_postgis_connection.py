"""Integration tests; opt in with RUN_DB_INTEGRATION=1 after starting PostGIS."""

import os
import uuid

import pandas as pd
import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skipif(
    os.getenv("RUN_DB_INTEGRATION") != "1",
    reason="Définir RUN_DB_INTEGRATION=1 pour tester une vraie instance PostGIS",
)
def test_postgis_round_trip():
    pytest.importorskip("sqlalchemy")
    from datacenter_usa.database import (
        count_data_centers,
        create_database_engine,
        postgis_healthcheck,
        read_data_centers,
        write_data_centers,
    )
    from sqlalchemy import text

    engine = create_database_engine()
    site_id = f"test-{uuid.uuid4()}"
    frame = pd.DataFrame(
        {
            "id": [site_id],
            "state": ["Test State"],
            "state_abb": ["ZZ"],
            "county": ["Integration County"],
            "operator": [None],
            "name": ["PostGIS test record"],
            "sqft": [100.0],
            "lat": [40.0],
            "lon": [-100.0],
        }
    )

    try:
        info = postgis_healthcheck(engine)
        assert info["database"]
        assert "POSTGIS" in info["postgis_version"].upper()

        written = write_data_centers(frame, engine)
        assert written == 1
        assert count_data_centers(engine, site_id=site_id) == 1

        result = read_data_centers(engine, site_id=site_id)
        assert len(result) == 1
        assert result.loc[0, "site_id"] == site_id
        assert result.loc[0, "geometry_wkt"] == "POINT(-100 40)"
    finally:
        with engine.begin() as connection:
            connection.execute(
                text("DELETE FROM staging.data_centers WHERE site_id = :site_id"),
                {"site_id": site_id},
            )
        engine.dispose()
