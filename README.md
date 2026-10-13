# Analyse des Data Centers aux États-Unis et de leur impact economique, environnemental et sanitaire — 

## Projet Data Analyst - Hugues GOUTTEBROZE - 2026

## Problématique

1. **Où sont concentrés les data centers aux États-Unis et quels États concentrent le plus de sites ?**

Ce notebook construit automatiquement une analyse géographique à partir d'un **dataset réel** issu du PNNL IM3 Open Source Data Center Atlas, via une copie CSV publique publiée par Energy Factbook.

2. **Analyse de l'impact de la forte consommation énergétique des Data Centers au niveau economique, environnemental et sanitaire aux États-Unis**: 

    2.1. **Quels sont les consécquences de la forte consommation d'éléctricité et d'eau au niveau economique, environnemental et sanitaire?** 
    
    2.2 **La consommation énergétique de Data Centers a-t-elle un impact sur les ressources des zones en situation de stress hydrique (région désertiques)?**

### Pipeline

```text
Dataset réel
    ↓
Pandas
    ↓
Nettoyage / contrôle qualité
    ↓
GeoPandas
    ↓
États américains + points des data centers
    ↓
Contextily
    ↓
Carte statique
    ↓
Plotly
    ↓
Carte interactive
    ↓
Graphiques
    ↓
Conclusions métier
```

### Librairies

- **Pandas** : préparation et analyse des données
- **GeoPandas** : données spatiales
- **Matplotlib** : graphiques et carte statique
- **Contextily** : fond de carte
- **Plotly** : carte interactive

> **Important :** le dataset PNNL/IM3 est une compilation ouverte issue notamment d'OpenStreetMap. Il ne constitue pas un recensement exhaustif de tous les data centers américains. La version utilisée ici est datée du 12 février 2026.

## Réflexion nouvelle architecture en pipeline, vers un code propre, modulaire, réutilisable & robuste, incluant une phase de test (unitaires, non-regression, intégration)

- ## First step - Data analytics pipeline

### Problématique métier

+ **Où sont concentrés les data centers aux États-Unis et quels États concentrent le plus de sites observés ?**

+ Ce projet démontre un workflow Data Analyst complet : 

  - **collecte de données → nettoyage → KPI → analyse géographique → visualisation → conclusions**.

## Stack

+ Python 
+ Pandas 
+ GeoPandas 
+ Matplotlib 
+ Contextily 
+ Plotly 
+ Jupyter

## Analyses

- nombre de records et couverture géographique ;
- top États par nombre de data centers ;
- concentration cumulée ;
- analyse des opérateurs ;
- carte choroplèthe ;
- carte géographique avec fond Contextily ;
- carte interactive Plotly.

## Structure

```
data-center-usa-portfolio/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   └── 01_data_centers_usa_analysis.ipynb
├── data/
│   ├── raw/
│   └── processed/
├── src/
├── outputs/
│   ├── figures/
│   └── tables/
└── docs/
    ├── methodology.md
    └── portfolio_checklist.md
```

## Sources

- **PNNL IM3 Open Source Data Center Atlas / Energy Factbook**  
  https://energyfactbook.com/data-centers/
- **U.S. Census Bureau — Cartographic Boundary Files**  
  https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html
- **OpenStreetMap** — données géographiques sous-jacentes à l'Atlas.

+ Le notebook télécharge automatiquement les données 

## Limitation

+ Le dataset est une source ouverte et ne doit pas être présenté comme un recensement exhaustif de tous les data centers américains. Les résultats décrivent les **records observés dans la source**.

## KPI

Le projet calcule notamment :

- records analysés
- États représentés
- nombre de data centers observés par État
- part de chaque État
- part cumulée
- part du Top 5
- principaux opérateurs

## Résultats attendus

### Carte choroplèthe
- Nombre de records par État

### Carte Contextily
- Localisation des sites sur un fond cartographique réel

### Carte Plotly
- Exploration interactive des sites et de leurs métadonnées.

## Compétences de Data Analyst utilisées sur cette étape du projet

