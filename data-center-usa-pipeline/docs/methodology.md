# Methodology

## Scope
The project analyses data-center records present in the public PNNL IM3 Atlas dataset.

## Main KPI
Number of observed data-center records by US state.

## Geographic processing
Coordinates start in WGS84 (`EPSG:4326`). Contextily maps use Web Mercator (`EPSG:3857`).

## State aggregation
Data-center records are aggregated by state and joined to US Census Cartographic Boundary Files using USPS state abbreviations.

## Limitations
The source is not an exhaustive official census. Coverage depends on the underlying open-data sources and methodology.

## Reproducibility
The notebook downloads the data automatically. A production version should preserve a dated raw snapshot and pin dataset versions.

-----------------------------------------------------------------------------------------------------
####  fr. methodology traduction   #### 
-----------------------------------------------------------------------------------------------------

# Méthodologie

## Portée
Le projet analyse les enregistrements relatifs aux centres de données présents dans l'ensemble de données public « PNNL IM3 Atlas ».

## Indicateur clé de performance (KPI) principal
Nombre d'enregistrements relatifs aux centres de données observés par État américain.

## Traitement géographique
Les coordonnées sont exprimées au format WGS84 (`EPSG:4326`). Les cartes de Contextily utilisent le système Web Mercator (`EPSG:3857`).

## Agrégation par État
Les enregistrements relatifs aux centres de données sont agrégés par État et recoupés avec les fichiers de limites cartographiques du recensement américain (US Census Cartographic Boundary Files) à l’aide des abréviations des États utilisées par l’USPS.

## Limites
La source n’est pas un recensement officiel exhaustif. La couverture dépend des sources de données ouvertes sous-jacentes et de la méthodologie utilisée.

## Reproductibilité
Le notebook télécharge automatiquement les données. Une version de production devrait conserver un instantané brut daté et verrouiller les versions des ensembles de données.
