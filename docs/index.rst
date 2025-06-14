.. Analyse et Prédiction Temporelle du NDVI pour la Région Fès-Meknès documentation master file, created by
   sphinx-quickstart on Wed May 21 19:01:14 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Analyse et Prédiction Temporelle du NDVI pour la Région Fès-Meknès's documentation!
==============================================================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

#########################################
Analyse de Données Environnementales
#########################################

Ce projet présente une analyse des séries temporelles de plusieurs indicateurs environnementaux pour un point géographique au Maroc, en utilisant la puissance de calcul de l'API Google Earth Engine.

.. toctree::
   :maxdepth: 2
   :caption: Contenu Principal:

  .. _accueil:

#####################################################################
Analyse de la Végétation et du Climat dans la Région Fès-Meknès
#####################################################################

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Contenu:

   self

.. note::
   Ce projet utilise l'API Google Earth Engine (GEE) pour collecter et analyser des données géospatiales. Une authentification et un projet GEE valide sont nécessaires pour exécuter le code.

**Objectif du projet :** Analyser l'évolution de la santé de la végétation (via l'indice NDVI) dans la région Fès-Meknès au Maroc entre 2018 et 2025, et étudier sa corrélation avec des variables météorologiques clés telles que les précipitations, la température et l'humidité relative.

**Périmètre géographique :**
* **Région :** Fès-Meknès, Maroc
* **Coordonnées (approximatives) :** de -5.8° à -3.0° de longitude et de 33.0° à 34.5° de latitude.

**Source des données :**
* **NDVI :** Images satellite Landsat 8 (Collection 2, Tier 1, Surface Reflectance).
* **Précipitations :** Données CHIRPS Daily.
* **Température & Humidité :** Données ERA5-Land Hourly.

---

*********************************************************
Étape 1 : Acquisition et Prétraitement des Données
*********************************************************

Cette première étape consiste à extraire les séries temporelles pour chaque variable depuis Google Earth Engine.

1.1. Indice de Végétation (NDVI) lissé
==========================================
Nous calculons le NDVI moyen pour chaque image Landsat 8 disponible avec une couverture nuageuse inférieure à 10%. Une moyenne mobile est ensuite appliquée pour lisser les variations à court terme.

.. code-block:: python
   :caption: Script d'extraction et lissage du NDVI

   import ee
   import pandas as pd
   import matplotlib.pyplot as plt
   from tqdm import tqdm

   # Définir la géométrie et la période
   roi_fes_meknes = ee.Geometry.Rectangle([-5.8, 33.0, -3.0, 34.5])
   start_date = "2018-01-01"
   end_date = "2025-01-01"

   # Charger la collection Landsat 8
   landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2") \
       .filterBounds(roi_fes_meknes) \
       .filterDate(start_date, end_date) \
       .filter(ee.Filter.lt("CLOUD_COVER", 10))

   # Fonction pour calculer NDVI moyen par image
   def get_ndvi_feature(image):
       ndvi = image.normalizedDifference(["SR_B5", "SR_B4"]).rename("NDVI")
       date = image.date().format("YYYY-MM-dd")
       mean_dict = ndvi.reduceRegion(
           reducer=ee.Reducer.mean(),
           geometry=roi_fes_meknes,
           scale=100,
           maxPixels=1e9
       )
       return ee.Feature(None, {'date': date, 'NDVI': mean_dict.get('NDVI')})

   # Appliquer la fonction et extraire les données
   ndvi_fc = landsat.map(get_ndvi_feature)
   features = ndvi_fc.toList(ndvi_fc.size())
   ndvi_data = []
   for i in tqdm(range(features.size().getInfo()), desc="Extraction NDVI"):
       f = ee.Feature(features.get(i)).getInfo()
       props = f['properties']
       if 'NDVI' in props and props['NDVI'] is not None:
           ndvi_data.append(props)

   # Créer et nettoyer le DataFrame
   df = pd.DataFrame(ndvi_data)
   df["date"] = pd.to_datetime(df["date"])
   df["NDVI"] = pd.to_numeric(df["NDVI"], errors="coerce")
   df = df.dropna()
   df_mean = df.groupby("date").mean().reset_index()
   df_mean["NDVI_smoothed"] = df_mean["NDVI"].rolling(window=5, center=True).mean()

   # Sauvegarder le CSV
   df_mean.to_csv("ndvi_grouped_smoothed_fes_meknes.csv", index=False)
   print("✅ CSV du NDVI exporté avec succès.")


