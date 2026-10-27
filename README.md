# US Data Centers Analytics

**An end-to-end geospatial data analytics pipeline exploring the distribution of data centers across the United States.**

## Overview

Where are US data centers located, and what factors might explain their geographical concentration?

This project aims to build a reproducible data pipeline to collect, validate, transform, store and analyze data center records across the United States. It combines data engineering, exploratory data analysis and geospatial analytics to turn raw data into actionable insights.

The project also explores the infrastructure and environmental implications of data center development, including electricity demand, water resources, population density and access to digital infrastructure, as data availability permits.

### Objectives

- Build a reproducible Python data processing pipeline.
- Assess data quality and document missing or inconsistent values.
- Store raw and processed data in PostgreSQL.
- Use PostGIS to create and query spatial geometries.
- Analyze the geographical distribution of data centers by US state.
- Produce reusable datasets for maps, dashboards and further analysis.
- Implement unit and integration tests to improve reliability.
- Document limitations and avoid drawing conclusions unsupported by the data.

## Tech stack

| Technology | Purpose |
|---|---|
| Python | Pipeline orchestration and data processing |
| Pandas | Data cleaning and analysis |
| SQLAlchemy | Database connectivity |
| PostgreSQL | Relational data storage |
| PostGIS | Spatial data storage and queries |
| GeoPandas | Geospatial analysis |
| pytest | Unit and integration testing |
| Docker | Local database environment |
| Git and GitHub | Version control and project documentation |

## Project architecture

The pipeline separates raw source data from processed analytical data.

```text
Source CSV
   |
   v
Python ingestion
   |
   v
PostgreSQL: staging
   |
   | Data quality checks
   | Type conversion and cleaning
   | Geometry creation
   v
PostgreSQL: processed
   |
   +--> SQL analysis by state
   |
   +--> Geospatial analysis
   |
   +--> CSV exports
           |
           v
     Maps and dashboards
```

### Repository structure

```text
us-data-centers-analytics/
├── data/
│   └── README.md
├── docs/
├── notebooks/
├── outputs/
│   └── analysis/
├── scripts/
│   ├── check_staging.py
│   ├── create_processed_table.py
│   ├── verify_processed.py
│   └── analyze_by_state.py
├── sql/
│   └── 02_create_processed_table.sql
├── src/
│   └── datacenter_usa/
│       ├── database.py
│       └── loader.py
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

The structure may evolve as new pipeline stages, tests and analyses are added.

## Getting started

### 1. Clone the repository

Replace `YOUR_GITHUB_USERNAME` with the GitHub account that hosts this repository.

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/us-data-centers-analytics.git
cd us-data-centers-analytics
```

If the repository has a different name or URL, use its actual clone URL.

### 2. Create a Python virtual environment

Python 3.12 or a compatible version supported by the project dependencies is recommended.

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

Install the project dependencies using the method configured in `pyproject.toml`. For example, if the project is installable:

```powershell
python -m pip install -e .
```

Install pytest if it is not already included in the development dependencies:

```powershell
python -m pip install pytest
```

### 3. Configure environment variables

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Configure the database variables locally:

```dotenv
POSTGRES_DB=datacenter
POSTGRES_USER=datacenter
POSTGRES_PASSWORD=replace_with_a_local_password
DATABASE_URL=postgresql+psycopg://datacenter:replace_with_a_local_password@localhost:5433/datacenter
```

These values are examples for a local development environment. Use your own password and ensure the connection URL matches your actual database configuration.

**Never commit `.env` or publish database credentials.**

### 4. Start PostgreSQL and PostGIS

Docker provides a reproducible way to run PostgreSQL with PostGIS locally.

If the container has not already been created, run the following PowerShell command from the project root:

```powershell
docker run --name datacenter_postgis `
  --env-file .env `
  -p 127.0.0.1:5433:5432 `
  -d postgis/postgis:16-3.5
