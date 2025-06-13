import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import xgboost as xgb
import seaborn as sns

# --- Configuration de la page ---
st.set_page_config(page_title="Prédiction NDVI", layout="wide")

# --- Fonctions mises en cache pour la performance ---

# Charger les données (mis en cache pour ne le faire qu'une fois)
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data_fusionner_netoyeer.csv")
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        # Nettoyage robuste
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df.interpolate(method='linear', inplace=True)
        df.bfill(inplace=True)
        if 'NDVI_smoothed' in df.columns:
            df = df.drop(columns=['NDVI_smoothed'])
        return df
    except FileNotFoundError:
        st.error("ERREUR : Le fichier 'data_fusionner_netoyeer.csv' est introuvable. Assurez-vous qu'il est dans le même dossier que app.py.")
        return None

# Charger le modèle (mis en cache pour ne le faire qu'une fois)
@st.cache_resource
def load_model():
    try:
        model = xgb.XGBRegressor()
        model.load_model('mon_modele_xgboost.json')
        return model
    except Exception as e:
        st.error(f"ERREUR : Le fichier modèle 'mon_modele_xgboost.json' est introuvable ou corrompu. {e}")
        return None

# --- Interface de l'application ---

st.title("🛰️ Tableau de Bord de Prédiction de l'Indice NDVI")
st.markdown("Cette application utilise un modèle **XGBoost** pour analyser et prédire l'évolution de l'indice de végétation (NDVI) dans la région de Fès-Meknès.")

# Charger les données et le modèle
df_final = load_data()
full_model = load_model()

if df_final is not None:
    # --- Section 1: Visualisation des données historiques ---
    st.header("1. Exploration des Données Historiques")
    if st.checkbox("Afficher les données brutes"):
        st.write(df_final)

    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    df_final['NDVI'].plot(ax=axes[0], title='NDVI', color='green', grid=True)
    df_final['temperature'].plot(ax=axes[1], title='Température', color='red', grid=True)
    df_final['precipitation'].plot(ax=axes[2], title='Précipitations', color='blue', grid=True)
    df_final['RH'].plot(ax=axes[3], title='Humidité Relative', color='purple', grid=True)
    plt.tight_layout()
    st.pyplot(fig)

    # --- Section 2: Prédiction ---
    st.header("2. Prédiction pour l'Année Suivante")
    st.markdown("Cliquez sur le bouton ci-dessous pour lancer la prédiction. Le modèle utilisera le climat de la dernière année connue comme scénario pour le futur.")

    if st.button("Lancer la Prédiction"):
        if full_model is not None:
            with st.spinner('Génération de la prédiction en cours...'):
                # Préparer les données pour le modèle
                df_model = df_final.copy()
                df_model['jour_annee'] = df_model.index.dayofyear
                df_model['mois'] = df_model.index.month
                for lag in range(1, 15):
                    df_model[f'ndvi_lag_{lag}'] = df_model['NDVI'].shift(lag)
                df_model = df_model.dropna()
                
                features = [col for col in df_model.columns if col != 'NDVI']
                y = df_model['NDVI']

                # Logique de prédiction
                climat_scenario = df_final[['temperature', 'precipitation', 'RH']].tail(365)
                last_date = df_model.index.max()
                start_prediction_date = last_date + pd.Timedelta(days=1)
                future_dates = pd.date_range(start=start_prediction_date, periods=len(climat_scenario), freq='D')
                future_df = pd.DataFrame(index=future_dates)
                future_df[['temperature', 'precipitation', 'RH']] = climat_scenario.values
                future_df['jour_annee'] = future_df.index.dayofyear
                future_df['mois'] = future_df.index.month

                last_known_lags = list(y.iloc[-14:])
                predictions_future = []

                for date in future_df.index:
                    for i in range(1, 15):
                        future_df.loc[date, f'ndvi_lag_{i}'] = last_known_lags[-i]
                    current_features = future_df.loc[[date]][features]
                    prediction = full_model.predict(current_features)[0]
                    predictions_future.append(prediction)
                    last_known_lags.append(prediction)
                    last_known_lags.pop(0)

                future_df['NDVI_predicted'] = predictions_future
                future_df['NDVI_predicted'] = future_df['NDVI_predicted'].clip(0, 1)

                # Afficher le graphique final
                st.subheader("Résultat de la Prédiction")
                fig_pred, ax_pred = plt.subplots(figsize=(15, 7))
                ax_pred.plot(df_model.index, df_model['NDVI'], label='NDVI Historique', color='royalblue')
                ax_pred.plot(future_df.index, future_df['NDVI_predicted'], label='NDVI Prédit', linestyle='--', color='darkorange')
                ax_pred.set_title("Prédiction Finale avec XGBoost et Scénario Climatique", fontsize=16)
                ax_pred.legend()
                ax_pred.grid(True)
                st.pyplot(fig_pred)
        else:
            st.error("Le modèle n'a pas pu être chargé. Impossible de faire une prédiction.")

    # --- Section 3: Importance des Facteurs ---
    st.header("3. Quels facteurs influencent le plus l'NDVI ?")
    if full_model is not None:
        feature_importance = pd.DataFrame({
            'feature': full_model.feature_names_in_,
            'importance': full_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        fig_imp, ax_imp = plt.subplots(figsize=(10, 8))
        sns.barplot(x='importance', y='feature', data=feature_importance.head(10), ax=ax_imp)
        ax_imp.set_title('Top 10 des caractéristiques les plus importantes')
        st.pyplot(fig_imp)