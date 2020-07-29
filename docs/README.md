# Decomp documentation

To build the documentation, you will need Sphinx and three Sphinx extensions:

```bash
pip install --user sphinx==3.1.2 sphinxcontrib-napoleon sphinx-autodoc-typehints sphinx_rtd_theme
```

Then, while in this directory, use:

```bash
make clean
make html
```

To view the built documentation, start a python http server with:


```bash
python3 -m http.server
```

Then, navigate to [http://localhost:8000/build/html/](http://localhost:8000/build/html/) in your browser.
