###########################################################
Guide de Démarrage avec Streamlit
###########################################################

**Streamlit** est une bibliothèque open-source en Python qui permet de créer et de partager des applications web personnalisées pour la data science et le machine learning avec une simplicité déconcertante.

Ce guide vous montrera les étapes fondamentales pour installer Streamlit, créer votre première application interactive et la lancer.

****************************************
Phase 1 : Installation
****************************************

L'installation de Streamlit se fait très facilement via `pip`, le gestionnaire de paquets de Python.

1.1. Prérequis
================

Assurez-vous d'avoir **Python** (version 3.8 ou supérieure) et **pip** installés sur votre système.

1.2. Commande d'Installation
==============================

Ouvrez votre terminal ou votre invite de commandes et tapez la commande suivante :

.. code-block:: bash

   pip install streamlit

Cette commande va télécharger et installer Streamlit ainsi que toutes ses dépendances.

1.3. Vérifier l'Installation
==============================
Pour vous assurer que tout fonctionne correctement, vous pouvez lancer l'application de démonstration de Streamlit.

.. code-block:: bash

   streamlit hello

Une nouvelle page devrait s'ouvrir dans votre navigateur web, vous présentant une application de bienvenue. Cela confirme que l'installation a réussi.

**************************************************
Phase 2 : Créer Votre Première Application
**************************************************

Une application Streamlit n'est rien de plus qu'un simple script Python.

2.1. Créer le Fichier
======================
Créez un nouveau fichier Python. Nommons-le `mon_app.py`.

2.2. Écrire le Code
====================
Copiez le code suivant dans votre fichier `mon_app.py`. Cet exemple simple crée une page interactive qui vous salue.

.. code-block:: python

   # mon_app.py
   import streamlit as st
   import pandas as pd

   # 1. Titre et introduction
   st.title("Mon Application Interactive avec Streamlit")
   st.header("Bienvenue sur ma première application !")
   st.write("Cette application simple démontre quelques fonctionnalités de base de Streamlit.")

   # 2. Widget interactif : un curseur (slider)
   st.subheader("Section Interactive")
   age = st.slider("Quel est votre âge ?", min_value=0, max_value=130, value=25, step=1)

   st.write(f"Vous avez sélectionné {age} ans.")

   # 3. Widget interactif : un bouton
   # L'action n'est déclenchée que si l'on clique sur le bouton
   if st.button("Cliquez ici pour voir un message"):
       st.success(f"Merci d'avoir cliqué ! Vous avez {age} ans.")
   else:
       st.info("En attente d'un clic sur le bouton.")

   # 4. Afficher des données
   st.subheader("Affichage de Données")
   st.write("On peut facilement afficher des DataFrames Pandas :")

   # Création d'un DataFrame simple pour l'exemple
   df = pd.DataFrame({
       'Variable': ['Température', 'Humidité', 'Précipitations'],
       'Valeur': [25, 60, 5]
   })
   st.dataframe(df)


**************************************************
Phase 3 : Lancer l'Application
**************************************************

Une fois votre script sauvegardé, la dernière étape est de le lancer.

3.1. La Commande `run`
=======================
Retournez dans votre terminal, assurez-vous d'être dans le même dossier que votre fichier `mon_app.py`, et tapez la commande :

.. code-block:: bash

   streamlit run mon_app.py

3.2. Que se passe-t-il ?
=========================
1.  Streamlit démarre un petit serveur web local sur votre machine.
2.  Un nouvel onglet s'ouvre automatiquement dans votre navigateur par défaut.
3.  Votre application apparaît !

.. admonition:: Le "Magic Loop" de Streamlit
   :class: important

   La force de Streamlit est son rechargement automatique. Chaque fois que vous **modifiez et sauvegardez** votre fichier `mon_app.py`, l'application dans votre navigateur vous proposera de se relancer ("Rerun") pour afficher instantanément vos modifications. C'est idéal pour un développement rapide et itératif.

**************************************************
Conclusion
**************************************************

Vous avez maintenant toutes les clés pour démarrer avec Streamlit. Vous avez appris à :
* **Installer** la bibliothèque.
* **Créer** une application avec du texte, des titres et des widgets interactifs comme des sliders et des boutons.
* **Afficher** des données structurées comme des DataFrames Pandas.
* **Lancer** votre application localement.

À partir de là, vous pouvez explorer les nombreux autres widgets disponibles (`st.selectbox`, `st.file_uploader`, etc.) et commencer à construire des tableaux de bord pour vos propres projets de data science.
