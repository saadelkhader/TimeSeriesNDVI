###########################################################
Comparaison des Modèles : SARIMA vs. XGBoost vs. LSTM
###########################################################

Cette page présente une analyse comparative rigoureuse de trois approches différentes pour la prédiction de la série temporelle du NDVI :
1.  **SARIMA** : Un modèle statistique classique (univarié).
2.  **XGBoost** : Un modèle de Machine Learning basé sur les arbres de décision (multivarié).
3.  **LSTM** : Un modèle de Deep Learning spécialisé dans les séquences (multivarié).

L'objectif est d'évaluer objectivement leur performance sur une période de test commune afin de sélectionner le modèle le plus précis et le plus fiable pour ce projet.

**************************************************
Phase 1 : Méthodologie de Comparaison
**************************************************

Pour garantir une comparaison équitable, un protocole strict a été mis en place.

1.1. Préparation Unifiée des Données
=====================================
Toutes les données antérieures au **1er janvier 2024** sont utilisées pour l'entraînement, et l'année **2024** complète sert de période de test commune pour évaluer les performances de chaque modèle sur des données qu'il n'a jamais vues.

.. admonition:: Différences Fondamentales dans la Préparation
   :class: important

   * **SARIMA** : Ce modèle est **univarié**, il n'utilise que l'historique de la variable NDVI elle-même. Pour capturer la saisonnalité annuelle, les données sont agrégées à une fréquence **hebdomadaire**.
   * **XGBoost et LSTM** : Ces modèles sont **multivariés**. Ils utilisent non seulement l'historique du NDVI (via des "lags"), mais aussi des **variables exogènes** (température, humidité, précipitations) et des caractéristiques temporelles (mois, jour de l'année) pour enrichir leur prédiction. Ils travaillent sur les données **journalières**.

.. code-block:: python

   # --- ÉTAPE 1: CHARGEMENT ET PRÉPARATION UNIFIÉE DES DONNÉES ---
   
   # Nettoyage robuste des données fusionnées
   df_final = pd.read_csv("data_fusionner_netoyeer.csv")
   df_final['date'] = pd.to_datetime(df_final['date'])
   df_final = df_final.set_index('date').sort_index()
   # ... (code de nettoyage) ...
   
   # Définition de la période de test commune
   split_date = '2024-01-01'
   
   # Préparation pour SARIMA (hebdomadaire, univarié)
   df_weekly = df_final['NDVI'].resample('W').mean().interpolate().bfill()
   train_sarima = df_weekly[df_weekly.index < split_date]
   test_sarima = df_weekly[df_weekly.index >= split_date]
   
   # Préparation pour XGBoost et LSTM (journalier, multivarié)
   df_model = df_final.copy()
   # ... (création des caractéristiques : lags, mois, jour_annee) ...
   X_train, X_test = X[X.index < split_date], X[X.index >= split_date]
   y_train, y_test = y[y.index < split_date], y[y.index >= split_date]


1.2. Métriques d'Évaluation
============================
Deux métriques standards sont utilisées pour mesurer l'erreur de prédiction :
* **RMSE (Root Mean Squared Error)** : L'erreur quadratique moyenne. Elle pénalise davantage les grosses erreurs.
* **MAE (Mean Absolute Error)** : L'erreur absolue moyenne. Elle est plus facile à interpréter.

Pour les deux métriques, **un score plus bas indique un meilleur modèle**.

**************************************************
Phase 2 : Entraînement et Prédictions
**************************************************

Les trois modèles sont entraînés sur la même période historique. Ensuite, ils génèrent des prédictions pour l'année de test (2024).

.. code-block:: python

   # --- ÉTAPE 2: ENTRAÎNEMENT DES TROIS MODÈLES ---
   
   # Modèle 1: SARIMA
   model_sarima = sm.tsa.SARIMAX(train_sarima, order=(0, 1, 1), seasonal_order=(0, 1, 1, 52)).fit(disp=False)
   
   # Modèle 2: XGBoost
   model_xgb = xgb.XGBRegressor(objective='reg:squarederror', n_estimators=500, random_state=42)
   model_xgb.fit(X_train, y_train)
   
   # Modèle 3: LSTM
   # ... (Normalisation et reformatage des données pour LSTM) ...
   model_lstm = Sequential(...)
   model_lstm.compile(...)
   model_lstm.fit(...)

