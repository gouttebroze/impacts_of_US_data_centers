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