.. Analyse et Prédiction Temporelle du NDVI pour la Région Fès-Meknès documentation master file, created by
   sphinx-quickstart on Wed May 21 19:01:14 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Analyse et Prédiction Temporelle du NDVI pour la Région Fès-Meknès's documentation!
==============================================================================================
.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   data
   model_training
   evaluation_metrics
   interface
   

.. toctree::
   :maxdepth: 2
   :caption: Contents:
   data
   model_training
   evaluation_metrics
   interface
###########################################################
Analyse Agro-Climatique Fès-Meknès
###########################################################

.. image:: https://img.shields.io/badge/Python-3.9+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Python Version

.. image:: https://img.shields.io/badge/Google%20Earth%20Engine-API-brightgreen.svg
   :target: https://earthengine.google.com/
   :alt: Google Earth Engine

.. image:: https://img.shields.io/badge/Pandas-DataFrame-blue.svg
   :target: https://pandas.pydata.org/
   :alt: Pandas

**Analyse Agro-Climatique Fès-Meknès** est un framework d'analyse de données géospatiales pour étudier la relation entre la végétation et le climat, en s'appuyant sur les données satellites de Google Earth Engine.

Overview
--------

Ce projet met en œuvre un pipeline complet pour le suivi de la santé de la végétation dans la région Fès-Meknès (Maroc) en utilisant des séries temporelles de données satellites. Il se concentre sur l'analyse de l'Indice de Végétation par Différence Normalisée (NDVI) et sa corrélation avec des facteurs climatiques clés.

L'analyse de **corrélation avec décalage temporel (lag)** est au cœur de l'étude, permettant de quantifier le temps de réponse de l'écosystème végétal aux variations de température, de précipitations et d'humidité.

Le framework permet une analyse reproductible et approfondie, essentielle pour des applications en agriculture de précision et en gestion des ressources hydriques.

Key Features
------------

✨ **Analyse de Séries Temporelles Multi-Sources**
Combine des données hétérogènes provenant de Landsat 8 (végétation), ERA5 (météo) et CHIRPS (pluie) pour une vue complète.

🛰️ **Extraction de Données Satellites à la Demande**
Utilise la puissance de calcul de Google Earth Engine pour traiter des pétaoctets de données satellites sans téléchargement local.

🔗 **Analyse de Corrélation Avancée**
Implémente des analyses de corrélation standard et avec décalage temporel pour découvrir les relations cachées entre le climat et la végétation.

🔧 **Pipeline de Données Reproductible**
L'ensemble du processus, de l'extraction à la visualisation, est scripté en Python pour garantir la cohérence et la reproductibilité des résultats.

⚡ **Lissage et Synchronisation des Données**
Applique des techniques de moyenne mobile pour réduire le bruit des séries temporelles et fusionne les données de manière robuste sur une base de temps commune.

📊 **Visualisations Compréhensibles**
Génère automatiquement des cartes, des graphiques de séries temporelles et des cartes de chaleur (heatmaps) pour une interprétation intuitive des résultats.

📈 **Quantification du Temps de Réponse**
Fournit des métriques claires sur le décalage optimal entre un événement climatique et la réponse de la végétation.


Getting Started Tutorials
-------------------------

Suivez nos tutoriels pour maîtriser le projet :

.. toctree::
   :maxdepth: 2
   :caption: Pour Commencer

   tutorials/index
   tutorials/installation
   tutorials/quickstart
   tutorials/first_analysis


📚 **Aperçu des Tutoriels :**

**Tutoriel d'Installation** - Guide de configuration complet, incluant l'authentification à Google Earth Engine.

**Démarrage Rapide** - Lancez votre première extraction de données NDVI et générez un graphique en 3 étapes.

**Première Analyse Complète** - Réalisez une analyse complète de A à Z :
- 🔧 **Extraction des Données**: Chargez et traitez les données NDVI, température, humidité et précipitations.
- 🔗 **Fusion des Données**: Synchronisez toutes les séries temporelles par date.
- 📊 **Analyse de Corrélation**: Calculez et visualisez la matrice de corrélation directe.
- 📈 **Analyse de Décalage (Lag)**: Identifiez le temps de réponse de la végétation.
- 💾 **Export des Résultats**: Sauvegardez les données traitées et les graphiques.
- 🌍 **Visualisation Cartographique**: Générez une carte du NDVI moyen de la région.

**Ce que vous obtiendrez :**
- ✅ Des séries temporelles propres pour 4 variables agro-climatiques.
- ✅ Une analyse de corrélation quantifiant la relation climat-végétation.
- ✅ Une estimation claire du décalage temporel optimal pour la pluie (> 30 jours).
- ✅ Un pipeline de données complet, automatisé et reproductible.


.. toctree::
   :maxdepth: 2
   :caption: Guide d'Utilisation

   user_guide/index
   user_guide/data_sources
   user_guide/correlation_analysis


.. toctree::
   :maxdepth: 2
   :caption: Développement

   development/index
   development/contributing


.. toctree::
   :maxdepth: 1
   :caption: À Propos

   about/changelog
   about/license


Principaux Résultats
--------------------

Corrélation NDVI vs. Climat
~~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Corrélation avec Précipitations (décalage de 30-60 jours)**: > 0.60
- **Corrélation avec Humidité Relative (décalage de 15-30 jours)**: > 0.55
- **Corrélation avec Température (décalage de 7-15 jours)**: < -0.40 (négative)

Temps de Réponse de l'Écosystème
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- **Temps de Latence à la Pluie**: ~45 jours pour un impact maximal sur le NDVI.
- **Impact de la Température**: Effet plus rapide, visible en 1 à 2 semaines.

Résumé des Sources de Données
-----------------------------

**Données Satellites Extraites via Google Earth Engine**

.. list-table::
   :header-rows: 1

   * - Source de Données
     - Variables Extraites
     - Résolution Native
     - Fournisseur
   * - Landsat 8 (OLI/TIRS)
     - NDVI (Santé de la végétation)
     - 30 mètres
     - USGS / NASA
   * - ERA5-Land Hourly
     - Température de l'air, Humidité Relative
     - ~11 km
     - ECMWF / Copernicus
   * - CHIRPS Daily
     - Précipitations
     - ~5.5 km
     - Climate Hazards Group

Auteurs
-------


**Saad ELkhader**
**Asmae ELhakioui**














==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
