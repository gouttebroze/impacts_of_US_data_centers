# PostgreSQL + PostGIS — démarrage local

## 1. Prérequis

- Docker Desktop démarré sous Windows.
- L'environnement Python du projet.

## 2. Configurer les variables locales

À la racine de `data-center-usa-pipeline` :

```powershell
Copy-Item .env.example .env
```

Modifie `POSTGRES_PASSWORD` et garde `DATABASE_URL` cohérente avec les identifiants. Ne commite jamais `.env`.

## 3. Installer les dépendances base de données

```powershell
python -m pip install -e ".[dev,db]"
```

L'extra `db` installe SQLAlchemy, psycopg 3 et python-dotenv.

## 4. Démarrer PostgreSQL/PostGIS

```powershell
docker compose --env-file .env -f docker-compose.postgis.yml up -d
```

Contrôle l'état :

```powershell
docker compose --env-file .env -f docker-compose.postgis.yml ps
```

## 5. Créer le schéma et vérifier PostGIS

```powershell
python scripts/init_postgis.py
```

La migration crée `staging`, `analytics`, `staging.data_centers`, l'extension PostGIS et les index spatiaux/attributaires.

## 6. Charger le CSV PNNL local

```powershell
python scripts/load_data_centers_to_postgis.py "..\pnnl_atlas_records.csv"
```

Adapte le chemin si le CSV est stocké ailleurs. Le script passe par le pipeline local pour normaliser/valider les données avant l'upsert. La clé `site_id` empêche les doublons lors des chargements répétés ; le chargement met à jour les records existants.

## 7. Tests

Les tests unitaires de préparation des enregistrements ne nécessitent pas de serveur. Pour les exécuter :

```powershell
python -m pytest tests/unit -v
```

Les tests d'intégration sont désactivés par défaut. Après initialisation de PostGIS :

```powershell
$env:RUN_DB_INTEGRATION = "1"
python -m pytest tests/integration -v
Remove-Item Env:RUN_DB_INTEGRATION
```

Le test d'intégration utilise un identifiant aléatoire et supprime le record créé à la fin.

## 8. Requêtes SQL de vérification

```sql
SELECT COUNT(*) FROM staging.data_centers;

SELECT state_abbr, COUNT(*) AS site_count
FROM staging.data_centers
GROUP BY state_abbr
ORDER BY site_count DESC;

SELECT site_id, ST_AsText(geom)
FROM staging.data_centers
LIMIT 5;
```

## Limites de cette étape

- Le CSV PNNL est un inventaire ouvert, pas un recensement exhaustif de tous les sites.
- `sqft` mesure une surface; ce n'est pas une mesure de puissance (MW) ou de consommation électrique.
- La géométrie est créée à partir de longitude/latitude en EPSG:4326. Les calculs de distance en mètres seront réalisés plus tard avec `geography` ou une projection adaptée.
- Cette étape valide la plomberie technique, pas les analyses de causalité prix électricité/eau.
