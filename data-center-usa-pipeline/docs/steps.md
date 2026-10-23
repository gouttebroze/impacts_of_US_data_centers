# Architecture steps

## ## schéma mental à retenir

tests/unit/test_cleaning.py
        │
        │ importe
        ▼
datacenter_usa.cleaning
        │
        │ contient
        ▼
extract_coordinates()
valid_coordinate_mask()
filter_valid_coordinates()

Le module cleaning.py définit les fonctions.

Le test importe et teste les fonctions.

Le notebook importe et utilise les fonctions.

## Next Step / création module générique

* Étape suivante

* migration ``normalize_columns()`` du **notebook** vers **datacenter_usa.cleaning**.

* *objectif*:

---------------
Notebook
    ↓
df = normalize_columns(df)
    ↓
src/datacenter_usa/cleaning.py
------------------------

* tests:

"Data Center Name" ---> "data_center_name"
" State "          ---> "state"
"Latitude (°)"     ---> "latitude"

* tests sur cas particuliers : colonnes vides, caractères spéciaux, doublons de noms après normalisation, etc.

* Une fois cleaning.py stabilisé, on aura le *premier module générique réutilisable pour les futurs projets Data Analyst*, 

## Step / pipeline d'ingestion

* flux Notebook → package → tests → données

# Normalisation

* on va améliorer ``normalize_columns()`` en ajoutant une translittération des accents, tout en conservant les contrôles de qualité déjà mis en place.

* L'objectif est que les noms de colonnes soient normalisés de façon prévisible, même lorsque les données proviennent de fichiers français, portugais ou espagnols.

* on utilise le module standard Python ``unicodedata``, sans ajouter de dépendance externe. La normalisation Unicode permet notamment de séparer de nombreuses lettres accentuées de leurs marques diacritiques.

* ajout de la fonction dans le test unitaire

## Tester le résultat

* Scripts (venv activé):

```sh
python -m pip install -e ".[dev]"
python -m pytest -v
```
* ok: *17 tests passed*

## Vérifier la normalisation directement

* Script: 
    `python -c "from datacenter_usa.cleaning import normalize_columns; import pandas as pd; print(normalize_columns(pd.DataFrame([[1, 2]], columns=['État', 'São Paulo'])).columns.tolist())"`:
* retourne valeurs attendues: ['etat', 'sao_paulo']

## étape importante pour le pipeline

* On dispose maintenant de deux fonctions distinctes :

    - ``_normalize_column_name()`` traite un seul nom de colonne.

    - ``normalize_columns()`` applique la règle au DataFrame entier et contrôle les collisions.

* Cette **séparation** rend la **logique plus facile à tester et à faire évoluer**. 

* Le notebook continue simplement d'utiliser :``df = normalize_columns(df_raw)``

* tests validés 

## vérifier la normalisation sur le vrai CSV PNNL

## documenter les règles de transformation dans le dictionnaire de données

* Cela nous permettra de stabiliser le nettoyage avant d'introduire ``PostgreSQL`` et ``PostGIS``

## Modification des fonctions séparées en un pipeline local exécutable et testable

* on transforme les fonctions séparées en un pipeline local exécutable de bout en bout, puis de le couvrir par des tests

* attention à respecter l'**isolation des tests unitaires**

## PostgreSQL & l'extention PostGIS