1.2. Précipitations (CHIRPS)
============================
Extraction des précipitations journalières moyennes (en mm) sur la zone d'étude.

.. code-block:: python
   :caption: Script d'extraction des précipitations

   # ... (importations ee, pd, etc.)
   chirps = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY") \
       .filterBounds(roi_fes_meknes) \
       .filterDate(start_date, end_date) \
       .select("precipitation")

   def extract_daily_precip(image):
       date = image.date().format("YYYY-MM-dd")
       mean_rain = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi_fes_meknes, scale=5000, maxPixels=1e9)
       return ee.Feature(None, {"date": date, "precipitation": mean_rain.get("precipitation")})

   rain_fc = chirps.map(extract_daily_precip)
   # ... (même logique d'extraction en DataFrame que pour le NDVI)
   # ...
   # df_rain.to_csv("serie_precipitation_fes_meknes.csv", index=False)


1.3. Température (ERA5-Land)
================================
Extraction de la température de l'air à 2 mètres (en °C) à midi (12:00) pour chaque jour.

.. code-block:: python
   :caption: Script d'extraction de la température

   # ... (importations ee, pd, etc.)
   def extract_daily_temp(image):
       date = image.date().format("YYYY-MM-dd")
       temp_c = image.select("temperature_2m").subtract(273.15) # K en °C
       mean_temp = temp_c.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi_fes_meknes, scale=1000, maxPixels=1e9)
       return ee.Feature(None, {"date": date, "temperature": mean_temp.get("temperature_2m")})

   # Boucle par année pour éviter les timeouts GEE
   all_temp_data = []
   for year in range(2018, 2026):
       # ...
       era5 = ee.ImageCollection("ECMWF/ERA5_LAND/HOURLY") \
           .filterBounds(roi_fes_meknes) \
           .filterDate(f"{year}-01-01", f"{year}-12-31") \
           .filter(ee.Filter.calendarRange(12, 12, 'hour')) \
           .select("temperature_2m")
       # ... (logique d'extraction similaire)
   # df_temp.to_csv("serie_temperature_fes_meknes.csv", index=False)

1.4. Humidité Relative (ERA5-Land)
=====================================
Calcul et extraction de l'humidité relative journalière (en %) à partir de la température de l'air et du point de rosée.

.. code-block:: python
   :caption: Script de calcul et d'extraction de l'humidité relative

   # ... (importations ee, pd, etc.)
   def compute_relative_humidity(image):
       temp = image.select("temperature_2m").subtract(273.15)
       dew = image.select("dewpoint_temperature_2m").subtract(273.15)
       # Formule de Magnus pour calculer la pression de vapeur saturante
       es = temp.multiply(17.625).divide(temp.add(243.04)).exp()
       ed = dew.multiply(17.625).divide(dew.add(243.04)).exp()
       rh = ed.divide(es).multiply(100).rename("RH")
       mean_rh = rh.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi_fes_meknes, scale=1000)
       return ee.Feature(None, {"date": image.date().format("YYYY-MM-dd"), "RH": mean_rh.get("RH")})
   # ... (logique d'extraction similaire par année)
   # df_rh.to_csv("humidite_relative_fes_meknes.csv", index=False)

---

***********************************************
Étape 2 : Fusion et Nettoyage des Données
***********************************************
Les différents fichiers CSV générés sont fusionnés en un seul DataFrame pandas sur la base de la colonne `date`.

.. code-block:: python
   :caption: Script de fusion des séries temporelles

   import pandas as pd

   # Charger chaque CSV
   df_ndvi = pd.read_csv("ndvi_grouped_smoothed_fes_meknes.csv")
   df_precip = pd.read_csv("serie_precipitation_fes_meknes.csv")
   df_temp = pd.read_csv("serie_temperature_fes_meknes.csv")
   df_rh = pd.read_csv("humidite_relative_fes_meknes.csv")

   # Convertir les dates
   df_ndvi["date"] = pd.to_datetime(df_ndvi["date"])
   # ... (faire de même pour les autres DataFrames)

   # Fusions successives
   df_all = pd.merge(df_ndvi, df_precip, on="date", how="inner")
   df_all = pd.merge(df_all, df_temp, on="date", how="inner")
   df_all = pd.merge(df_all, df_rh, on="date", how="inner")

   # Nettoyage final (suppression des lignes avec valeurs manquantes)
   df_all_cleaned = df_all.dropna().reset_index(drop=True)
   
   # Exporter le jeu de données final
   df_all_cleaned.to_csv("donnees_fusionnees_fes_meknes_nettoyees.csv", index=False)
   print("✅ DataFrame fusionné et nettoyé exporté.")