```

The `.env` file must contain `POSTGRES_DB`, `POSTGRES_USER` and `POSTGRES_PASSWORD`. Additional variables, such as `DATABASE_URL`, are not used by the PostgreSQL image to initialize the database.

The host port is `5433`, mapped to container port `5432`. This avoids conflicts when another PostgreSQL service already uses port `5432`.

Check the container status:

```powershell
docker ps
docker logs datacenter_postgis
```

Start an existing stopped container:

```powershell
docker start datacenter_postgis
```

Stop it when finished:

```powershell
docker stop datacenter_postgis
```

The PostGIS image provides PostgreSQL with the PostGIS extension available. The project enables the extension in the database when required.

### 5. Prepare the source data

The pipeline currently uses the PNNL Atlas CSV file, `pnnl_atlas_records.csv`.

Obtain the source data from its original provider and follow the applicable usage and attribution requirements. Do not assume the dataset is included in the repository.

The current ingestion command expects the file at `..\pnnl_atlas_records.csv` relative to the project root. Place the file there, or update the script to point to its actual location before running the pipeline.

Keep raw datasets out of Git unless redistribution is explicitly permitted. A `data/README.md` file can document the source, download instructions, date retrieved, license and expected file location without storing the dataset itself.

## Running the pipeline

Run commands from the repository root.

In PowerShell, configure the Python import path:

```powershell
$env:PYTHONPATH = "$PWD\src"
```

### 1. Load raw data into PostgreSQL

```powershell
python -c "from datacenter_usa.database import get_engine; from datacenter_usa.loader import load_csv_to_staging; engine = get_engine(); print('Rows loaded:', load_csv_to_staging('..\pnnl_atlas_records.csv', engine)); engine.dispose()"
```

The loader stores source columns as text in `staging.pnnl_atlas_records`. This staging layer preserves raw values before type conversion.

The loader intentionally fails if the destination table already exists. This helps prevent accidental overwrites. For subsequent runs, implement an explicit reload or migration strategy rather than dropping tables blindly.

### 2. Run data quality checks

```powershell
python scripts/check_staging.py
```

The checks cover missing or duplicated identifiers, coordinate validity, missing fields and surface values.

The current source snapshot contains 1,237 records. Earlier checks found no missing or duplicate IDs and no invalid coordinates, but `operator` and `name` contain missing values. These are retained rather than automatically dropping affected records.

### 3. Create the processed PostGIS table

```powershell
python scripts/create_processed_table.py
```

This step creates `processed.data_centers`, converts numeric fields and constructs spatial points using longitude and latitude in EPSG:4326.

The SQL script is intended for initial table creation. If the table already exists, review the schema and use a deliberate migration or rebuild procedure rather than deleting data without a backup.

### 4. Verify the processed table

```powershell
python scripts/verify_processed.py
```

The verification checks row counts, unique IDs, missing geometries, geometry validity and spatial reference identifiers.

### 5. Analyze data centers by state

```powershell
python scripts/analyze_by_state.py
```

The analysis produces a state-level summary, including the number of records, percentage of the dataset, aggregated surface area, median surface area and number of records with a known operator.

The output is written to:

```text
outputs/analysis/data_centers_by_state.csv
```

This file can be used in Pandas, GeoPandas, Power BI or other visualization tools.

## Testing

Testing is an essential part of the pipeline: it helps detect regressions and makes data transformations easier to trust.

### Run unit tests

Unit tests check individual functions without requiring a live database when their dependencies are mocked.

```powershell
$env:PYTHONPATH = "$PWD\src"
python -m pytest tests/unit -v
```

### Run PostgreSQL/PostGIS integration tests

Integration tests connect to the configured database and validate the real schema, spatial extension, record counts and geometry consistency.

Make sure the database is running and the processed table has been created before executing:

```powershell
python -m pytest tests/integration -v -m integration
```

### Run the complete test suite

```powershell
python -m pytest -v
```

The full suite may require a working PostgreSQL/PostGIS connection for integration tests. Use a dedicated test database for destructive tests or future tests that modify database contents.

## Initial data quality findings

The current dataset snapshot contains 1,237 records.

| Check | Result |
|---|---:|
| Total source records | 1,237 |
| Missing IDs | 0 |
| Duplicate ID values | 0 |
| Invalid coordinates | 0 |
| Missing state values | 0 |
| Missing county values | 0 |
| Missing operator values | 412 |
| Missing name values | 252 |
| Invalid surface values | 0 |
| Negative surface values | 0 |
| Zero surface values | 0 |

These findings describe the current source snapshot and should be recalculated whenever the source data changes.

Valid numerical coordinates do not guarantee positional accuracy, and a complete surface value does not establish that the measurement is comparable across all sites.

## Security and data protection

Security applies to configuration, source data, database access and test execution.

### Environment variables and secrets

- Never commit `.env`, passwords, API tokens or connection strings containing credentials.
- Commit `.env.example` with placeholder values only.
- Avoid printing secrets in logs, terminal output, notebooks or CI logs.
- Do not embed credentials directly in Python files, SQL scripts or notebooks.
- Rotate credentials immediately if they are accidentally exposed.

### Git hygiene

A suitable `.gitignore` should include at least:

```gitignore
# Secrets and local configuration
.env
.env.*
!.env.example

# Python
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/

# Local data and generated outputs
data/raw/
data/processed/
outputs/
*.csv

# Local tooling
.vscode/
.idea/
```

Adjust the data and output rules if specific non-sensitive artifacts are intentionally versioned. For example, small curated sample datasets or selected portfolio figures may be committed when licensing and privacy requirements permit.

Before publishing the repository, inspect tracked files:

```powershell
git status --short
git ls-files
```

If a secret was committed previously, adding it to `.gitignore` is not enough. Remove it from version control, rotate it, and assess whether Git history needs to be cleaned.

### Database security

- Bind development database ports to localhost rather than exposing them publicly.
- Use strong, unique passwords.
- Grant database users only the permissions they need.
- Keep production and test databases separate.
- Avoid destructive SQL operations against a shared database.
- Keep backups before schema migrations or data reloads.

### Testing safety

- Use mocked dependencies for unit tests where practical.
- Keep integration tests focused on the intended test database.
- Avoid embedding real credentials in tests.
- Make data loading and table creation behavior explicit.
- Verify expected row counts and constraints after every pipeline stage.

## Analytical limitations

The results represent the source dataset, not necessarily a complete census of all US data centers.

Missing operator and name values may affect grouping and entity identification. Counts and surface totals should therefore be interpreted in the context of source coverage, definitions and collection methods.

Geographical concentration is descriptive rather than causal. Further analysis would be needed to investigate potential explanatory variables such as electricity prices, network connectivity, population density, climate, water stress and infrastructure availability.

## Roadmap

- [x] Import raw CSV records into PostgreSQL staging.
- [x] Implement initial data quality checks.
- [x] Create a typed PostGIS table.
- [ ] Expand PostgreSQL/PostGIS integration test coverage.
- [ ] Analyze data center distribution by state.
- [ ] Produce a ranked bar chart and a US state choropleth map.
- [ ] Integrate state-level population, electricity and climate datasets.
- [ ] Investigate water stress and environmental impacts.
- [ ] Add automated pipeline execution and continuous integration.
- [ ] Publish documented findings and visualizations.

## Author

* [Hugues](https://github.com/gouttebroze), Data Analyst and musician, focused on Java, Python, SQL, data analytics, IA and DevOps.

