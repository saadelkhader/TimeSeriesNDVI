import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import xgboost as xgb
from warnings import filterwarnings

# Ignorer les avertissements pour un affichage plus propre
filterwarnings("ignore")

# --- Configuration de la page ---
st.set_page_config(page_title="Analyse NDVI", layout="wide")

# --- Fonctions mises en cache pour la performance ---
@st.cache_data
def load_data():
    """Charge et nettoie les données une seule fois."""
    try:
        # NOTE : J'ai adapté le nom du fichier à celui que vous avez mentionné dans votre code
        df = pd.read_csv("data_fusionner_netoyeer.csv") 
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        # Interpolation et remplissage pour gérer les valeurs manquantes
        df.interpolate(method='linear', inplace=True)
        df.bfill(inplace=True)
        # On supprime la colonne smoothed si elle existe pour la recalculer au besoin
        if 'NDVI_smoothed' in df.columns:
            df = df.drop(columns=['NDVI_smoothed'])
        return df
    except FileNotFoundError:
        st.error("ERREUR : Le fichier 'data_fusionner_netoyeer.csv' est introuvable. Assurez-vous qu'il est dans le même dossier que app.py.")
        return None

@st.cache_resource
def load_models():
    """Charge les modèles pré-entraînés."""
    models = {}
    st.sidebar.write("--- Chargement des modèles ---")
    try:
        models['SARIMA'] = joblib.load('mon_modele_sarima.joblib')
        st.sidebar.success("✅ SARIMA chargé")
    except FileNotFoundError:
        models['SARIMA'] = None
        st.sidebar.warning("Fichier SARIMA non trouvé.")
    try:
        models['XGBoost'] = xgb.XGBRegressor()
        models['XGBoost'].load_model('mon_modele_xgboost.json')
        st.sidebar.success("✅ XGBoost chargé")
    except Exception:
        models['XGBoost'] = None
        st.sidebar.error("Fichier XGBoost introuvable.")
    return models

# --- Chargement initial ---
df_final = load_data()
models = load_models()

# --- Barre de navigation latérale ---
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Aller à la page :", 
    ["Accueil & Exploration", 
     "Analyse de Corrélation", # Page ajoutée ici
     "Comparaison des Modèles", 
     "Prédiction avec XGBoost"]
)

# ==============================================================================
# PAGE 1: ACCUEIL & EXPLORATION
# ==============================================================================
if page == "Accueil & Exploration":
    st.title("🛰️ Exploration des Données NDVI et Climatiques")
    if df_final is not None:
        st.subheader("Variation de l'indice NDVI (2018-2024)")
        fig_ndvi, ax_ndvi = plt.subplots(figsize=(12, 5))
        df_final['NDVI'].plot(ax=ax_ndvi, color='green', grid=True, ylabel="NDVI")
        st.pyplot(fig_ndvi)
        
        st.subheader("Variation des facteurs d'influence")
        fig_factors, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
        df_final['temperature'].plot(ax=axes[0], title='Température', color='red', grid=True, ylabel='°C')
        df_final['precipitation'].plot(ax=axes[1], title='Précipitations', color='blue', grid=True, ylabel='mm')
        df_final['RH'].plot(ax=axes[2], title='Humidité Relative', color='purple', grid=True, ylabel='%')
        plt.tight_layout()
        st.pyplot(fig_factors)

