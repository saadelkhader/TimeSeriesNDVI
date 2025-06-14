###########################################################
Modélisation et Prédiction du NDVI avec SARIMA
###########################################################

Cette page détaille la méthodologie complète utilisée pour construire, entraîner et évaluer un modèle **SARIMA** (Seasonal AutoRegressive Integrated Moving Average) dans le but de prédire l'évolution future de l'indice de végétation (NDVI) dans la région Fès-Meknès.

Le processus se décompose en trois phases principales :

1.  **Analyse et Préparation des Données** : Étude de la série temporelle pour comprendre ses caractéristiques.

2.  **Construction du Modèle SARIMA** : Recherche des meilleurs paramètres et entraînement du modèle.

3.  **Prédiction et Visualisation** : Utilisation du modèle pour prévoir les valeurs futures et visualiser les résultats.

**************************************************
Phase 1 : Analyse et Préparation des Données
**************************************************

Avant de construire un modèle, il est essentiel d'analyser la série temporelle pour vérifier ses propriétés, comme la stationnarité et la saisonnalité.

1.1. Préparation de la Série Hebdomadaire
==========================================
Les données quotidiennes sont d'abord agrégées à une fréquence hebdomadaire pour lisser le bruit et régulariser la série.

.. code-block:: python

   import pandas as pd
   import matplotlib.pyplot as plt

   # Charger et préparer les données
   df = pd.read_csv("ndvi_grouped_smoothed_fes_meknes.csv")
   df['date'] = pd.to_datetime(df['date'])
   df_ndvi = df[['date', 'NDVI']].set_index('date').sort_index()

   # Agréger par semaine et gérer les valeurs manquantes par interpolation
   df_weekly = df_ndvi.resample('W').mean().interpolate(method='linear')

   # Afficher les statistiques descriptives
   print(df_weekly.describe())


1.2. Analyse de la Stationnarité
=================================
Un modèle de type ARIMA suppose que la série temporelle est **stationnaire** (ses propriétés statistiques comme la moyenne et la variance ne changent pas dans le temps). Deux tests statistiques sont utilisés pour vérifier cette hypothèse.

.. admonition:: Qu'est-ce que la Stationnarité ?
   :class: tip

   Une série est stationnaire si ses caractéristiques statistiques fondamentales (moyenne, variance, autocorrélation) sont constantes au fil du temps. La plupart des modèles de séries temporelles, y compris SARIMA, fonctionnent mieux sur des données stationnaires. Si une série n'est pas stationnaire, elle est souvent "différenciée" pour le devenir.

.. code-block:: python

   from statsmodels.tsa.stattools import adfuller, kpss

   # Test Augmented Dickey-Fuller (ADF)
   # H0: La série est non-stationnaire.
   adf_result = adfuller(df_weekly['NDVI'])
   print(f'ADF p-value: {adf_result[1]}')
   if adf_result[1] > 0.05:
       print("Conclusion ADF : Non-stationnaire.")
   else:
       print("Conclusion ADF : Stationnaire.")

   # Test KPSS
   # H0: La série est stationnaire.
   kpss_result = kpss(df_weekly['NDVI'], regression='c')
   print(f'KPSS p-value: {kpss_result[1]}')
   if kpss_result[1] < 0.05:
       print("Conclusion KPSS : Non-stationnaire.")
   else:
       print("Conclusion KPSS : Stationnaire.")


1.3. Décomposition et Autocorrélation
=======================================
Pour identifier la saisonnalité et les paramètres potentiels du modèle, on décompose la série et on analyse ses fonctions d'autocorrélation (ACF) et d'autocorrélation partielle (PACF).

.. code-block:: python

   from statsmodels.tsa.seasonal import seasonal_decompose
   from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

   # Décomposition en Tendance, Saisonnalité et Résidus
   decomposition = seasonal_decompose(df_weekly['NDVI'], model='additive', period=52)
   fig = decomposition.plot()
   plt.show()

   # Graphiques ACF et PACF
   fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
   plot_acf(df_weekly['NDVI'], ax=ax1, lags=60)
   plot_pacf(df_weekly['NDVI'], ax=ax2, lags=60)
   plt.show()

