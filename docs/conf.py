# -- Project information -----------------------------------------------------
project = 'Analyse et Prédiction Temporelle du NDVI pour la Région Fès-Meknès'
copyright = '2025, SAAD ELKHADER  ET  ASMAE ELHAKIOUI'
author = 'SAAD ELKHADER  ET  ASMAE ELHAKIOUI'

# -- Imports -----------------------------------------------------------------
import sphinx_rtd_theme

# -- General configuration ---------------------------------------------------
extensions = []
templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
language = 'fr'

# -- Options for HTML output -------------------------------------------------
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_static_path = ['_static']

# -- nbsphinx execution (optional) -------------------------------------------
nbsphinx_execute = 'auto'