---

***************************************
Étape 3 : Analyse et Visualisation
***************************************

3.1. Carte du NDVI Médian (2018-2025)
=====================================
Une carte est générée en calculant la médiane du NDVI pour chaque pixel sur toute la période. La médiane est utilisée pour sa robustesse aux valeurs extrêmes (ex: nuages non détectés).

.. image:: carte_ndvi_moyen_fes_meknes.png
   :alt: Carte du NDVI médian de la région Fès-Meknès
   :align: center
   :width: 80%

.. code-block:: python
   :caption: Génération de la carte NDVI

   # ... (voir le code de génération de la carte dans les scripts fournis)

3.2. Visualisation des Séries Temporelles Combinées
==================================================
Un graphique superposant les quatre variables (NDVI, précipitations, température, humidité) est créé pour une analyse visuelle des tendances et saisonnalités.

.. image:: graph_combine.png
   :alt: Graphique combiné des séries temporelles
   :align: center

.. code-block:: python
   :caption: Création du graphique multi-axes

   # ... (voir le code de génération du graphique dans les scripts fournis)


3.3. Matrice de Corrélation
===========================
Une heatmap est générée pour quantifier la corrélation linéaire entre les variables.

.. image:: heatmap_correlation_fes_meknes.png
   :alt: Heatmap des corrélations
   :align: center
   :width: 60%

.. code-block:: python
   :caption: Calcul et affichage de la matrice de corrélation

   import seaborn as sns
   import matplotlib.pyplot as plt

   # Sélectionner les colonnes numériques pertinentes
   colonnes_pour_correlation = ['NDVI_smoothed', 'precipitation', 'temperature', 'RH']
   df_pour_correlation = df_all_cleaned[colonnes_pour_correlation]

   # Calculer la matrice
   matrice_correlation = df_pour_correlation.corr()

   # Visualiser
   plt.figure(figsize=(10, 8))
   sns.heatmap(matrice_correlation, annot=True, cmap='coolwarm', fmt=".2f")
   plt.title('Heatmap de Corrélation entre NDVI et Variables Météo')
   plt.show()

---

*********************************************************
Étape 4 : Analyse de Corrélation avec Décalage Temporel
*********************************************************
La végétation ne réagit pas instantanément aux changements climatiques. Cette analyse introduit un décalage temporel (lag) sur les variables météorologiques pour trouver la corrélation maximale avec le NDVI.

.. code-block:: python
   :caption: Calcul des corrélations avec décalage

   df_lag = df_all_cleaned.copy()

   # Définir les décalages à tester (en jours)
   lags = [15, 30, 45, 60, 75, 90]

   for lag in lags:
       df_lag[f'precipitation_lag{lag}'] = df_lag['precipitation'].shift(lag)
       df_lag[f'temperature_lag{lag}'] = df_lag['temperature'].shift(lag)
       df_lag[f'RH_lag{lag}'] = df_lag['RH'].shift(lag)

   # Nettoyer les NaN créés par le décalage
   df_lag_cleaned = df_lag.dropna()

   # Recalculer la matrice de corrélation
   matrice_correlation_lag = df_lag_cleaned.corr()

   # Afficher les corrélations les plus fortes avec le NDVI
   print(matrice_correlation_lag['NDVI_smoothed'].sort_values(ascending=False))


**Résultats attendus :** Cette analyse permet d'identifier, par exemple, que le pic de NDVI est le plus fortement corrélé avec les précipitations tombées **45 jours** auparavant, fournissant un aperçu précieux sur l'inertie de l'écosystème local. Des nuages de points sont ensuite utilisés pour visualiser ces relations décalées.




==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
