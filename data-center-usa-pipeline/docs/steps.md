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