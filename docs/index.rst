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

   DATA_INFLUANCE


#################################################
Méthodologie d'Extraction des Données
#################################################

L'extraction des données a suivi un processus rigoureux en quatre étapes principales, allant de la définition des paramètres à la génération des visualisations finales.

.. _etape1:

1. Initialisation et Définition des Paramètres
================================================

La première étape consiste à configurer l'environnement de travail et à définir les paramètres fondamentaux de l'analyse.

* **Initialisation de l'API** : Connexion à la plateforme Google Earth Engine.
* **Définition du Point d'Intérêt (POI)** : Un point géographique spécifique a été choisi pour concentrer l'analyse. Pour cette étude, un point près de la capitale, Rabat, a été sélectionné.

    .. code-block:: python

       point_interet = ee.Geometry.Point(-6.8498, 33.9716)

* **Définition de la Période Temporelle** : Une période de quatre ans, du **1er janvier 2017 au 31 décembre 2020**, a été choisie pour observer les variations saisonnières et les tendances à moyen terme.

.. _etape2:

2. Acquisition des Collections d'Images Satellites
====================================================

Google Earth Engine héberge un catalogue massif de données géospatiales. Pour cette analyse, les collections d'images suivantes ont été utilisées :

* **NDVI (Indice de Végétation)** : La collection `MODIS/061/MOD13A2` a été utilisée pour suivre la santé et la densité de la végétation. La bande spectrale 'NDVI' a été sélectionnée.

* **Température de Surface** : La collection `MODIS/061/MOD11A2` a fourni les données de température de surface terrestre (LST). La bande 'LST_Day_1km' a été utilisée.

* **Précipitations** : Les données de précipitations quotidiennes proviennent de la collection `UCSB-CHG/CHIRPS/DAILY`.

.. note::
   Les données d'humidité n'étant pas directement disponibles dans une collection simple et compatible, leur graphique est présenté à titre illustratif dans ce projet.

.. _etape3:

3. Extraction et Transformation des Données (GEE vers Pandas)
==============================================================

Cette étape cruciale consiste à extraire les valeurs des pixels correspondant à notre point d'intérêt pour chaque image dans la période définie.

* **Filtrage des collections** : Chaque collection a été filtrée par date et par localisation (le POI).
* **Extraction des valeurs** : La fonction `geemap.ee_to_pandas` a été utilisée pour interroger le serveur de Google Earth Engine et rapatrier les données sous la forme d'un **DataFrame Pandas** pour chaque variable.
* **Nettoyage des données** : Une fois les données en local, elles ont été nettoyées :
    * La colonne de temps (timestamp) a été convertie au format `datetime`.
    * Cette colonne a été définie comme index du DataFrame pour faciliter les manipulations temporelles.

.. _etape4:

4. Traitement Final et Visualisation
=======================================

La dernière étape consiste à traiter les données brutes pour les rendre interprétables et à les visualiser.

* **Application des Facteurs d'Échelle** : Les données MODIS ne sont pas stockées dans leurs unités réelles. Les facteurs d'échelle fournis dans la documentation de Google Earth Engine ont été appliqués pour convertir les valeurs en unités standards.
    * Pour le NDVI : `valeur * 0.0001`
    * Pour la Température : `(valeur * 0.02) - 273.15` pour convertir du Kelvin au Celsius.

* **Génération des Graphiques** : Pour chaque variable, un graphique linéaire a été généré avec `matplotlib` pour visualiser son évolution dans le temps.
* **Sauvegarde en PNG** : Chaque graphique a été automatiquement sauvegardé sous forme de fichier image `.png` dans le dossier `_static/` de la documentation, prêt à être affiché sur le site.

---
.. centered::
   **Visualisation des Séries Temporelles**

.. list-table::
   :widths: 50 50
   :class: nounderline

   * - .. image:: _static/serie_ndvi.png
          :alt: Série temporelle du NDVI

     - .. image:: _static/serie_temperature.png
          :alt: Série temporelle de la température

   * - .. image:: _static/serie_precipitation.png
          :alt: Série temporelle des précipitations

     - .. image:: _static/serie_humidite.png
          :alt: Série temporelle de l'humidité

## Matrice de Corrélation

Voici l'analyse de corrélation entre les différentes variables étudiées. Elle montre comment des facteurs comme les lumières nocturnes sont liés à la densité de population.

.. image:: _static/matrice_correlation.png
   :alt: Matrice de corrélation des données
   :align: center
   :scale: 80%
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