# ==============================================================================
# --- PAGE 5: ANALYSE DE CORRÉLATION (Nouvelle Page) ---
# ==============================================================================
elif page == "Analyse de Corrélation":
    st.title("🔗 Analyse de Corrélation : Comprendre les Liens")
    st.markdown("""
    Cette page exécute dynamiquement le code pour analyser les relations entre la végétation (NDVI) et les facteurs climatiques.
    """)

    if df_final is not None:
        # Création d'une copie pour ne pas modifier le DataFrame original
        df_corr = df_final.copy()
        # L'analyse de corrélation se base sur un NDVI lissé, nous le recréons
        df_corr['NDVI_smoothed'] = df_corr['NDVI'].rolling(window=7, center=True).mean().bfill().ffill()
        
        st.markdown("---")
        
        # --- Section 1: Corrélation Directe ---
        st.subheader("1. Corrélation Directe")
        st.write("Analyse des liens directs entre les variables, sans prendre en compte les décalages temporels.")

        with st.spinner("Calcul de la corrélation directe..."):
            colonnes_pour_correlation = ['NDVI_smoothed', 'precipitation', 'temperature', 'RH']
            df_pour_correlation = df_corr[colonnes_pour_correlation]
            matrice_correlation = df_pour_correlation.corr()

            # Affichage de la matrice de données
            st.write("**Matrice de Corrélation :**")
            st.dataframe(matrice_correlation)

            # Affichage de la heatmap
            fig_heatmap, ax_heatmap = plt.subplots(figsize=(8, 6))
            sns.heatmap(matrice_correlation,
                        annot=True,
                        cmap='coolwarm',
                        fmt=".2f",
                        linewidths=.5,
                        ax=ax_heatmap)
            ax_heatmap.set_title('Heatmap de Corrélation entre NDVI et Variables Météo')
            st.pyplot(fig_heatmap)

        st.markdown("---")
        
        # --- Section 2: Corrélation Décalée ---
        st.subheader("2. Corrélation avec Décalage Temporel (Lag)")
        st.write("Analyse plus approfondie qui prend en compte le temps de réponse de la végétation aux facteurs climatiques.")

        with st.spinner("Calcul de la corrélation décalée..."):
            df_lag = df_corr.copy()
            lags_precipitation = [15, 30, 45, 60]
            lags_temperature = [7, 15, 30, 45, 60]
            lags_rh = [7, 15, 30, 45, 60]

            for lag in lags_precipitation:
                df_lag[f'precipitation_lag{lag}'] = df_lag['precipitation'].shift(lag)
            for lag in lags_temperature:
                df_lag[f'temperature_lag{lag}'] = df_lag['temperature'].shift(lag)
            for lag in lags_rh:
                df_lag[f'RH_lag{lag}'] = df_lag['RH'].shift(lag)
            
            df_lag.dropna(inplace=True)

            colonnes_pour_lag_correlation = ['NDVI_smoothed', 'precipitation', 'temperature', 'RH'] + \
                                            [f'precipitation_lag{lag}' for lag in lags_precipitation] + \
                                            [f'temperature_lag{lag}' for lag in lags_temperature] + \
                                            [f'RH_lag{lag}' for lag in lags_rh]
            
            matrice_correlation_lag = df_lag[colonnes_pour_lag_correlation].corr()

            st.write("**Classement des facteurs les plus corrélés au NDVI (avec décalage) :**")
            st.dataframe(matrice_correlation_lag['NDVI_smoothed'].sort_values(ascending=False))

            if st.checkbox("Afficher la heatmap complète des corrélations décalées (grande)"):
                fig_heatmap_lag, ax_heatmap_lag = plt.subplots(figsize=(12, 10))
                sns.heatmap(matrice_correlation_lag, annot=False, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax_heatmap_lag)
                ax_heatmap_lag.set_title('Heatmap de Corrélation avec Décalage Temporel')
                st.pyplot(fig_heatmap_lag)

    else:
        st.error("Les données n'ont pas pu être chargées. Impossible d'effectuer l'analyse.")
# ==============================================================================
# PAGE 2: COMPARAISON DES MODÈLES (REMPLACÉE PAR APERÇU DE L'APPLICATION)
# ==============================================================================
elif page == "Comparaison des Modèles":
    # J'ai adapté le titre pour mieux correspondre au nouveau contenu
    st.title("Comparaison entre les 3 Modèles") 
   

    st.markdown("---")

    # --- Section 1: Le Tableau de Bord ---
    st.subheader(" Comparaison des erreurs des models ")
   
    try:
        st.image("Capture d'écran 2025-06-14 094221.png")
    except FileNotFoundError:
        st.error("ERREUR : L'image 'Capture d'écran 2025-06-14 094221.png' est introuvable.")

    st.markdown("---")

    # --- Section 2: L'outil de prédiction ---
    st.subheader("Comparaison de models vs realite ")
    
    try:
        st.image("Capture d'écran 2025-06-14 094300.png")
    except FileNotFoundError:
        st.error("ERREUR : L'image 'Capture d'écran 2025-06-14 094300.png' est introuvable.")

    st.markdown("---")

    # --- Section 3: L'interprétabilité ---
    st.subheader("Distribution des erreures par MODEL ")
    
    try:
        st.image("Capture d'écran 2025-06-14 094807.png")
    except FileNotFoundError:
        st.error("ERREUR : L'image 'Capture d'écran 2025-06-14 094807.png' est introuvable.")
