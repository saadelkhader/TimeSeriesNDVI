###########################################################
Modélisation Avancée avec LSTM
###########################################################

Cette section détaille la construction, l'entraînement et l'utilisation d'un modèle de réseau de neurones récurrents de type **LSTM (Long Short-Term Memory)** pour la prédiction de séries temporelles.

Contrairement aux modèles statistiques comme SARIMA, les modèles LSTM peuvent apprendre des relations complexes et non linéaires à partir de multiples variables d'entrée (multivariées). L'objectif est de prédire la valeur future du NDVI en se basant sur son historique récent et les conditions climatiques.

**************************************************
Phase 1 : Préparation des Données pour le LSTM
**************************************************

Les réseaux de neurones sont sensibles à l'échelle des données et nécessitent une structuration spécifique des entrées sous forme de "séquences".

1.1. Nettoyage et Normalisation
================================

Avant tout, les données sont nettoyées pour s'assurer qu'il n'y a pas de valeurs manquantes ou infinies. Ensuite, elles sont normalisées.

.. admonition:: Pourquoi Normaliser les Données ?
   :class: important

   La normalisation, généralement entre 0 et 1, est une étape cruciale pour les réseaux de neurones. Elle garantit que toutes les variables (NDVI, température, etc.) ont une échelle comparable. Sans cela, les variables avec des ordres de grandeur plus élevés (comme la température) pourraient dominer le processus d'apprentissage, rendant le modèle instable et plus lent à converger.

.. code-block:: python

   from sklearn.preprocessing import MinMaxScaler

   # ... (chargement et nettoyage initial du DataFrame df_final) ...

   # Normaliser toutes les colonnes entre 0 et 1
   scaler = MinMaxScaler()
   data_scaled = scaler.fit_transform(df_final)

   # Créer un scaler séparé juste pour la colonne NDVI
   # Il sera utilisé plus tard pour dé-normaliser les prédictions
   scaler_ndvi = MinMaxScaler()
   scaler_ndvi.fit(df_final[['NDVI']])

1.2. Création de Séquences Temporelles
=======================================
Les LSTMs ne traitent pas les données point par point, mais analysent une **séquence d'observations passées** pour prédire la suivante. Une fonction est créée pour transformer nos données en ces séquences.

.. code-block:: python

   # lookback: le nombre de pas de temps passés à utiliser pour prédire le pas de temps futur.
   lookback = 60

   def create_sequences(data, lookback):
       X, y = [], []
       for i in range(len(data) - lookback):
           # X contient une séquence de 'lookback' jours avec toutes les variables
           X.append(data[i:(i + lookback), :])
           # y est la valeur du NDVI du jour suivant la séquence
           y.append(data[i + lookback, 0]) # 0 est l'index de la colonne NDVI
       return np.array(X), np.array(y)

   # Créer les séquences
   X_seq, y_seq = create_sequences(data_scaled, lookback)

   # Diviser en ensembles d'entraînement et de test
   split_index = int(len(X_seq) * 0.8)
   X_train, X_test = X_seq[:split_index], X_seq[split_index:]
   y_train, y_test = y_seq[:split_index], y_seq[split_index:]


.. admonition:: Le concept de "Fenêtre Glissante"
   :class: tip

   Avec un `lookback` de 60, la fonction `create_sequences` crée des "fenêtres glissantes".
   * La première séquence `X[0]` contient les données des jours 1 à 60, et la cible `y[0]` est le NDVI du jour 61.
   * La deuxième séquence `X[1]` contient les données des jours 2 à 61, et la cible `y[1]` est le NDVI du jour 62.
   * Et ainsi de suite...

**************************************************
Phase 2 : Architecture et Entraînement du Modèle
**************************************************

Le modèle est construit avec Keras, une API de haut niveau de TensorFlow.

.. code-block:: python

   from tensorflow.keras.models import Sequential
   from tensorflow.keras.layers import LSTM, Dense, Dropout

   model_lstm = Sequential([
       # Couche LSTM principale avec 70 neurones (unités de mémoire)
       LSTM(70, input_shape=(X_train.shape[1], X_train.shape[2])),

       # Couche de Dropout pour éviter le surapprentissage
       Dropout(0.2),

       # Couche Dense intermédiaire
       Dense(35),

       # Couche de sortie avec 1 neurone pour la prédiction du NDVI
       Dense(1)
   ])

   # Compilation du modèle
   model_lstm.compile(optimizer='adam', loss='mean_squared_error')

   # Entraînement
   history = model_lstm.fit(X_train, y_train,
                  batch_size=32, epochs=60,
                  validation_data=(X_test, y_test),
                  verbose=0)