.. admonition:: Fonctions Clés

    * **`seasonal_decompose`** : Sépare la série en trois composantes : la **tendance** (l'évolution à long terme), la **saisonnalité** (les cycles répétitifs, ici sur 52 semaines) et les **résidus** (le bruit aléatoire).
    * **`plot_acf` et `plot_pacf`** : Ces graphiques aident à déterminer les ordres `p` et `q` du modèle ARIMA. L'ACF montre la corrélation de la série avec ses propres valeurs décalées, tandis que le PACF montre la corrélation directe après suppression des effets intermédiaires.

**************************************************
Phase 2 : Construction du Modèle SARIMA
**************************************************

2.1. Recherche des Meilleurs Paramètres (Grid Search)
======================================================
Le modèle SARIMA a 7 paramètres : `(p,d,q)` pour la partie non saisonnière et `(P,D,Q,m)` pour la partie saisonnière. Trouver la meilleure combinaison manuellement est difficile. Une recherche par grille (`Grid Search`) est donc utilisée pour tester automatiquement de nombreuses combinaisons et trouver celle qui minimise le critère **AIC (Akaike Information Criterion)**.

.. admonition:: Le critère AIC
    :class: important

    L'AIC est un estimateur de la qualité de prédiction d'un modèle statistique. Il pénalise les modèles qui ont trop de paramètres pour éviter le surapprentissage. Dans une comparaison de modèles, celui avec l'**AIC le plus bas** est considéré comme le meilleur.

.. code-block:: python

   import numpy as np
   import statsmodels.api as sm
   import itertools

   # Définir les plages de paramètres à tester
   p = d = q = range(0, 2)
   pdq = list(itertools.product(p, d, q))
   seasonal_pdq = [(x[0], x[1], x[2], 52) for x in pdq]

   best_aic = np.inf
   best_pdq = None
   best_seasonal_pdq = None

   # Boucle pour tester les combinaisons
   for param in pdq:
       for param_seasonal in seasonal_pdq:
           try:
               temp_model = sm.tsa.SARIMAX(df_weekly['NDVI'],
                                           order=param,
                                           seasonal_order=param_seasonal,
                                           enforce_stationarity=False,
                                           enforce_invertibility=False)
               results = temp_model.fit(disp=False)
               if results.aic < best_aic:
                   best_aic = results.aic
                   best_pdq = param
                   best_seasonal_pdq = param_seasonal
           except:
               continue

   print(f"Meilleurs paramètres : SARIMA{best_pdq}{best_seasonal_pdq} - AIC: {best_aic}")

**************************************************
Phase 3 : Entraînement Final et Prédictions
**************************************************

3.1. Entraînement et Sauvegarde du Modèle
===========================================
Avec les meilleurs paramètres trouvés, le modèle final est entraîné sur l'ensemble des données, puis sauvegardé sur le disque pour une utilisation future sans avoir à le ré-entraîner.

.. code-block:: python

   import statsmodels.api as sm
   import joblib

   # Entraînement du modèle final avec les meilleurs paramètres
   final_model = sm.tsa.SARIMAX(df_weekly['NDVI'],
                                order=best_pdq,
                                seasonal_order=best_seasonal_pdq).fit(disp=False)
   
   # Sauvegarder le modèle entraîné
   joblib.dump(final_model, 'mon_modele_sarima.joblib')


3.2. Prédictions et Visualisation
====================================
Le modèle sauvegardé est ensuite chargé pour générer des prédictions pour les 52 semaines suivantes (un an). La visualisation finale compare les données historiques, les prédictions et l'intervalle de confiance à 95%.

.. code-block:: python

   import joblib
   import matplotlib.pyplot as plt

   # Charger le modèle
   modele_charge = joblib.load('mon_modele_sarima.joblib')

   # Générer les prédictions
   forecast_result = modele_charge.get_forecast(steps=52)
   forecast_df = forecast_result.summary_frame()

   # Visualisation
   plt.figure(figsize=(15, 7))
   plt.plot(df_weekly.index, df_weekly['NDVI'], label='NDVI Historique')
   plt.plot(forecast_df.index, forecast_df['mean'], label='NDVI Prédit', linestyle='--')
   plt.fill_between(forecast_df.index,
                    forecast_df['mean_ci_lower'],
                    forecast_df['mean_ci_upper'],
                    color='darkorange', alpha=0.2, label='Intervalle de confiance')
   plt.title("Prédiction de l'NDVI pour l'année suivante avec SARIMA")
   plt.legend()
   plt.grid(True)
   plt.show()

.. admonition:: Fonctions Clés

    * **`joblib.dump()` et `joblib.load()`** : Fonctions efficaces pour sauvegarder et charger des objets Python complexes comme un modèle Scikit-learn ou Statsmodels.
    * **`model.get_forecast(steps=n)`** : Calcule les prédictions pour les `n` prochaines périodes.
    * **`result.summary_frame()`** : Renvoie un DataFrame Pandas contenant les prédictions (`mean`), ainsi que les bornes inférieure (`mean_ci_lower`) et supérieure (`mean_ci_upper`) de l'intervalle de confiance.
    * **`plt.fill_between()`** : Fonction de Matplotlib utilisée pour colorer la zone entre deux lignes, ici pour représenter visuellement l'incertitude des prédictions (l'intervalle de confiance).
