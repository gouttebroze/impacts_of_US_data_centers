# US Data Centers — Geospatial Data Analysis

## First step - Data analytics pipeline

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