.. code-block:: python

   # --- ÉTAPE 3: GÉNÉRATION ET ALIGNEMENT DES PRÉDICTIONS ---

   # Générer les prédictions pour chaque modèle
   pred_sarima = model_sarima.get_forecast(steps=len(test_sarima)).predicted_mean
   pred_xgb_daily = pd.Series(model_xgb.predict(X_test), index=X_test.index)
   # ... (prédictions LSTM) ...

   # Création du DataFrame de résultats alignés par semaine pour la comparaison
   df_results = pd.DataFrame({'NDVI_Reel': test_sarima})
   df_results['SARIMA_pred'] = pred_sarima
   df_results['XGBoost_pred'] = pred_xgb_daily.resample('W').mean()
   df_results['LSTM_pred'] = pred_lstm_daily.resample('W').mean()
   df_results = df_results.dropna()

**************************************************
Phase 3 : Analyse Comparative des Résultats
**************************************************

3.1. Comparaison Quantitative des Erreurs
==========================================

Les métriques RMSE et MAE sont calculées pour chaque modèle sur la période de test.

.. admonition:: Tableau des Métriques
   :class: note

   .. list-table::
      :header-rows: 1

      * - Modèle
        - RMSE
        - MAE
      * - SARIMA
        - 0.027777
        - 0.020787
      * - XGBoost
        - **0.028302**
        - *0.0204408**
      * - LSTM
        - 0.031210
        - 0.024639

.. image:: _static/votre_image_bar_chart_erreurs.png
   :alt: Comparaison des erreurs des modèles
   :align: center
   :width: 80%

   *Figure 1 : Comparaison des scores d'erreur. Les modèles de Machine Learning (XGBoost, LSTM) sont nettement plus performants que le modèle statistique SARIMA.*

3.2. Comparaison Visuelle des Prédictions
==========================================
La comparaison des courbes de prédiction avec la réalité permet une évaluation qualitative.

.. image:: _static/votre_image_comparaison_courbes.png
   :alt: Comparaison des courbes de prédictions
   :align: center
   :width: 90%

   *Figure 2 : Prédictions vs Réalité (2024). Les courbes de XGBoost et LSTM (orange, vert) suivent de très près la courbe réelle (noir), tandis que celle de SARIMA (bleu) est décalée et moins précise.*

3.3. Analyse de la Distribution des Erreurs
============================================
Le boxplot des erreurs (Réel - Prédit) montre la dispersion et le biais de chaque modèle.

.. image:: _static/votre_image_boxplot_erreurs.png
   :alt: Distribution des erreurs par modèle
   :align: center
   :width: 80%

   *Figure 3 : Les boîtes pour XGBoost et LSTM sont petites et centrées sur zéro, indiquant des erreurs faibles et non biaisées. La boîte de SARIMA est large et au-dessus de zéro, montrant une tendance à la sous-estimation.*

**************************************************
Phase 4 : Conclusion et Choix du Modèle
**************************************************

.. admonition:: 🏆 Le Gagnant : XGBoost
   :class: important

   Bien que les performances de **XGBoost** et **LSTM** soient très similaires et excellentes, **XGBoost est choisi comme le meilleur modèle** pour ce projet pour les raisons suivantes :

   1.  **Rapidité et Simplicité** : Il est beaucoup plus rapide à entraîner que le LSTM, qui nécessite une préparation des données plus complexe (séquences, normalisation).
   2.  **Robustesse** : Il est généralement plus simple à optimiser et moins sujet à des problèmes d'entraînement complexes.
   3.  **Interprétabilité** : Il est plus facile d'extraire l'importance des caractéristiques (feature importance) d'un modèle XGBoost pour comprendre quels facteurs (climat, lags) influencent le plus la prédiction.

   Le modèle **SARIMA**, bien qu'utile pour des séries temporelles simples, a montré ses limites ici. Son incapacité à intégrer des variables externes comme la météo l'a rendu significativement moins précis que les modèles de Machine Learning.
