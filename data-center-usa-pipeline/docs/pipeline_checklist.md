# Configuration environnements, dependances

## transformer le projet en pipeline,

* configurations & explications (sous windows...enfin Windows/PowerShell!):
    - ``venv``, 
    - ``requirements.txt``
    - ``pyproject.toml``
    - ``__pycache__``.

1. principe général

l'environnement de travail :

dépôt GitHub
│
├── data-center-usa-pipeline/
│   │
│   ├── .venv/              --- environnement Python local
│   ├── src/                --- ton code
│   ├── tests/              --- tests
│   ├── notebooks/          --- notebooks
│   ├── requirements.txt    --- dépendances
│   └── pyproject.toml      --- configuration du projet Python
│
└── ...

Le rôle de ``.venv`` est de séparer les bibliothèques de ce projet du reste de ton ordinateur.

2. Pourquoi utiliser ``venv`` ?

pr gérer les différentes versions suivant tel besoin d'un projet:

Projet A
→ pandas 2.x
→ geopandas 1.x

Projet B
→ pandas autre version
→ geopandas autre version

* Permet de ne pas tout installer globalement sur Windows, & éviter des conflits.

* Avec un environnement virtuel :

Projet A
└── .venv/
    └── ses propres packages

Projet B
└── .venv/
    └── ses propres packages

* Chaque projet possède son environnement.

* pratique standard en Python.

3. Créer le venv

* dans le dossier :

``python -m venv .venv``

* Python crée :

data-center-usa-pipeline/
│
├── .venv/
│   ├── Scripts/
│   ├── Lib/
│   └── ...

4. Activer le venv sous Windows

* Avec PowerShell :

``.\.venv\Scripts\Activate.ps1``

* ce qui lance l'environnement tel:

    (.venv) PS C:\Users\...\data-center-usa-pipeline>

* (.venv) est important (signifie que les commandes Python utilisent maintenant cet environnement).

* PowerShell me refuse l'activation, et me retourne l'erreur suivante et fréquente :

``running scripts is disabled on this system``

* Que faire??!! tt simplement, lancer:

``Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser``

* Suivi de:

``.\.venv\Scripts\Activate.ps1``

* **Steps 5 & 6**: Vérifier que le bon Python est utilisé

- Une fois le ``venv`` activé, on check la version :

``python --version``

* Puis, chercher l'executable :

``where.exe python``

* Ce qui est sensé retourner (ici, le script me renvoie 3 chemins, dont un tel que ci-dessous)
+ A NOTER / ce qui est rendu ???!!
``where.exe python``

* rend 3 chemins:
    C:\Users\Data404\Documents\PERSONNAL_PROJECTS\Data_centers_USA\impacts_of_US_data_centers\data-center-usa-pipeline\.venv\Scripts\python.exe
    C:\Users\Data404\AppData\Local\Microsoft\WindowsApps\python.exe
    C:\Users\Data404\AppData\Local\Python\bin\python.exe

* et non un seul tel que:
    C:\...\data-center-usa-pipeline\.venv\Scripts\python.exe

* **A CHERCHER car semble important...**

#### Script pr lancer install des dépendences de requirements.txt ?

* fichier qui contient :

```txt
pandas
numpy
geopandas
matplotlib
contextily
plotly
requests
pyogrio
pytest
pytest-cov
```

* ds fichier ``requirements.txt``
 
8. Installer les dépendances en une seule commande

* Avec ``venv`` activé :

``python -m pip install --upgrade pip``

* Puis :

``pip install -r requirements.txt``

* & Python installe les bibliothèques listées 

    - pr vérifier :

        - ``pip list``

#### 10. Et pyproject.toml, à quoi sert-il ?

C'est probablement la partie qui va t'intéresser le plus.

requirements.txt répond principalement à :

Quelles bibliothèques dois-je installer ?

Alors que pyproject.toml répond à une question plus large :

Comment mon projet Python est-il configuré et construit ?

