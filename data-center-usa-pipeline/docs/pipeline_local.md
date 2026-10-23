# Pipeline local : ingestion, nettoyage et qualité

## Étapes

1. `load_csv()` charge un CSV local ou distant.
2. `normalize_columns()` harmonise les noms de colonnes.
3. `validate_required_columns()` vérifie le contrat de schéma.
4. `extract_coordinates()` crée des colonnes latitude/longitude numériques.
5. `valid_coordinate_mask()` vérifie les bornes numériques géographiques.
6. `quality_report()` calcule les indicateurs de qualité sur le dataset avant filtrage.
7. `prepare_dataset()` renvoie les données préparées, le rapport et un résumé du pipeline.

## Lancer les tests

```powershell
python -m pytest -v
```

Les tests utilisent des fichiers temporaires synthétiques ; ils ne dépendent pas d'Internet ni du CSV de production.

## Exécuter avec le CSV du projet

Depuis le dossier `data-center-usa-pipeline` :

```powershell
python scripts/validate_local_pipeline.py
```

Le script recherche `pnnl_atlas_records.csv` à la racine du dépôt, puis dans `data/raw/`. Il exporte le rapport de qualité, le dataset préparé et le résumé JSON sous `outputs/tables/`.

## Limite actuelle

La validation vérifie les limites numériques globales de latitude/longitude. Elle ne prouve pas que chaque point est situé aux États-Unis ou dans le bon État. Une validation spatiale sur les frontières des États sera ajoutée plus tard avec GeoPandas/PostGIS.
