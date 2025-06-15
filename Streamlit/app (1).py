import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import xgboost as xgb
from warnings import filterwarnings
import streamlit.components.v1 as components

# Ignorer les avertissements
filterwarnings("ignore")

# Configuration de la page
st.set_page_config(page_title="Analyse NDVI", layout="wide")

# ===============================
# CHARGEMENT DES DONNÉES
# ===============================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_fusionner_netoyeer.csv")
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date').sort_index()
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.interpolate(method='linear', inplace=True)
        df.bfill(inplace=True)
        if 'NDVI_smoothed' in df.columns:
            df = df.drop(columns=['NDVI_smoothed'])
        return df
    except FileNotFoundError:
        st.error("❌ Fichier 'data_fusionner_netoyeer.csv' introuvable.")
        return None

# ===============================
# CHARGEMENT DES MODÈLES
# ===============================
@st.cache_resource
def load_models():
    models = {}
    st.sidebar.write("--- Chargement des modèles ---")
    try:
        models['SARIMA'] = joblib.load('mon_modele_sarima.joblib')
        st.sidebar.success("✅ SARIMA chargé")
    except FileNotFoundError:
        models['SARIMA'] = None
        st.sidebar.warning("❌ SARIMA introuvable.")
    try:
        models['XGBoost'] = xgb.XGBRegressor()
        models['XGBoost'].load_model('mon_modele_xgboost.json')
        st.sidebar.success("✅ XGBoost chargé")
    except Exception:
        models['XGBoost'] = None
        st.sidebar.error("❌ XGBoost introuvable.")
    return models

# ===============================
# CHARGEMENT GLOBAL
# ===============================
df_final = load_data()
models = load_models()

# ===============================
# NAVIGATION
# ===============================
st.sidebar.title("Navigation")
page = st.sidebar.radio("Choisir une page :", [
    "Accueil & Exploration",
    "Analyse de Corrélation",
    "Comparaison des Modèles",
    "Prédiction avec XGBoost",
    "Assistant Virtuel (JS)"
])

# ===============================
# PAGE 1 : ACCUEIL & EXPLORATION
# ===============================
if page == "Accueil & Exploration":
    st.title("🛰️ Exploration des Données NDVI")
    if df_final is not None:
        st.subheader("NDVI (2018-2024)")
        fig1, ax1 = plt.subplots(figsize=(12, 5))
        df_final['NDVI'].plot(ax=ax1, color='green', grid=True)
        ax1.set_ylabel("NDVI")
        st.pyplot(fig1)

        st.subheader("Facteurs Climatiques")
        fig2, axes = plt.subplots(3, 1, figsize=(12, 9), sharex=True)
        df_final['temperature'].plot(ax=axes[0], title='Température', color='red')
        df_final['precipitation'].plot(ax=axes[1], title='Précipitations', color='blue')
        df_final['RH'].plot(ax=axes[2], title='Humidité Relative', color='purple')
        plt.tight_layout()
        st.pyplot(fig2)

# ===============================
# PAGE 2 : ANALYSE DE CORRÉLATION
# ===============================
elif page == "Analyse de Corrélation":
    st.title("🔗 Corrélation NDVI et Facteurs Climatiques")
    if df_final is not None:
        df_corr = df_final.copy()
        df_corr['NDVI_smoothed'] = df_corr['NDVI'].rolling(window=7, center=True).mean().bfill().ffill()

        st.subheader("1. Corrélation Directe")
        variables = ['NDVI_smoothed', 'precipitation', 'temperature', 'RH']
        corr_matrix = df_corr[variables].corr()

        st.write("Matrice de corrélation directe :")
        st.dataframe(corr_matrix)

        fig3, ax3 = plt.subplots(figsize=(8, 6))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=.5, ax=ax3)
        ax3.set_title("Heatmap Corrélation Directe")
        st.pyplot(fig3)

        st.subheader("2. Corrélation Décalée")
        df_lag = df_corr.copy()
        for lag in [15, 30, 45, 60]:
            df_lag[f'precipitation_lag{lag}'] = df_lag['precipitation'].shift(lag)
        for lag in [7, 15, 30, 45, 60]:
            df_lag[f'temperature_lag{lag}'] = df_lag['temperature'].shift(lag)
            df_lag[f'RH_lag{lag}'] = df_lag['RH'].shift(lag)

        df_lag.dropna(inplace=True)
        corr_lag_matrix = df_lag.corr()

        st.write("Top corrélations avec NDVI (avec lag) :")
        st.dataframe(corr_lag_matrix['NDVI_smoothed'].sort_values(ascending=False))

        if st.checkbox("Afficher la heatmap complète"):
            fig4, ax4 = plt.subplots(figsize=(12, 10))
            sns.heatmap(corr_lag_matrix, cmap='coolwarm', linewidths=0.5, ax=ax4)
            ax4.set_title("Corrélation avec Décalage Temporel")
            st.pyplot(fig4)
    else:
        st.error("Données indisponibles.")

# ===============================
# PAGE 3 : COMPARAISON DES MODÈLES
# ===============================
elif page == "Comparaison des Modèles":
    st.title("📊 Comparaison des Modèles SARIMA / XGBoost / Prophet")

    st.subheader("Erreurs des Modèles")
    try:
        st.image("Capture d'écran 2025-06-14 094221.png")
    except:
        st.warning("Image 1 manquante.")

    st.subheader("Prédictions vs Réalité")
    try:
        st.image("Capture d'écran 2025-06-14 094300.png")
    except:
        st.warning("Image 2 manquante.")

    st.subheader("Distribution des Erreurs")
    try:
        st.image("Capture d'écran 2025-06-14 094807.png")
    except:
        st.warning("Image 3 manquante.")

