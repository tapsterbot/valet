# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Valet'
copyright = '© 2024 Tapster Robotics, Inc.'
author = 'Tapster Robotics, Inc.'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

templates_path = ['_templates']
exclude_patterns = []

extensions = [
    "sphinx_design",
    "myst_parser"
]

myst_enable_extensions = [
  "colon_fence",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'shibuya'
html_static_path = ['_static']



html_theme_options = {  
    "github_url": "https://github.com/tapsterbot",
    "twitter_url": "https://twitter.com/tapsterbot"
}

# This is needed to render custom domain correctly on GitHub Pages
html_extra_path = ['CNAME']

html_show_copyright = True
html_show_sphinx = False