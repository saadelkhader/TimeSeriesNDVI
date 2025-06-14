###########################################################
Modélisation Prédictive avec XGBoost
###########################################################

Cette page détaille la construction d'un modèle de prédiction de séries temporelles en utilisant **XGBoost** (Extreme Gradient Boosting), une approche basée sur le Machine Learning qui diffère des modèles statistiques classiques comme SARIMA.

L'objectif est de prédire la valeur future de l'NDVI en utilisant non seulement son historique, mais aussi des variables exogènes (climat) et des caractéristiques temporelles.

**************************************************
Phase 1 : Feature Engineering (Création de Caractéristiques)
**************************************************

La première étape consiste à transformer la série temporelle en un problème de régression supervisée. Pour cela, nous créons de nouvelles caractéristiques (features) à partir des données existantes.

.. code-block:: python

   # Création des caractéristiques (Features)
   df_model = df_final.copy()

   # 1. Caractéristiques Temporelles
   df_model['jour_annee'] = df_model.index.dayofyear
   df_model['mois'] = df_model.index.month

   # 2. Caractéristiques Décalées (Lags)
   for lag in range(1, 8): # On crée 7 jours de lags
       df_model[f'ndvi_lag_{lag}'] = df_model['NDVI'].shift(lag)

   df_model = df_model.dropna() # Supprimer les lignes avec des NaN créés par le shift

.. admonition:: Pourquoi ces caractéristiques ?
   :class: tip

   * **Caractéristiques Temporelles** (`jour_annee`, `mois`) : Elles permettent au modèle d'apprendre les **cycles saisonniers**. Le modèle peut ainsi comprendre que le NDVI est naturellement plus bas en janvier (mois 1) qu'en avril (mois 4).
   * **Caractéristiques Décalées (Lags)** : Ce sont les caractéristiques les plus importantes. `ndvi_lag_1` est la valeur de l'NDVI de la veille. En incluant les 7 derniers jours (`lag_1` à `lag_7`), on donne au modèle un **contexte temporel** pour qu'il comprenne la tendance récente.

**************************************************
Phase 2 : Entraînement et Validation du Modèle
**************************************************

Le jeu de données est divisé en un ensemble d'entraînement (données jusqu'à fin 2023) et un ensemble de test (l'année 2024), permettant une validation temporelle robuste.

.. code-block:: python

   import xgboost as xgb

   # Définir les features (X) et la cible (y)
   features = ['temperature', 'precipitation', 'RH', 'jour_annee', 'mois', 'ndvi_lag_1', ... , 'ndvi_lag_7']
   target = 'NDVI'
   X = df_model[features]
   y = df_model[target]

   # Diviser les données en ensembles d'entraînement et de test
   split_date = '2024-01-01'
   X_train, y_train = X[X.index < split_date], y[y.index < split_date]
   X_test, y_test = X[X.index >= split_date], y[y.index >= split_date]

   # Créer et entraîner le modèle XGBoost
   model = xgb.XGBRegressor(
       objective='reg:squarederror',
       n_estimators=1000,          # Nombre maximal d'arbres
       learning_rate=0.05,
       max_depth=5,
       early_stopping_rounds=50,   # Arrêt précoce pour éviter le surapprentissage
       random_state=42
   )

   model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

.. admonition:: Détails du Modèle XGBoost

   * **`XGBRegressor`** : C'est un algorithme de "gradient boosting" qui construit des modèles de manière séquentielle. Chaque nouvel "arbre de décision" qu'il ajoute tente de corriger les erreurs des précédents, ce qui le rend très performant.
   * **`n_estimators=1000`** : Le modèle va tenter de construire jusqu'à 1000 arbres.
   * **`early_stopping_rounds=50`** : C'est un mécanisme de sécurité crucial contre le **surapprentissage**. Le modèle surveille sa performance sur le jeu de test (`X_test`). Si l'erreur ne s'améliore pas pendant 50 cycles consécutifs, l'entraînement s'arrête automatiquement, en gardant la meilleure version du modèle.

**************************************************
Phase 3 : Évaluation de la Performance
**************************************************
Le modèle est évalué sur ses prédictions pour l'année 2024.

.. code-block:: python

   from sklearn.metrics import mean_absolute_error, mean_squared_error
   import numpy as np

   # Prédictions sur le jeu de test (2024)
   predictions = model.predict(X_test)

   # Métriques d'erreur
   mae = mean_absolute_error(y_test, predictions)
   rmse = np.sqrt(mean_squared_error(y_test, predictions))
   print(f'MAE: {mae:.4f}')
   print(f'RMSE: {rmse:.4f}')


Le **RMSE (Root Mean Squared Error)** est particulièrement utile car il exprime l'erreur dans la même unité que la variable cible (le NDVI). Un RMSE faible indique de bonnes performances.

**************************************************
Phase 4 : Prédictions Futures (Stratégie Récursive)
**************************************************

Pour prédire l'avenir (au-delà des données connues), on utilise une **stratégie récursive**.

.. admonition:: Comment fonctionne la prédiction récursive ?
    :class: important

    1.  Pour prédire le jour 1, le modèle utilise les 7 dernières valeurs **réelles** connues.
    2.  La prédiction pour le jour 1 est générée.
    3.  Pour prédire le jour 2, le modèle utilise les 6 dernières valeurs réelles connues ET la **prédiction du jour 1** comme s'il s'agissait d'une vraie valeur.
    4.  Ce processus se répète : la prédiction de chaque jour est réinjectée dans les données pour prédire le jour suivant.

.. code-block:: python

   # Ré-entraînement du modèle sur TOUTES les données pour la prédiction finale
   full_model = xgb.XGBRegressor(...)
   full_model.fit(X, y, verbose=False)

   # Logique de prédiction récursive
   last_known_lags = list(y.iloc[-7:]) # Initialiser avec les 7 dernières vraies valeurs
   predictions_future = []

   for date in future_dates:
       # ... (création des features du jour, incluant les lags)
       # ... (prédiction du jour)
       
       # Mettre à jour l'historique des lags avec la nouvelle prédiction
       last_known_lags.append(prediction)
       last_known_lags.pop(0)

   # Sauvegarder le modèle final
   full_model.save_model('mon_modele_xgboost.json')


Cette méthode permet de générer des prévisions à long terme, bien que l'incertitude augmente à mesure que l'on s'éloigne des données connues.
