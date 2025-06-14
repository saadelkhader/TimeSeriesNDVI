# TimeSeriesNDVI

Modélisation et Prédiction de la Dynamique de la Végétation dans la Région Fès-Meknès
Ce projet vise à analyser, comprendre et prédire la santé de la végétation dans la région Fès-Meknès en se basant sur des données satellitaires et climatiques. Le projet se décompose en deux phases principales : une phase d'analyse exploratoire et une phase de modélisation prédictive.

Phase 1 : Analyse des Facteurs d'Influence (2018-2025)
L'objectif initial était de comprendre les relations entre la dynamique de la végétation, mesurée par l'Indice de Végétation par Différence Normalisée (NDVI), et les principaux facteurs climatiques.

Collecte de Données : Utilisation de Google Earth Engine pour extraire :
L'indice NDVI à partir d'images satellites Landsat 8.
Les précipitations, la température et l'humidité relative à partir des bases de données mondiales (CHIRPS, ERA5-Land).
Analyse de Corrélation : Une analyse approfondie a révélé les liens entre ces variables. La découverte majeure est l'existence d'un décalage temporel : la corrélation la plus forte entre les précipitations et le NDVI survient avec un retard d'environ 60 jours.
Résultat : La création d'un jeu de données complet et unifié, où chaque entrée journalière contient le NDVI ainsi que les conditions météorologiques actuelles et passées (décalées). Ce jeu de données a servi de fondation pour la phase prédictive.
Phase 2 : Modélisation Prédictive du NDVI
L'objectif de cette phase est de développer un modèle capable de prévoir les futures valeurs de l'indice NDVI. En s'appuyant sur les relations découvertes précédemment, plusieurs modèles de prédiction, aux approches différentes et complémentaires, ont été entraînés et évalués.

SARIMA (Seasonal AutoRegressive Integrated Moving Average) :

Description : Un modèle statistique classique et robuste pour les séries temporelles. Il est particulièrement efficace pour capturer la saisonnalité évidente observée dans les données de végétation.
Rôle : Servir de modèle de référence solide basé sur les caractéristiques temporelles intrinsèques du NDVI.
LSTM (Long Short-Term Memory) :

Description : Un type de réseau de neurones récurrent (Deep Learning) spécialement conçu pour apprendre des dépendances à long terme dans les séquences.
Rôle : Tirer parti de la nature séquentielle des données et modéliser les relations complexes entre le NDVI et les multiples variables climatiques sur de longues périodes.
XGBoost (Extreme Gradient Boosting) :

Description : Un modèle d'apprentissage automatique (Machine Learning) basé sur des arbres de décision, réputé pour sa haute performance et sa capacité à gérer des relations non linéaires complexes.
Rôle : Utiliser l'ensemble des facteurs (température, pluie, humidité, et leurs versions décalées) comme des caractéristiques indépendantes pour prédire la valeur du NDVI.
Objectif Final et Bénéfices
L'objectif ultime est de comparer les performances de ces trois modèles pour identifier le plus précis et le plus fiable pour prévoir la santé de la végétation dans la région. Un tel outil prédictif a des applications concrètes de grande valeur, notamment pour l'agriculture de précision, la gestion anticipée des ressources en eau et la prévention des sécheresses.
 lien readthedocs: https://timeseriesndvi.readthedocs.io/fr/latest/index.html#
