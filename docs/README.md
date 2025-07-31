# Decomp Documentation

This directory contains the source files for building the Decomp documentation using Sphinx.

## Prerequisites

First, install the decomp package in development mode from the parent directory:

```bash
cd ..
pip install -e ".[dev]"
cd docs
```

Then install the documentation-specific dependencies:

```bash
pip install -r requirements.txt
```

This will install:
- Sphinx (documentation generator)
- sphinx-autodoc-typehints (automatic type hint documentation)
- furo (modern documentation theme)
- sphinx-copybutton (adds copy buttons to code blocks)
- sphinx-design (enhanced design elements)
- sphinx-togglebutton (collapsible sections)
- myst-parser (Markdown support)

## Building the Documentation

### Build HTML Documentation

To build the HTML documentation:

```bash
make html
```

The built documentation will be in `build/html/`.

### Clean and Rebuild

To clean the build directory and rebuild from scratch:

```bash
make clean
make html
```

## Viewing the Documentation

### Method 1: Simple HTTP Server

To serve the documentation locally:

```bash
python -m http.server --directory build/html 8000
```

Then open your browser to http://localhost:8000

### Method 2: Auto-rebuild During Development

For development with automatic rebuilding when files change:

```bash
pip install sphinx-autobuild
sphinx-autobuild source build/html
```

This will:
- Serve the documentation at http://localhost:8000
- Watch for changes in the source files
- Automatically rebuild and refresh your browser

## Other Build Formats

Sphinx can build documentation in various formats:

```bash
make latexpdf  # Build PDF documentation (requires LaTeX)
make epub      # Build EPUB format
make json      # Build JSON format
make text      # Build plain text format
```

## Documentation Structure

- `source/` - Source files for the documentation
  - `conf.py` - Sphinx configuration file
  - `index.rst` - Main documentation index
  - `tutorial/` - Tutorial pages
  - `package/` - API documentation (auto-generated)
  - `_static/` - Static files (CSS, images)
  - `_ext/` - Custom Sphinx extensions
- `build/` - Built documentation (git-ignored)
- `requirements.txt` - Python dependencies for building docs
- `Makefile` - Build commands for Unix/Linux/macOS
- `make.bat` - Build commands for Windows

## Troubleshooting

If you encounter issues:

1. **ImportError**: Make sure you've installed the package in development mode:
   ```bash
   cd ..
   pip install -e ".[dev]"
   ```

2. **Theme not found**: Ensure all requirements are installed:
   ```bash
   pip install -r requirements.txt
   ```

3. **Build warnings**: Sphinx treats warnings as errors by default. To build despite warnings:
   ```bash
   make html SPHINXOPTS=""
   ```

## Contributing to Documentation

When adding new documentation:

1. Write new pages in reStructuredText (`.rst`) format in the appropriate directory
2. Add new pages to the relevant `index.rst` file's table of contents
3. For API documentation, ensure your code has proper docstrings
4. Run `make clean && make html` to test your changes
5. Check for any warnings or errors in the build output