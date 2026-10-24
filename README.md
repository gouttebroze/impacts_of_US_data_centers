# Analyse de données des Data Centers aux États-Unis 

+ **auteur**: Hugues GOUTTEBROZE 
+ **année**: 2026
 
+ **URL code source** sur Github: 
    - vers branche principale [main](https://github.com/gouttebroze/impacts_of_US_data_centers)

+ Projet en cours de progression -  **analyses de données géospatiales** sur la répartition des Data Centers, sur le territoires des Etats-Unis: 
    - *croiser les data centers avec les comtés américains*
    - puis, avancer sur l'analyse des **données**: 
        + *liées à l'énergie (électricité, eau)*
        + *liées à la **population***
        + *liées au **stress hydrique***.

## Dernières progressions sur le projet

* une connexion **Python–PostgreSQL** fonctionnelle, avec l'extention **PostGIS** (toute la chaîne de connexion est validée):
    - **PostGIS** v3.5.2 (extension PostgreSQL active, création des géométries en EPSG:4326)
    - **Python** (**SQLAlchemy** et **psycopg** fonctionnent ensemble).
    - **Docker** (le conteneur est opérationnel sur le port hôte 5433).

* projet possède désormais une base de données géospatiale (ne se limite plus aux CSVs et notebooks)

* création d'une table typée et exploitable pour les analyses SQL et géospatiales

* contrôle de la qualité des données importées avant de les nettoyer, génération d'un rapport 

* ajout de tests unitaires & écriture des premiers tests d'intégration 

+ la pipeline à été renforcer sur ces points:

    1. le contrôle de l'intégrité des données: identifiants dupliqués, champs vides et coordonnées manquantes ou invalides.

    2. Séparation entre staging et données préparées ( permet de conserver la table brute et d'appliquer le nettoyage dans une nouvelle table).

    3. Créer les géométries PostGIS à partir des coordonnées latitude/longitude, avec le système de référence adapté (EPSG:4326).

+ **Issues en cours / à faire**:

    * **MAJ** documentations (synthétiser, simplifier, organiser), ``README.md`` et des **fichiers de documentation**, situés ds le dossier [./docs](./data-center-usa-pipeline/docs/), 

## Lancer le projet

```bash
git clone https://github.com/YOUR_USERNAME/data-center-usa-pipeline.git
cd data-center-usa-pipeline

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

# suppression notebook avec refactoring vers une pipeline
# jupyter notebook
```

# Architecture

- **refactoring** terminé (reprise des *fonction du notebooks* pour les rendre **génériques**, créer une architecture avec une pipeline d'analyse des données automatisée)

## Refactoring

* **Étape 1**

    * Nettoyer et organiser le dépôt

        * *Identifier le notebook de référence, supprimer les doublons seulement après validation, organiser les dossiers.*

* **Étape 2**

    *Extraire normalize_columns() et extract_coordinates() dans cleaning.py.

* Étape 3

Écrire les tests pytest : coordonnées valides, valeurs manquantes, colonnes absentes, formats incorrects.

* Étape 4

Créer le premier pipeline d'ingestion et de qualité, avec sauvegarde des données brutes.

* Étape 5

Reproduire les premiers KPI du notebook initial avec les nouvelles fonctions et comparer les résultats.

* Étape 6

Ajouter PostgreSQL/PostGIS, puis les données complémentaires.

+ **Une règle à appliquer**

    - *À chaque refactoring, nous vérifierons que les nouveaux résultats correspondent aux anciens lorsque la logique métier n'a pas changé, permettant une première forme de **test de non-régression**, en complément des **tests unitaires***.

### Structure globale du projet

```
impacts_of_US_data_centers/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── data-center-usa-pipeline/
│   │
│   ├── data/
│   │   ├── raw/
│   │   ├── interim/
│   │   └── processed/
│   │
│   ├── src/
│   │   └── datacenter_usa/
│   │       ├── __init__.py
│   │       ├── ingestion.py
│   │       ├── cleaning.py
│   │       ├── quality.py
│   │       ├── indicators.py
│   │       └── geo.py
│   │
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_data_quality.ipynb
│   │   └── 03_concentration_analysis.ipynb
│   │
│   ├── sql/
│   │   ├── staging/
│   │   └── analytics/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   │
│   ├── outputs/
│   │   ├── figures/
│   │   └── tables/
│   │
│   └── docs/
│       ├── methodology.md
│       ├── data_dictionary.md
│       └── testing_strategy.md
│
└── data_center_usa_portfolio.ipynb
```

### Lancenemt pipeline automatisée

* **se plasser dans le dossier** [data-center-usa-pipeline](./data-center-usa-pipeline/), qui contient le pipeline

* **Automatisation des étapes suivantes:**

1. **Ingestion**

    * ``load_csv()``

2. **Nettoyage**

    * ``normalize_columns()`` et ``extract_coordinates()``

3. **Validation**

    * Schéma, coordonnées, doublons et valeurs manquantes

4. **Résultats**

    * DataFrame préparé 
    * rapport qualité 
    * résumé JSON

* Ecriture du CODE: rester le plus simple possible, un code lisible, classes et fonctions génériques, indépendantes et réutilisable  
* Isolation des tests unitaires.

### Exécuter les tests (sous Windows)

* à la racine de [data-center-usa-pipeline](./data-center-usa-pipeline/) :

```sh
# lancement de l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# MAJ packages
python -m pip install -e ".[dev]" # Successfully installed datacenter-usa-0.1.0

# lancement des tests unitaires
python -m pytest -v # 39 passed
```

### 5. Lancement du pipeline sur CSV réel

* script de lancement sous powershell (recherche ``pnnl_atlas_records.csv`` à la racine du dépôt):

```sh
python scripts/validate_local_pipeline.py
```

* exécution du pipeline sur le snapshot CSV disponible : 

    - **traitement**: 1 237 lignes, 44 États, sans doublon de ligne ni d’identifiant, et avec 1 237 coordonnées numériquement valides. 
    - **rapport qualité**: 412 valeurs manquantes dans *operator* et 252 dans *name*.

* résultats exportés dans [`outputs/tables`](./data-center-usa-pipeline/outputs/tables/):

```
outputs/
└── tables/
    ├── data_quality_report.csv
    ├── data_centers_prepared.csv
    └── pipeline_summary.json
```

* **Attention** : *les coordonnées sont contrôlées selon leurs limites numériques, il faudra vérifier spatialement que chaque point se trouve bien aux États-Unis ou dans l’État qui lui est attribué*.

## Vers PostgreSQL et PostGIS

### Ajout & Installation de Dependences

```toml
db = [
    "SQLAlchemy>=2.0",
    "psycopg[binary]>=3.2",
    "python-dotenv>=1.0",
]
```
* lancement des scripts
```sh
# lancement env. virtuel py
.\.venv\Scripts\Activate.ps1

# installation dependences
python -m pip install -e ".[dev,db]"
```

* [SQLAlchemy](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html?utm_source=chatgpt.com) assurera la connexion entre Python et PostgreSQL.

* l'URL de connexion utilisée est au format ``postgresql+psycopg``(voir doc. de [SQLAlchemy](https://docs.sqlalchemy.org/en/21/dialects/postgresql.html?utm_source=chatgpt.com)) 

### Démarrage de la base PostGIS

* verifier la version de `docker`

* création du fichier ``docker-compose.postgis.yml``, basé sur l'image officielle ``postgis/postgis`` (voir site [Hub Docker Image](https://hub.docker.com/r/postgis/postgis?utm_source=chatgpt.com))

* lancer les scripts suivants pr démarrer `docker postgis`
```sh
docker compose --env-file .env -f docker-compose.postgis.yml up -d

docker compose --env-file .env -f docker-compose.postgis.yml ps 
```
* Le conteneur ``datacenter_postgis`` affiche un état **Up** ou **Running**

## Suite du pipeline

1. Préparer PostgreSQL/PostGIS

    - Créer un schéma de staging pour accueillir les données brutes importées.

2. Charger les data centers

    - Importer le`` CSV PNNL`` dans ``PostgreSQL`` sans perdre les données utiles ni masquer les anomalies.

3. Tester l'import

    - Vérifier le nombre de lignes, les colonnes, les identifiants, les coordonnées et les valeurs manquantes.

4. Exploiter les données géographiques

    - Créer les géométries ``PostGIS`` et préparer les jointures spatiales avec les données des comtés américains.

### Connexion Python à PostgreSQL

#### Dépendances nécessaires

- ``SQLAlchemy`` pour **gérer les connexions** et **exécuter les requêtes**.
- ``psycopg`` pour **communiquer** avec ``PostgreSQL``.
- ``python-dotenv`` pour **lire** les variables de ``.env``.
- ``pandas`` pour **lire** et **contrôler** le **CSV**.

* Pas d'ajoute de dépendances, on réutilise celles déjà déclarées dans le fihier ``pyproject.toml``.

### Étape 1 — Vérification de la configuration de connexion

* On vérifie que: 
    - l'URL de connexion utilise bien le port 5433  
    - l'environnement virtuel est actif

    ```sh
    .\.venv\Scripts\Activate.ps1
    ```

* Puis 
```sh
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('DATABASE_URL définie :', bool(os.getenv('DATABASE_URL')))"
```

* résultat attendu:
```sh
DATABASE_URL définie : True
```

### Étape 2 — On érifie que les bibliothèques sont installées

```sh
python -c "import sqlalchemy, psycopg, pandas, dotenv; print('SQLAlchemy :', sqlalchemy.__version__); print('psycopg :', psycopg.__version__); print('pandas :', pandas.__version__); print('Dépendances OK')"
```
* **OK** si retourne la liste des versions des bibliothèques et Dépendances attendues

```sh```
```sh```
### Étape 3 — Création

+ Ds ``src/datacenter_usa/database.py``, on implémente une fonction ``get_engine()`` qui:

1. récupère ``DATABASE_URL`` depuis l'environnement
2. utilise le pilote ``psycopg v3``
3. crée un moteur ``SQLAlchemy`` 
4. vérifie la configuration

```py
"""Database connection helpers for the data center pipeline."""
import os
from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine

def get_engine() -> Engine:
    """Create a SQLAlchemy engine using DATABASE_URL.

    Returns:
        Engine: SQLAlchemy engine configured for PostgreSQL.

    Raises:
        RuntimeError: If DATABASE_URL is missing.
    """
    load_dotenv()

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is missing. Check your .env configuration."
        )

    return create_engine(database_url, pool_pre_ping=True)
```
* ``get_engine()`` centralise la connexion dans un seul module.
* ``pool_pre_ping=True`` aide à détecter les connexions périmées.
* Le moteur ``SQLAlchemy`` est créé sans ouvrir immédiatement de connexion.

### Étape 2 — Tester la connexion réelle

* on exécute cette commande ds PowerShell, (.venv activé):
```sh
$env:PYTHONPATH = "$PWD\src"
python -c "from datacenter_usa.database import get_engine; engine = get_engine(); conn = engine.connect(); print('Connexion PostgreSQL : OK'); print(conn.exec_driver_sql('SELECT current_database(), current_user').one()); print(conn.exec_driver_sql('SELECT PostGIS_Full_Version()').scalar()); conn.close(); engine.dispose()"
```

* la cmd vérifie que:
    1. ``Python`` trouve ton module
    2. ``DATABASE_URL`` permet de se connecter
    3. ``PostgreSQL`` répond 
    4. ``PostGIS`` est disponible

* si tt fonctionne, la cmd retourne: ``"Connexion PostgreSQL : OK"``, suivi des **EXTENTIONS PostgreSQL** (nom et version) dont l'**EXTENTION PostGIS**.

### Étape 3 — On importe le CSV

* On crée ``loader.py`` pour importer ``..\pnnl_atlas_records.csv`` dans ``staging.pnnl_atlas_records``, en préservant les **colonnes sources** et en évitant les **transformations silencieuses**.

* On ajoute des **tests unitaires** pour le **chargement** et des **contrôles d'intégration** pour **comparer** le nombre de **lignes importées** avec celui du **CSV**.

## Création du rapport de qualité des données

* On commence par un contrôle direct sur les données en base.

* Création fichier ``scripts/check_staging.py``:
```py
"""Run data quality checks on the raw staging table."""

from sqlalchemy import text
from datacenter_usa.database import get_engine

def main() -> None:
    engine = get_engine()

    summary_query = text(
        r"""
        WITH parsed AS (
            SELECT
                NULLIF(BTRIM(id), '') AS clean_id,
                CASE
                    WHEN BTRIM(lat) ~
                        '^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$'
                    THEN BTRIM(lat)::numeric
                END AS latitude,
                CASE
                    WHEN BTRIM(lon) ~
                        '^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$'
                    THEN BTRIM(lon)::numeric
                END AS longitude
            FROM staging.pnnl_atlas_records
        ),
        duplicate_ids AS (
            SELECT clean_id
            FROM parsed
            WHERE clean_id IS NOT NULL
            GROUP BY clean_id
            HAVING COUNT(*) > 1
        )
        SELECT
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE clean_id IS NULL
            ) AS missing_ids,
            (SELECT COUNT(*) FROM duplicate_ids)
                AS duplicated_id_values,
            COUNT(*) FILTER (
                WHERE latitude IS NULL
                   OR longitude IS NULL
                   OR latitude NOT BETWEEN -90 AND 90
                   OR longitude NOT BETWEEN -180 AND 180
            ) AS invalid_coordinates
        FROM parsed;
        """
    )

    missing_query = text(
        """
        SELECT
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(state), '') IS NULL
            ) AS missing_state,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(county), '') IS NULL
            ) AS missing_county,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(operator), '') IS NULL
            ) AS missing_operator,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(name), '') IS NULL
            ) AS missing_name,
            COUNT(*) FILTER (
                WHERE NULLIF(BTRIM(sqft), '') IS NULL
            ) AS missing_sqft
        FROM staging.pnnl_atlas_records;
        """
    )

    try:
        with engine.connect() as connection:
            summary = connection.execute(summary_query).mappings().one()
            missing = connection.execute(missing_query).mappings().one()

        print("=== STAGING DATA QUALITY REPORT ===")
        for key, value in summary.items():
            print(f"{key}: {value}")

        print("\n=== MISSING VALUES ===")
        for key, value in missing.items():
            print(f"{key}: {value}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
```

* **Pourquoi ces contrôles ?**

    - **missing_ids** : *repère les identifiants absents*
    - **duplicated_id_values** : *compte les valeurs d'identifiant présentes plusieurs fois*
    - **invalid_coordinates** : *repère les coordonnées non numériques ou hors des limites géographiques valides*.
    - missing_* : *mesure les champs vides pour les informations importantes*.

* **Attention** : 
    - une **coordonnée valide au sens numérique** n'est pas nécessairement une **position géographique correcte**. **A vérifier avec une carte**.

### Exécution du rapport

* lancer scripts dans PowerShell:
```sh
$env:PYTHONPATH = "$PWD\src"
python scripts/check_staging.py
```
* script ne modifie aucune donnée. 
* affiche des statistiques sur la table `staging.pnnl_atlas_records`.

```
rapport :
Champ	Valeurs manquantes	Interprétation
state	0	Tous les enregistrements ont un État renseigné.
county	0	Tous les enregistrements ont un comté renseigné.
operator	412	Certains opérateurs ne sont pas identifiés.
name	252	Certains data centers n'ont pas de nom renseigné.
sqft	0	La surface est renseignée pour tous les enregistrements.
```
```
Sur 1 237 lignes, les champs operator et name présentent respectivement environ 33,3 % et 20,4 % de valeurs manquantes.
```

* **Recommandation** : ne pas supprime de lignes. Un data center sans opérateur ou sans nom peut rester pertinent pour analyser sa **localisation géographique**. Nous **conserverons ces valeurs manquantes** et les **documenterons plutôt** que d'**inventer des informations**.

### Vérification des identifiants et coordonnées

* Pour **décider comment préparer la table** nettoyée, on a besoin des résultats de la première partie du rapport :
    - total_rows
    - missing_ids
    - duplicated_id_values
    - invalid_coordinates

- scripts générant ces lignes:

```sh
python scripts/check_staging.py

# génere:

=== STAGING DATA QUALITY REPORT ===
total_rows: 1237
missing_ids: 0
duplicated_id_values: 0
invalid_coordinates: 0
missing_state: 0
missing_county: 0
missing_operator: 412
missing_name: 252
missing_sqft: 0
missing_operator: 412
missing_name: 252
missing_sqft: 0
```

### 1. Interprétation du rapport

|Enregistrements importés     | Coordonnées invalides  |
|:----------------------------|:-----------------------|
| 1 237                       | 0                      |
| **Identifiants absents ou dupliqués**|**Opérateurs manquants**|
|0                  |412 (33,3 %)|

* 252 noms manquants, soit 20,4 %. 
* Aucun État, comté ou champ de surface n'est vide selon les contrôles réalisés.

- les **identifiants** sont **présents et uniques**
- toutes les **coordonnées** passent les **contrôles numériques et les limites latitude/longitude**.

* **Attention**: *des coordonnées valides ne garantissent pas que le point corresponde à la bonne localisation réelle, Cohérence géographique à vérifier lors de la cartographie*.

### 2. Nettoyage recommandé

* On conserve les 1 237 lignes dans la future table, (*à condition que les prochains contrôles ne révèlent pas d'autres anomaliesbloquantes*) 

    - **id** : conserver et utiliser comme identifiant de référence.
    - **lat, lon** : convertir en valeurs numériques et créer la géométrie PostGIS.
    - **operator, name** : préserver les valeurs manquantes, sans inventer de données.
    - **sqft** : vérifier la conversion numérique et les éventuelles valeurs négatives.
    - **state, county** : conserver pour les futures jointures géographiques.

### 3. Prochaine étape — Contrôle sqft avant conversion

* Avant de créer la table préparée, on vérifie que la surface est bien numérique et qu'elle ne contient pas de valeurs négatives. 
* Une colonne sans valeurs manquantes peut tout de même contenir des valeurs incohérentes.

Dans ``scripts/check_staging.py``, on va ajouter cette requête à l'intérieur de ``main()``, après les requêtes:

```py
sqft_query = text(
    r"""
    WITH values_checked AS (
        SELECT
            BTRIM(sqft) AS raw_sqft,
            CASE
                WHEN BTRIM(sqft) ~
                    '^[+-]?([0-9]+(\.[0-9]*)?|\.[0-9]+)$'
                THEN BTRIM(sqft)::numeric
            END AS numeric_sqft
        FROM staging.pnnl_atlas_records
    )
    SELECT
        COUNT(*) FILTER (
            WHERE numeric_sqft IS NULL
        ) AS invalid_sqft,
        COUNT(*) FILTER (
            WHERE numeric_sqft < 0
        ) AS negative_sqft,
        COUNT(*) FILTER (
            WHERE numeric_sqft = 0
        ) AS zero_sqft
    FROM values_checked;
    """
)
```

* on ajoute:
```sh
sqft = connection.execute(sqft_query).mappings().one()
```

* enfin on ajoute ce block de code :
```sh
print("\n=== SURFACE QUALITY CHECKS ===")for key, value in sqft.items():    print(f"{key}: {value}")
```

* on relance le rapport :
```sh
python scripts/check_staging.py

# affiche
=== STAGING DATA QUALITY REPORT ===
total_rows: 1237
missing_ids: 0
duplicated_id_values: 0
invalid_coordinates: 0

=== MISSING VALUES ===
missing_state: 0
missing_county: 0
missing_operator: 412
missing_name: 252
missing_sqft: 0

=== SURFACE QUALITY CHECKS ===
invalid_sqft: 0
negative_sqft: 0
zero_sqft: 0
```

* **interprétation des résultats**

    - **invalid_sqft = 0** : toutes les surfaces peuvent être converties en nombres selon le format contrôlé.
    - **negative_sqft = 0** : aucune surface négative n'a été détectée.
    - **zero_sqft** : une surface nulle mérite une vérification, mais ne doit pas être automatiquement considérée comme une erreur sans connaître la source.

* **SUITE**:
    - définir le schéma typé de la table préparée 
    - créer les géométries PostGIS en EPSG:4326 
    - ajouter des tests d'intégration pour vérifier le résultat

### 1. Bilan de la qualité des données

Identifiants        1 237 lignes, aucun identifiant manquant ni dupliqué.           Valide


Coordonnées géographiques   Aucune coordonnée invalide selon les limites de latitude et longitude.      Valide


Superficie (sqft)           Aucune valeur non numérique, négative, nulle ou manquante.          Valide


Opérateur (operator)        412 valeurs manquantes, soit 33,3 % des lignes.                 À examiner


Nom du data center (name)       252 valeurs manquantes, soit 20,4 % des lignes.             À examiner


* **Attention** : *les coordonnées sont valides numériquement, mais cela ne garantit pas encore que chaque point soit positionné précisément sur le bon site. De même, les superficies sont présentes et non négatives, mais il restera pertinent de vérifier leur distribution et les valeurs extrêmes*.

D* écision de traitement : conservons les 1 237 lignes. Les opérateurs et noms manquants ne justifient pas la suppression d'enregistrements ; nous pourrons les traiter selon les besoins des analyses.

### 2. Création table préparée

* On conserve ``staging.pnnl_atlas_records`` comme copie brute, puis on crée une table ``processed.data_centers`` contenant des types adaptés:

|Colonne	        |Type cible	              |Utilité                              |
|:-----------------:|:-----------------------:|:-----------------------------------:|
|id	                |TEXT	                  |Identifiant conservé sans altération |
|state	            | TEXT	                  | État américain                       |
|state_abb	        | VARCHAR	              | Code de l'État                       |
|county	            | TEXT	                  | Comté|
|operator	        | TEXT	                  | Opérateur, nullable|
|name	            | TEXT	                  | Nom, nullable|
|sqft	            | NUMERIC	              | Superficie exploitable en SQL|
|lat	            | DOUBLE  PRECISION	      | Latitude|
|lon	            | DOUBLE PRECISION	      | Longitude|
|geom	            | geometry(Point, 4326)   |Géométrie PostGIS|

* **séparation** entre ``staging`` et ``processed`` constitue une **bonne pratique de pipeline**: 

    - **préserve** la **source** et on rend les **transformations reproductibles**.

### 3. Création SQL

* création fichier :
    - ``sql/02_create_processed_table.sql``

* **Pourquoi créer ``geom`` à partir de ``lon``, puis ``lat`` ?**
    - ``ST_MakePoint()`` attend les coordonnées dans cet ordre : 
        + **longitude**, **latitude**. 
        + **système de référence 4326** correspond aux **coordonnées géographiques WGS 84**, adaptées à ce datas set.

* L'index spatial **GIST** facilite les **requêtes géographiques**, par exemple pour **rechercher les data centers dans une zone** ou **compter ceux situés à proximité d'une infrastructure**.

### 4. Exécution

* Ce script est conçu pour une première création. Si ``processed.data_centers`` existe déjà, la commande ``CREATE TABLE`` échouera plutôt que d'écraser les données.

* on lance le script avec un fichier ``.py`` 

* on crée ``scripts/create_processed_table.py`` :

```py
"""Create the processed PostGIS table from staging data."""

from pathlib import Path

from sqlalchemy import text

from datacenter_usa.database import get_engine


def main() -> None:
    sql_path = (
        Path(__file__).resolve().parents[1]
        / "sql"
        / "02_create_processed_table.sql"
    )

    sql_script = sql_path.read_text(encoding="utf-8")
    engine = get_engine()

    try:
        with engine.begin() as connection:
            # Le script contient plusieurs instructions SQL.
            raw_connection = connection.connection.driver_connection
            with raw_connection.cursor() as cursor:
                cursor.execute(sql_script)

        print("Table processed.data_centers créée avec succès.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
```

* puis on lance les scripts ds PowerShell :
```sh
$env:PYTHONPATH = "$PWD\src"
python scripts/create_processed_table.py
# Table processed.data_centers créée avec succès.
```
* L'exécution utilise la connexion PostgreSQL déjà configurée dans le ``.env``.

### 5. Vérification du résultat

* on crée le fichier ``scripts/verify_processed.py`` :
```sh

"""Verify the processed data center table."""

from sqlalchemy import text

from datacenter_usa.database import get_engine


def main() -> None:
    engine = get_engine()

    query = text("""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT id) AS unique_ids,
            COUNT(*) FILTER (
                WHERE geom IS NULL
            ) AS missing_geometries,
            COUNT(*) FILTER (
                WHERE NOT ST_IsValid(geom)
            ) AS invalid_geometries,
            COUNT(*) FILTER (
                WHERE ST_SRID(geom) <> 4326
            ) AS wrong_srid
        FROM processed.data_centers;
    """)

    try:
        with engine.connect() as connection:
            result = connection.execute(query).mappings().one()

        print("=== PROCESSED DATA QUALITY ===")
        for key, value in result.items():
            print(f"{key}: {value}")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
```
* on exécute le script:
```sh
python scripts/verify_processed.py

# résultats
=== PROCESSED DATA QUALITY ===
total_rows: 1237
unique_ids: 1237
missing_geometries: 0
invalid_geometries: 0
wrong_srid: 0
```



```sh```

## Sources

- **PNNL IM3 Open Source Data Center Atlas / Energy Factbook**  
  https://energyfactbook.com/data-centers/
- **U.S. Census Bureau — Cartographic Boundary Files**  
  https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
- **OpenStreetMap** — données géographiques sous-jacentes à l'Atlas.
