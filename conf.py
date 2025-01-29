# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "JasonGrace2282's Blog"
copyright = "%Y, Aarush Deshpande"
author = "Aarush Deshpande"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "ablog",
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.intersphinx",
]

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    ".venv",
    "venv",
    "env",
    ".env",
    ".git",
    ".github",
    "README.md",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"

html_theme_options = {
    "search_bar_text": "Search this site...",
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/JasonGrace2282/",
            "icon": "fa-brands fa-github",
        },
    ],
}
html_sidebars = {
    "index": ["hello.html"],
    "about": ["hello.html"],
}

html_static_path = ["_static"]
html_title = "JasonGrace2282"

blog_baseurl = "https://jasongrace2282.github.io"
blog_title = "Aarush Deshpande"
blog_authors = {
    "Aarush": ("Aarush Deshpande", "https://github.com/JasonGrace2282"),
}
blog_post_pattern = "blog/**/*"
blog_feed_fulltext = True
blog_feed_subtitle = "Developing and having fun"
fontawesome_included = True
post_redirect_refresh = 1
post_auto_image = 1
post_auto_excerpt = 2


# myst

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
]

myst_update_mathjax = False


def setup(app):
    app.add_css_file("custom.css")