.. admonition:: Détails de l'Architecture

    * **`LSTM(70, ...)`** : C'est le cœur du modèle. Cette couche est capable de mémoriser les informations des 60 jours de la séquence d'entrée pour détecter des motifs temporels.
    * **`Dropout(0.2)`** : Technique de régularisation qui "désactive" aléatoirement 20% des neurones à chaque étape d'entraînement. Cela force le réseau à apprendre des caractéristiques plus robustes et réduit le risque de surapprentissage.
    * **`Dense(1)`** : La couche finale qui agrège les informations pour produire une seule valeur de sortie : la prédiction du NDVI.
    * **`optimizer='adam'`** et **`loss='mean_squared_error'`** : Adam est un optimiseur efficace et populaire. La MSE est la fonction de coût standard pour les problèmes de régression.


**************************************************
Phase 3 : Validation et Prédictions Futures
**************************************************

3.1. Validation sur les Données de Test
=========================================
Le modèle est évalué sur l'ensemble de test (données qu'il n'a jamais vues pendant l'entraînement) pour vérifier sa capacité de généralisation.

.. admonition:: L'importance de la dé-normalisation
    :class: important

    Le modèle prédit des valeurs normalisées (entre 0 et 1). Pour interpréter les résultats et les erreurs, il est crucial de les "dé-normaliser" en utilisant le `scaler_ndvi` créé à l'étape 1, afin de les ramener à l'échelle originale du NDVI.

.. code-block:: python

   from sklearn.metrics import mean_absolute_error, mean_squared_error

   # Prédictions sur le jeu de test
   predictions_scaled = model_lstm.predict(X_test)

   # Dénormalisation
   predictions = scaler_ndvi.inverse_transform(predictions_scaled)
   y_test_real = scaler_ndvi.inverse_transform(y_test.reshape(-1, 1))

   # Calcul des métriques d'erreur
   mae = mean_absolute_error(y_test_real, predictions)
   rmse = np.sqrt(mean_squared_error(y_test_real, predictions))


.. image:: _static/votre_image_validation_lstm.png
   :alt: Validation du modèle LSTM sur les données de test
   :align: center
   :width: 90%

   *Figure 1 : Comparaison entre les valeurs réelles (bleu) et les prédictions du modèle (orange) sur l'ensemble de test.*


3.2. Prédiction Future (Stratégie Récursive)
==============================================
Pour prédire l'avenir, une stratégie récursive est mise en place. Le modèle utilise ses propres prédictions pour construire la séquence du jour suivant.

.. code-block:: python

   # On récupère la dernière séquence de données réelles
   last_sequence = data_scaled[-lookback:]
   future_predictions = []
   current_sequence = last_sequence.copy()

   # On estime le climat futur en utilisant la moyenne historique pour chaque jour de l'année
   dayofyear_map = df_final.groupby(df_final.index.dayofyear)[['temperature', 'precipitation', 'RH']].mean()
   # ... (code pour remplir les jours manquants du template climatique)

   # Boucle de prédiction jour par jour
   for i in range(365):
       # Prédire le jour suivant à partir de la séquence actuelle
       next_pred_scaled = model_lstm.predict(current_sequence[np.newaxis, :, :], verbose=0)
       
       # ... (code pour construire le vecteur du jour futur en combinant le NDVI prédit et le climat estimé) ...
       
       # On met à jour la séquence : on enlève le jour le plus ancien et on ajoute le nouveau jour
       current_sequence = np.vstack([current_sequence[1:], next_day_vector])

   # Dénormaliser la prédiction finale
   future_predictions_real = scaler_ndvi.inverse_transform(...)

.. image:: _static/votre_image_prediction_finale_lstm.png
   :alt: Prédiction future du NDVI avec le modèle LSTM
   :align: center
   :width: 90%

   *Figure 2 : Prédiction du NDVI pour les 365 prochains jours, basée sur la stratégie récursive.*
