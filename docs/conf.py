# Configuration file for the Sphinx documentation builder.

project = 'AutoDataSetBuilder'
copyright = '2024, Raja Muhammad Awais'
author = 'Raja Muhammad Awais'
release = '0.1.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx_autodoc_typehints',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

# Master document
master_doc = 'index'

# Templates path
templates_path = ['_templates']

# Source suffix
source_suffix = '.rst'

# HTML theme
html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': 'blob',
    'style_nav_header_background': '#2980B9',
}

# HTML output options
html_static_path = ['_static']
html_logo = '../architecture.png'

# Autodoc options
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'show-inheritance': True,
}

# Napoleon options for Google-style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_attr_annotations = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'boto3': ('https://boto3.amazonaws.com/v1/documentation/api/latest/', None),
}

# LaTeX options
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '11pt',
}

# Exclude patterns
exclude_patterns = ['_build']

# Language
language = 'en'

# Syntax highlighting
pygments_style = 'sphinx'

# Suppress warnings
suppress_warnings = ['toctree.ref']
