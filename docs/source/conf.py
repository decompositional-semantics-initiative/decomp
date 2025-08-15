# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/config

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = 'Decomp'
copyright = '2020-2025, Aaron Steven White'
author = 'Aaron Steven White'

# The full version, including alpha/beta/rc tags
release = '0.3.2'
version = '0.3.2'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # Core Sphinx extensions
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    
    # Type hints support
    'sphinx_autodoc_typehints',
    
    # Modern UI enhancements
    'sphinx_copybutton',
    'sphinx_design',
    'sphinx_togglebutton',
    
    # Additional parsing
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The master toctree document.
master_doc = 'index'

# -- Options for autodoc -----------------------------------------------------

# General autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Type hints configuration
autodoc_typehints = 'description'  # Show type hints in description, not signature
autodoc_typehints_format = 'short'  # Suppress module names (e.g., io.StringIO -> StringIO)
autodoc_typehints_description_target = 'documented'
autodoc_class_signature = 'separated'
autodoc_type_aliases = {
    'ArrayLike': 'numpy.typing.ArrayLike',
}

# Don't add module names to signatures
add_module_names = False
python_use_unqualified_type_names = True

# Suppress specific warnings
suppress_warnings = [
    'autodoc.import_object',  # Suppress import warnings for optional dependencies
]

# -- Napoleon settings -------------------------------------------------------

napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None
napoleon_attr_annotations = True

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'networkx': ('https://networkx.org/documentation/stable/', None),
    'rdflib': ('https://rdflib.readthedocs.io/en/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
}

# Cache intersphinx inventories for 5 days
intersphinx_cache_limit = 5

# Disable certain reference types from intersphinx
intersphinx_disabled_reftypes = ['std:doc']

# -- sphinx-autodoc-typehints configuration ----------------------------------

# Additional configuration for sphinx-autodoc-typehints
typehints_defaults = 'comma'
typehints_use_signature = False
typehints_use_signature_return = False
typehints_fully_qualified = False

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.
html_theme = 'furo'

# Theme options
html_theme_options = {
    # Furo specific options
    "light_css_variables": {
        "color-brand-primary": "#1976d2",
        "color-brand-content": "#1976d2",
        "color-api-background": "#f8f9fa",
        "color-api-background-hover": "#efeff0",
    },
    "dark_css_variables": {
        "color-brand-primary": "#64b5f6",
        "color-brand-content": "#64b5f6",
        "color-api-background": "#1a1a1a",
        "color-api-background-hover": "#2a2a2a",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Custom CSS files
html_css_files = [
    'custom.css',
]

# Custom sidebar templates
html_sidebars = {
    "**": [
        "sidebar/brand.html",
        "sidebar/search.html",
        "sidebar/scroll-start.html",
        "sidebar/navigation.html",
        "sidebar/ethical-ads.html",
        "sidebar/scroll-end.html",
    ]
}

# Logo and favicon
# html_logo = "_static/logo.png"
# html_favicon = "_static/favicon.ico"

# Output file base name for HTML help builder
htmlhelp_basename = 'decompdoc'

# -- Code highlighting -------------------------------------------------------

# The name of the Pygments (syntax highlighting) style to use
pygments_style = 'friendly'
pygments_dark_style = 'monokai'

# Default language for code blocks
highlight_language = 'python3'

# -- Copy button configuration -----------------------------------------------

# Patterns to exclude from copy button
copybutton_exclude = '.linenos, .gp, .go'
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- MyST parser configuration -----------------------------------------------

myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "html_image",
]

# -- Additional configuration ------------------------------------------------

# Suppress specific warnings
suppress_warnings = [
    'autodoc.import_object',
    'ref.python',  # Suppress warnings about Python references
]

# Nitpicky mode - ensure all references can be resolved
nitpicky = False
nitpick_ignore = [
    ('py:class', 'optional'),
    ('py:class', '_io.StringIO'),
    ('py:class', 'typing.Any'),
    ('py:class', 'decomp.semantics.uds.types.TypeAliasType'),
    ('py:class', 'decomp.syntax.dependency.TypeAliasType'),
    ('py:class', 'UDSSubspace'),
    ('py:obj', 'decomp.syntax.dependency.ConllData'),
    ('py:class', 'dash.dash.Dash'),
]

# -- Build configuration -----------------------------------------------------

# Parallel builds
numfig = True

# Keep warnings as warnings
keep_warnings = False

# Show todos
todo_include_todos = False