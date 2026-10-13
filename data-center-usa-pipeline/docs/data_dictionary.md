# Dictionnaire de données — PNNL / IM3 Data Center Atlas

## Périmètre

Ce dictionnaire décrit le CSV `pnnl_atlas_records.csv` disponible dans le dépôt au moment du contrôle. Le fichier examiné pendant cette étape contient **1 237 lignes et 10 colonnes**. Ces chiffres sont des statistiques de ce snapshot et doivent être recalculés à chaque nouvelle ingestion.

La source est un inventaire ouvert de bâtiments/sites associés aux data centers. Il ne faut pas le considérer comme un recensement exhaustif de tous les data centers américains. Les résultats décrivent les enregistrements de la source.

## Schéma source

| Colonne source | Type observé | Description de travail | Qualité / remarque |
|---|---|---|---|
| `id` | entier | Identifiant du record dans le dataset | 1 237 valeurs présentes ; aucun doublon d'ID dans le snapshot contrôlé. Vérifier la documentation de la source avant de considérer cet ID comme une clé métier définitive. |
| `layer` | texte | Couche/catégorie source de l'objet | Valeur observée : `building`. |
| `state` | texte | Nom de l'État associé au record | 44 valeurs distinctes dans le snapshot. |
| `state_abb` | texte | Abréviation de l'État | 44 valeurs distinctes dans le snapshot. |
| `county` | texte | Comté associé au record | À harmoniser avec les géographies Census pour les jointures. |
| `operator` | texte | Opérateur mentionné par la source | 412 valeurs manquantes, soit 33,31 %. Ne pas interpréter les valeurs absentes comme « aucun opérateur ». |
| `name` | texte | Nom/label du site ou de l'objet selon la source | 252 valeurs manquantes, soit 20,37 %. La granularité exacte du nom doit être confirmée à partir de la documentation source. |
| `sqft` | entier | Champ de surface exprimé, d'après son nom, en pieds carrés | Aucune valeur manquante, nulle ou négative dans le snapshot. Confirmer dans la documentation si la mesure correspond à l'emprise du bâtiment, à la surface de plancher ou à une autre mesure avant de l'interpréter métier. |
| `lat` | flottant | Latitude en degrés décimaux | Aucune valeur manquante dans le snapshot ; limites observées : 18,44683 à 48,75727. |
| `lon` | flottant | Longitude en degrés décimaux | Aucune valeur manquante dans le snapshot ; limites observées : -123,03369 à -66,05169. |

## Colonnes dérivées par le pipeline

| Colonne dérivée | Source | Règle |
|---|---|---|
| `latitude` | `lat` ou colonne latitude équivalente | Conversion numérique par `extract_coordinates()`. La valeur source `lat` est conservée. |
| `longitude` | `lon` ou colonne longitude équivalente | Conversion numérique par `extract_coordinates()`. La valeur source `lon` est conservée. |
| noms normalisés | noms de colonnes du CSV | `normalize_columns()` applique casefold/minuscules, décomposition Unicode NFKD, retrait des marques diacritiques, remplacement des caractères non ASCII alphanumériques par `_`, puis suppression des `_` en début/fin. |

## Règles de normalisation

Exemples attendus :

| Entrée | Sortie |
|---|---|
| `État` | `etat` |
| `São Paulo` | `sao_paulo` |
| `Crème brûlée` | `creme_brulee` |
| `Latitude (°)` | `latitude` |
| `County, State` | `county_state` |
| ` Data Center Name ` | `data_center_name` |
| `Straße` | `strasse` |

Si deux colonnes aboutissent au même nom normalisé, le pipeline doit lever une erreur plutôt que de choisir arbitrairement une colonne. Les noms qui deviennent vides doivent également déclencher une erreur.

## Règles d'interprétation et limites

1. Les colonnes `lat` et `lon` sont des coordonnées géographiques, mais leur présence dans les limites numériques valides ne garantit pas à elle seule que le point appartient au territoire analysé. Une validation spatiale par jointure avec les frontières géographiques sera ajoutée ultérieurement.
2. Les absences de `operator` et `name` sont conservées comme valeurs manquantes ; elles ne sont pas remplacées par des textes arbitraires.
3. Le CSV examiné ne contient pas de variable de capacité en MW/GW ni de statut détaillé de projet. Ces dimensions nécessiteront des sources complémentaires avant de pouvoir comparer la capacité électrique ou les projets futurs.
4. `sqft` ne doit pas être interprété comme capacité électrique. La définition métier et l'unité doivent être confirmées dans la documentation de la source.
5. Les comptages et taux de valeurs manquantes ci-dessus décrivent un snapshot et peuvent changer lors d'une mise à jour de la source.