- **récupérer** une **donnée externe automatiquement**
- **contrôler** et **nettoyer** un dataset
- définir des **KPI**
- travailler avec des **données géographiques**
- utiliser **Python** pour l'**analyse**
- produire des **visualisations statiques et interactives**
- documenter les **limites** méthodologiques
- transformer une **donnée brute** en **information exploitable**

## Extensions

- capacité électrique (MW/GW)
- statut des projets
- évolution temporelle
- opérateurs
- prix de l'électricité
- réseau électrique
- fibre
- densité géographique
- clustering spatial
- dashboard Streamlit / Power BI

### 2 questions métier avancées

- **Quels territoires américains présentent les caractéristiques infrastructurelles les plus favorables au développement de nouveaux data centers ?**

- **Quels territoires américains présentent les caractéristiques environnementales les plus défavorables et fragiles aux activités des datas centers depuis leur implentation ? Quels les impacts environnementaux et économiques peuvent être misent en lumière ?**

+ Ces questions nécessiteront plusieurs datasets complémentaires et de nouvelles méthodologies de scoring documentées.

## Lancer le projet

```bash
git clone https://github.com/YOUR_USERNAME/data-center-usa-pipeline.git
cd data-center-usa-pipeline

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

jupyter notebook
```

Puis ouvrir :

```text
notebooks/01_data_centers_usa_analysis.ipynb
```

# Du notebook à la nouvelle architecture

- **refacto**.: on commence par reprendre les *fonction du notebooks*, et les rendre **génériques**, et les **tester**

## Creation nouvelle branche pour refactoring

* Étape 1 — Maintenant

    * Nettoyer et organiser le dépôt

        * Identifier le notebook de référence, supprimer les doublons seulement après validation, organiser les dossiers.

* Étape 2

Extraire normalize_columns() et extract_coordinates() dans cleaning.py.

* Étape 3

Écrire les tests pytest : coordonnées valides, valeurs manquantes, colonnes absentes, formats incorrects.

* Étape 4

Créer le premier pipeline d'ingestion et de qualité, avec sauvegarde des données brutes.

* Étape 5

Reproduire les premiers KPI du notebook initial avec les nouvelles fonctions et comparer les résultats.

* Étape 6

Ajouter PostgreSQL/PostGIS, puis les données complémentaires.

+ **Une règle à appliquer**

    - *À chaque refactoring, nous vérifierons que les nouveaux résultats correspondent aux anciens lorsque la logique métier n'a pas changé*.

    - Par exemple :

Ancien notebook
       ↓
Nombre de records par État
       ↓
Résultats de référence
       │
       ▼
Nouvelle fonction Python
       ↓
Même agrégation
       ↓
Comparaison automatique

- Cela nous donnera une première forme de **test de non-régression**, en complément des **tests unitaires**.

### Structure globale du projet


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

### Step 1 refacto.

* **évolution architecture**:

    - Dans ``data-center-usa-pipeline/`` :

src/
└── datacenter_usa/
    ├── __init__.py
    └── cleaning.py

tests/
└── unit/
    └── test_cleaning.py

pyproject.toml

* Extraction et amélioration de la fonction du notebook ``extract_coordinates()``
* Séparation de la validation :

```py
extract_coordinates()
valid_coordinate_mask()
filter_valid_coordinates()
```

#### Tests

* Création de 7 tests unitaires:

    - latitude/longitude déjà présentes
    - coordonnées dans une colonne combinée
    - valeurs impossibles à parser
    - colonnes de coordonnées absentes
    - mauvais type d'entrée
    - coordonnées hors limites
    - filtrage des lignes invalides

* test de la fonction sur le vrai dataset PNNL :

    1 237 records
    1 237 coordonnées valides
    0 coordonnées invalides

#### pas de modification des notebooks

- comme le module (provenant du notebook) fonctionne et qu'il est testé, le notebook devient maintenant un **simple consommateur de la fonction ``extract_coordinates()``** :


Notebook
   │
   └── import extract_coordinates()
                  │
                  ↓
             src/
          datacenter_usa/


### Version intermédiaire du projet