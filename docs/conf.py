# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

import os
import sys

import sphinx_bootstrap_theme

sys.path.insert(0, os.path.abspath('../'))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Talky Trader'
copyright = '2022'
author = 'mraniki'


# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',  
    "sphinx.ext.intersphinx",
]


# -- Extension configuration ---------------------------------------------------

intersphinx_mapping = {
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    # - :doc:`sphinx:usage/extensions/intersphinx`
    "dynaconf": ("https://www.dynaconf.com", None),
    "python": ("https://docs.python.org/3", None),
    "talky": ("https://talky.readthedocs.io/en/latest/", None),
    "talky-dev": ("https://talky.readthedocs.io/en/dev/", None),
    "findmyorder": ("https://talky.readthedocs.io/projects/findmyorder/en/latest", None),
    "dxsp": ("https://talky.readthedocs.io/projects/dxsp/en/latest", None),
    "iamlistening": ("https://talky.readthedocs.io/projects/iamlistening/en/latest", None),
    "talkytrend": ("https://talky.readthedocs.io/projects/talkytrend/en/latest", None),
    "myllm": ("https://talky.readthedocs.io/projects/myllm/en/latest", None),
}

intersphinx_disabled_reftypes = ["*"]

napoleon_google_docstring = True
autosummary_generate = True
autoclass_content = 'both'
autodoc_inherit_docstrings = True 
set_type_checking_flag = True 
autodoc_member_order = 'bysource'
add_module_names = True

master_doc = 'index'
source_suffix = ['.rst', '.md']
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------


html_theme = "bootstrap"

html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_static_path = ["_static"]
html_logo = '_static/favicon.png'
html_favicon = '_static/favicon.ico'
html_css_files = [
    "custom.css",
]
html_show_sphinx = False
html_theme_options = {
    'navbar_title': " ",
    'navbar_site_name': "Talky",
    'navbar_sidebarrel': False,
    'navbar_pagenav': False,
    'globaltoc_depth': 4,
    'globaltoc_includehidden': "true",
    'navbar_class': "navbar",
    'navbar_fixed_top': "true",
    'source_link_position': "none",

    'bootswatch_theme': "darkly",
    'bootstrap_version': "3",

    # 'navbar_links': [
    #     ("TalkyTrader", "https://talkytrader.github.io/wiki/",True),
    #     ("_menu",  "🗿 Talky",[
    #         ("🪙 Get started",  "https://talky.rtfd.io/01_start",True),
    #         ("⚙️ Config",  "https://talky.rtfd.io/02_config",True),
    #     ]),
    #     ("_menu",  "🔌 Plugins",[
    #         ("👂 IamListening",  "https://iamlistening.rtfd.io/", True),
    #         ("🔎 FindMyOrder",  "https://findmyorder.rtfd.io/", True),
    #         ("⛓️ DXSP", "https://dxsp.rtfd.io/00_index_dxsp", True),
    #         ("💱 CEX",  "index",True),
    #         ("💁 Helper",  "index",True),
    #         ("📰 Talkytrend",  "https://talkytrend.rtfd.io/", True),
    #     ]),
    #     ("_menu",  "➕ More",[
    #         ("🆕 What's new?",  "https://github.com/mraniki/tt",True),
    #         ("💬 Connect",  "https://talky.rtfd.io",True),
    #     ]),
    # ]

}




def setup(app):
    app.add_css_file("custom.css")