Il peut notamment définir :

le nom du projet ;
sa version ;
sa description ;
la version minimale de Python ;
les dépendances ;
les dépendances de développement ;
la configuration de pytest ;
le système de packaging ;
éventuellement des outils comme Ruff, Black, MyPy, etc.

Dans ton projet, nous avons par exemple :

[project]
name = "datacenter-usa"
version = "0.1.0"
description = "US data center geospatial and business analysis"
requires-python = ">=3.10"

Cela décrit ton projet Python.

11. requirements.txt vs pyproject.toml

Pour ton projet, pense à ceci :

requirements.txt
        ↓
"Quelles dépendances dois-je installer ?"

pyproject.toml
        ↓
"Comment est défini/configuré mon projet Python ?"

Mais il y a une nuance importante : les deux peuvent contenir des dépendances.

Dans un projet moderne, on peut même n'avoir qu'un pyproject.toml.

Par exemple :

[project]
dependencies = [
    "pandas",
    "numpy",
    "geopandas"
]

Dans ton projet actuel, nous gardons les deux pour le moment parce que c'est plus pédagogique et pratique.

Plus tard, on pourra décider d'unifier la gestion des dépendances.

12. Pourquoi pytest est dans requirements.txt ?

Parce qu'il fait partie de l'environnement nécessaire au développement.

Tu as deux catégories :

Dépendances du projet
pandas
numpy
geopandas
...
Dépendances de développement
pytest
pytest-cov

Plus tard, on pourra formaliser cela dans pyproject.toml :

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-cov"
]

Et installer :

pip install -e ".[dev]"

Mais pour le moment, gardons les choses simples.

13. À quoi servent les dossiers __pycache__ ?

Tu vas probablement voir apparaître quelque chose comme :

src/
└── datacenter_usa/
    ├── __init__.py
    ├── cleaning.py
    └── __pycache__/
        └── cleaning.cpython-313.pyc

__pycache__ est créé automatiquement par Python.

Lorsque Python exécute :

from datacenter_usa.cleaning import extract_coordinates

Python transforme le code source en une forme compilée plus rapide à charger.

Cette version peut être stockée dans :

__pycache__/

avec des fichiers :

*.pyc
14. Est-ce que tu dois modifier __pycache__ ?

Non.

Tu n'as rien à faire dedans.

Tu peux même supprimer tout le dossier :

__pycache__

Python le recréera automatiquement.

15. Pourquoi __pycache__ ne doit pas aller sur GitHub ?

Parce que ce ne sont pas des fichiers source du projet.

Ils sont générés automatiquement par Python.

Ton .gitignore contient normalement :

__pycache__/
*.py[cod]

Donc Git les ignore.

Tu peux vérifier :

git status

Tu ne devrais pas voir :

__pycache__

dans les fichiers à committer.

--------------------------------------------------------------------------------------------


# Pipeline checklist

- Run the notebook from a fresh kernel
- Verify source download
- Check record count and coordinate quality
- Export 2–4 key figures
- Add screenshots to README
- Replace `YOUR_USERNAME` in README
- Add GitHub topics: *python, pandas, geopandas, gis, data-analysis, data-visualization*
- Keep limitations visible
- Do not commit large/raw datasets unnecessarily

----------------------------------------------------------------------------------------------------------------------------
-        ####  french checklist traduction   #### 
----------------------------------------------------------------------------------------------------------------------------

- Exécuter le notebook à partir d'un kernel vierge
- Vérifier le téléchargement des sources
- Vérifier le nombre d'enregistrements et la qualité des coordonnées
- Exporter 2 à 4 indicateurs clés
- Ajouter des captures d'écran au fichier README
- Remplacer `YOUR_USERNAME` dans le fichier README
- Ajouter les thèmes GitHub suivants : *python, pandas, geopandas, gis, analyse de données, visualisation de données*
- Indiquer clairement les limites
- Ne pas valider inutilement des ensembles de données volumineux ou bruts

