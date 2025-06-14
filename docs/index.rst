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

###########################################################
Analyse Agro-climatique de la Région Fès-Meknès (2018-2025)
###########################################################

.. meta::
   :description: Analyse de la relation entre l'indice de végétation (NDVI) et les facteurs climatiques (température, précipitations, humidité) dans la région Fès-Meknès en utilisant Google Earth Engine et Python.
   :keywords: NDVI, Google Earth Engine, Fès-Meknès, Séries Temporelles, Corrélation, Python, Analyse de Données

**Auteur** : Saad ELkhader - Asmae ELhakioui
**Date** : 14 Juin 2025

************
Introduction
************

Ce projet présente une analyse de données complète visant à comprendre la dynamique de la végétation dans la région Fès-Meknès au Maroc et ses liens avec les conditions climatiques locales sur une période de sept ans (2018 à 2025).

L'objectif principal est de quantifier la relation entre l'**Indice de Végétation par Différence Normalisée (NDVI)** et des variables météorologiques clés telles que la **température**, les **précipitations** et l'**humidité relative**. Une attention particulière est portée à l'**analyse de décalage temporel (lag)** pour déterminer le temps de réponse de l'écosystème végétal aux changements climatiques.

L'ensemble du processus, de l'extraction des données satellites à l'analyse statistique, a été réalisé en utilisant l'API **Google Earth Engine** et des bibliothèques Python spécialisées.

.. toctree::
   :maxdepth: 2
   :caption: Navigation du Projet

   data


**********************************************
Phase 1 : Résumé de la Méthodologie
**********************************************

La première phase a consisté à extraire les données brutes de différentes sources satellites via Google Earth Engine. Les variables suivantes ont été collectées :

* **NDVI (Indice de Végétation)** : Provenant des images Landsat 8, il a été utilisé pour mesurer la santé de la végétation.
* **Température & Humidité Relative** : Extraites de la réanalyse climatique ERA5, elles fournissent des indicateurs météorologiques clés.
* **Précipitations** : Obtenues à partir des données CHIRPS Daily.

Une fois extraites, ces séries temporelles ont été nettoyées, traitées et fusionnées en un unique jeu de données synchronisé par date pour l'analyse.

**********************************************
Phase 2 : Résumé de l'Analyse et des Résultats
**********************************************

L'analyse des données fusionnées a révélé plusieurs informations importantes sur les relations entre le climat et la végétation dans la région.

* **Analyse de Corrélation Directe** : A permis de quantifier les relations linéaires immédiates entre les variables. Les résultats montrent des liens attendus, comme une corrélation négative entre le NDVI et la température.

* **Analyse de Corrélation avec Décalage Temporel (Lag)** : C'est la partie la plus révélatrice de l'étude. En créant des variables décalées (par exemple, la pluie d'il y a 30 ou 60 jours), l'analyse a montré que la végétation ne répond pas instantanément aux conditions météorologiques.

.. admonition:: Principale Conclusion de l'Analyse
    :class: important

    La corrélation entre le NDVI et les précipitations est significativement plus forte avec un **décalage de 30 à 60 jours**, ce qui représente le temps nécessaire à l'eau pour être absorbée par le sol et utilisée par les plantes. Cette découverte est cruciale pour la modélisation prédictive.

************
Conclusion
************

Ce projet a démontré avec succès comment utiliser des données satellites publiques pour mener une analyse agro-climatique approfondie. En quantifiant le **temps de réponse de l'écosystème**, les résultats de cette étude peuvent avoir des applications directes pour l'agriculture de précision, la gestion des ressources en eau et l'anticipation des périodes de sécheresse dans la région Fès-Meknès.

Pour une explication technique complète, avec le code et les graphiques, veuillez consulter la page "data" via le menu de navigation.








==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
