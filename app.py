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
     "Comparaison des Modèles", 
     "Prédiction avec XGBoost", 
     "Interprétation du Modèle"]
)

# ==============================================================================
# PAGE 1: ACCUEIL & EXPLORATION
# ==============================================================================
if page == "Accueil & Exploration":
    st.title("🛰️ Exploration des Données NDVI et Climatiques")
    if df_final is not None:
        # ... (Le code de cette page reste identique)
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
# PAGE 2: COMPARAISON DES MODÈLES
# ==============================================================================
elif page == "Comparaison des Modèles":
    st.title("📊 Comparaison des Performances des Modèles")
    st.markdown("Évaluation des modèles sur la période de test (2024).")
    
    if models['SARIMA'] and models['XGBoost']:
        with st.spinner("Génération de la comparaison..."):
            split_date = '2024-01-01'
            df_weekly = df_final['NDVI'].resample('W').mean().interpolate().bfill()
            test_sarima = df_weekly[df_weekly.index >= split_date]
            
            df_model = df_final.copy()
            df_model['jour_annee'] = df_model.index.dayofyear
            df_model['mois'] = df_model.index.month
            for lag in range(1, 8):
                df_model[f'ndvi_lag_{lag}'] = df_model['NDVI'].shift(lag)
            df_model = df_model.dropna()
            
            features = [
                'temperature', 'precipitation', 'RH', 
                'jour_annee', 'mois',
                'ndvi_lag_1', 'ndvi_lag_2', 'ndvi_lag_3', 'ndvi_lag_4', 
                'ndvi_lag_5', 'ndvi_lag_6', 'ndvi_lag_7'
            ]
            X_test = df_model[features][df_model.index >= split_date]

            df_results = pd.DataFrame({'NDVI_Reel': test_sarima})
            df_results['SARIMA'] = models['SARIMA'].get_forecast(steps=len(test_sarima)).predicted_mean
            pred_xgb_daily = pd.Series(models['XGBoost'].predict(X_test), index=X_test.index)
            df_results['XGBoost'] = pred_xgb_daily.resample('W').mean()
            df_results.dropna(inplace=True)

            st.subheader("Graphique comparatif des prédictions")
            fig_comp, ax_comp = plt.subplots(figsize=(15, 7))
            ax_comp.plot(df_results['NDVI_Reel'], label='NDVI Réel (2024)', color='black', linewidth=2)
            ax_comp.plot(df_results['SARIMA'], label='SARIMA', linestyle='--')
            ax_comp.plot(df_results['XGBoost'], label='XGBoost', linestyle='--')
            ax_comp.set_title('Comparaison des Prédictions vs Réalité (2024)')
            ax_comp.legend()
            ax_comp.grid(True)
            st.pyplot(fig_comp)
    else:
        st.error("Les modèles SARIMA et XGBoost doivent être chargés pour effectuer la comparaison.")
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
# =# ==============================================================================
# --- PAGE 4: INTERPRÉTATION DU MODÈLE (VERSION CORRIGÉE) ---
# ==============================================================================
elif page == "Interprétation du Modèle":
    st.title("💡 Interprétation : Quels facteurs influencent le plus l'NDVI ?")
    st.markdown("Grâce au modèle XGBoost, nous pouvons classer les variables par ordre d'importance pour comprendre ce qui pilote la santé de la végétation.")

    # Vérifier que le modèle XGBoost est bien chargé
    if models['XGBoost']:
        try:
            # --- Affichage de l'importance des features (comme avant) ---
            feature_names = models['XGBoost'].feature_names_in_
            feature_importances = models['XGBoost'].feature_importances_
            feature_importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': feature_importances
            }).sort_values('importance', ascending=False)
            
            st.subheader("Classement des facteurs d'influence")
            fig_imp, ax_imp = plt.subplots(figsize=(10, 8))
            sns.barplot(x='importance', y='feature', data=feature_importance_df.head(10), ax=ax_imp)
            ax_imp.set_title('Top 10 des caractéristiques les plus importantes')
            st.pyplot(fig_imp)

            # --- Section pour l'analyse SHAP avancée ---
            st.subheader("Analyse Approfondie avec SHAP")
            st.info("SHAP nous montre non seulement QUELS facteurs sont importants, mais aussi COMMENT ils influencent la prédiction (positivement ou négativement).")

            if st.button("Lancer l'analyse SHAP (peut prendre du temps)"):
                with st.spinner("Installation de SHAP et calcul des valeurs..."):
                    import subprocess
                    import sys
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'shap'])
                    import shap
                    
                    # On prépare les données exactement comme pour l'entraînement
                    df_model_shap = df_final.copy()
                    df_model_shap['jour_annee'] = df_final.index.dayofyear
                    df_model_shap['mois'] = df_final.index.month
                    for lag in range(1, 8):
                        df_model_shap[f'ndvi_lag_{lag}'] = df_model_shap['NDVI'].shift(lag)
                    df_model_shap = df_model_shap.dropna()
                    
                    # --- LA CORRECTION EST ICI ---
                    # On redéfinit la liste des 'features' pour que cette section du code la connaisse
                    features = [
                        'temperature', 'precipitation', 'RH', 'jour_annee', 'mois'
                    ] + [f'ndvi_lag_{i}' for i in range(1, 8)]
                    # --- FIN DE LA CORRECTION ---

                    X_shap = df_model_shap[features]
                    
                    st.write("Calcul des valeurs SHAP...")
                    explainer = shap.TreeExplainer(models['XGBoost'])
                    shap_values = explainer.shap_values(X_shap)
                    
                    st.write("Génération du graphique SHAP...")
                    fig_shap, ax_shap = plt.subplots(figsize=(10, 8))
                    shap.summary_plot(shap_values, X_shap, plot_type='dot', show=False)
                    st.pyplot(fig_shap)
                    st.success("Analyse SHAP terminée.")

        except Exception as e:
            st.error(f"Une erreur est survenue lors de la génération de l'interprétation : {e}")
    else:
        st.warning("Le modèle XGBoost n'est pas chargé. Veuillez l'importer.")