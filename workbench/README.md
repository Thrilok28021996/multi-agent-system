# MyProject

A modern Python project with a standard project structure.

## Project Structure

```
myproject/
├── pyproject.toml          # Project manifest & build configuration
├── README.md               # This file
├── .gitignore              # Git ignore patterns
├── LICENSE                 # License file
├── src/
│   └── myproject/
│       ├── __init__.py     # Package initialization
│       └── main.py         # Main entry point
├── tests/
│   ├── __init__.py
│   └── test_main.py        # Unit tests
├── docs/                   # Documentation
│   └── .gitkeep
└── .github/
    └── workflows/
        └── tests.yml       # CI configuration
```

## Installation

### Development Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/myproject.git
cd myproject

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Usage

After installation, you can run the project via:

```bash
myproject
```

Or as a Python module:

```bash
python -m myproject
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=myproject
```

## Development

- Format code: `black src/ tests/`
- Lint code: `flake8 src/ tests/`
- Type check: `mypy src/`

## License

MIT