# ==============================================================================
# --- PAGE 3: PRÉDICTION AVEC XGBOOST (VERSION CORRIGÉE ET FINALE) ---
# ==============================================================================
elif page == "Prédiction avec XGBoost":
    st.title("🔮 Prédiction avec le Meilleur Modèle : XGBoost")
    st.markdown("Utilisation du modèle XGBoost pour prédire l'année suivante en se basant sur un scénario climatique réaliste.")
    
    if st.button("Lancer la Prédiction pour l'année suivante"):
        if models['XGBoost'] and df_final is not None:
             with st.spinner('Génération de la prédiction en cours...'):
                # --- CORRECTION APPLIQUÉE ICI ---
                # On s'assure de préparer les données avec le bon nombre de lags (7)
                
                df_model = df_final.copy()
                df_model['jour_annee'] = df_final.index.dayofyear
                df_model['mois'] = df_final.index.month
                # On utilise 7 lags, comme pour l'entraînement
                for lag in range(1, 8): 
                    df_model[f'ndvi_lag_{lag}'] = df_model['NDVI'].shift(lag)
                df_model = df_model.dropna()
                
                # On définit la liste de features avec 7 lags
                features_pred = ['temperature', 'precipitation', 'RH', 'jour_annee', 'mois'] + [f'ndvi_lag_{i}' for i in range(1,8)]
                y = df_model['NDVI']

                # La logique de scénario reste la même
                climat_scenario = df_final[['temperature', 'precipitation', 'RH']].tail(365)
                last_date = df_model.index.max()
                start_prediction_date = last_date + pd.Timedelta(days=1)
                future_dates = pd.date_range(start=start_prediction_date, periods=len(climat_scenario), freq='D')
                future_df = pd.DataFrame(index=future_dates)
                future_df[['temperature', 'precipitation', 'RH']] = climat_scenario.values
                future_df['jour_annee'] = future_df.index.dayofyear
                future_df['mois'] = future_df.index.month
                
                # On prend les 7 dernières valeurs connues pour démarrer
                last_known_lags = list(y.iloc[-7:]) 
                predictions_future = []

                # Boucle de prédiction
                for date in future_df.index:
                    # On crée les 7 lags pour le jour à prédire
                    for i in range(1, 8): 
                        future_df.loc[date, f'ndvi_lag_{i}'] = last_known_lags[-i]
                    
                    current_features = future_df.loc[[date]][features_pred]
                    prediction = models['XGBoost'].predict(current_features)[0]
                    predictions_future.append(prediction)
                    
                    last_known_lags.append(prediction)
                    last_known_lags.pop(0)
                
                future_df['NDVI_predicted'] = predictions_future
                future_df['NDVI_predicted'] = future_df['NDVI_predicted'].clip(0, 1)

                # Affichage du graphique
                st.subheader("Résultat de la Prédiction")
                fig_pred, ax_pred = plt.subplots(figsize=(15, 7))
                ax_pred.plot(df_model.index, df_model['NDVI'], label='NDVI Historique')
                ax_pred.plot(future_df.index, future_df['NDVI_predicted'], label='NDVI Prédit', linestyle='--')
                ax_pred.set_title("Prédiction Finale avec XGBoost", fontsize=16)
                ax_pred.legend()
                ax_pred.grid(True)
                st.pyplot(fig_pred)
        else:
            st.error("Le modèle XGBoost ou les données ne sont pas chargés.")