# ===============================
# PAGE 4 : PRÉDICTION XGBOOST
# ===============================
elif page == "Prédiction avec XGBoost":
    st.title("🔮 Prédiction NDVI - XGBoost")

    if st.button("Lancer la Prédiction pour l'année suivante"):
        if models.get('XGBoost') and df_final is not None and not df_final.empty:
            with st.spinner("Prédiction en cours..."):
                
                FEATURES_ORDER = ['temperature', 'precipitation', 'RH', 'jour_annee', 'mois'] + \
                                 [f'ndvi_lag_{i}' for i in range(1, 8)]

                df_model = df_final.copy()
                df_model['jour_annee'] = df_model.index.dayofyear
                df_model['mois'] = df_model.index.month
                for lag in range(1, 8):
                    df_model[f'ndvi_lag_{lag}'] = df_model['NDVI'].shift(lag)
                df_model.dropna(inplace=True)
                
                y_historique = df_model['NDVI']

                # --- 3. Préparer le DataFrame pour les prédictions futures ---
                
                # =================== BLOC CORRIGÉ ===================
                # On crée un scénario de 365 jours en répétant les données météo disponibles
                # pour éviter l'erreur de longueur.
                
                # 1. Prendre toutes les données météo historiques disponibles
                historical_climate = df_final[['temperature', 'precipitation', 'RH']]
                
                # 2. Répéter les données pour qu'elles couvrent au moins 365 jours
                n_days_available = len(historical_climate)
                if n_days_available > 0:
                    repeats = (365 // n_days_available) + 1
                    tiled_climate_values = np.tile(historical_climate.values, (repeats, 1))
                    
                    # 3. Tronquer pour avoir exactement 365 jours
                    climate_scenario_values = tiled_climate_values[:365]
                else:
                    st.error("Pas de données climatiques disponibles pour la prédiction.")
                    st.stop() # Arrêter l'exécution si aucune donnée

                # ======================================================

                start_date = df_model.index.max() + pd.Timedelta(days=1)
                future_idx = pd.date_range(start=start_date, periods=365)
                future_df = pd.DataFrame(index=future_idx)

                # Assigner les valeurs du scénario qui ont maintenant la bonne taille (365)
                future_df[['temperature', 'precipitation', 'RH']] = climate_scenario_values
                future_df['jour_annee'] = future_df.index.dayofyear
                future_df['mois'] = future_df.index.month
                
                for lag in range(1, 8):
                    future_df[f'ndvi_lag_{lag}'] = 0.0

                # --- 4. Boucle de prédiction itérative ---
                last_lags = list(y_historique.iloc[-7:]) 
                predictions = []

                for date in future_df.index:
                    for i in range(1, 8):
                        future_df.loc[date, f'ndvi_lag_{i}'] = last_lags[-i]
                    
                    X = future_df.loc[[date], FEATURES_ORDER]
                    pred = models['XGBoost'].predict(X)[0]
                    predictions.append(pred)
                    
                    last_lags.append(pred)
                    last_lags.pop(0)

                # --- 5. Afficher les résultats ---
                future_df['NDVI_predicted'] = np.clip(predictions, 0, 1)

                st.subheader("NDVI Prédit vs. Historique")
                fig_pred, ax_pred = plt.subplots(figsize=(15, 6))
                ax_pred.plot(df_model.index, y_historique, label="NDVI Historique", color='blue')
                ax_pred.plot(future_df.index, future_df['NDVI_predicted'], '--', label="NDVI Prédit", color='red')
                ax_pred.set_title("Prédiction du NDVI pour l'année suivante")
                ax_pred.set_xlabel("Date")
                ax_pred.set_ylabel("NDVI")
                ax_pred.legend()
                ax_pred.grid(True)
                st.pyplot(fig_pred)
        else:
            st.error("Modèle XGBoost ou données non disponibles. Veuillez d'abord entraîner le modèle et vous assurer que des données sont chargées.")
# ==============================================================================
# PAGE 6: ASSISTANT VIRTUEL (JS) - VERSION FINALE
# ==============================================================================
elif page == "Assistant Virtuel (JS)":
    st.title("🤖 Assistant Virtuel (Version JavaScript)")
    st.markdown("Ce chatbot s'exécute entièrement dans votre navigateur.")

    try:
        # 1. Charger les données en Python depuis le fichier JSON
        with open('data_chatbot.json', 'r', encoding='utf-8') as f:
            data_as_string = f.read()

        # 2. Charger le template HTML unique
        with open('1.html', 'r', encoding='utf-8') as f:
            html_template = f.read()
        
        # 3. Injecter les données dans le template HTML
        html_code_with_data = html_template.replace('__DATA_JSON__', data_as_string)

        # 4. Afficher le composant HTML final
        components.html(html_code_with_data, height=520, scrolling=True)

    except FileNotFoundError:
        st.error("ERREUR : Assurez-vous que 'chatbot_final.html' et 'data_chatbot.json' sont bien dans le dossier de votre projet.")
    except Exception as e:
        st.error(f"Une erreur inattendue est survenue : {e}")