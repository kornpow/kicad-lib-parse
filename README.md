# KiCad Library Parser

A Python library for parsing KiCad library files. This tool allows for parsing and modification of KiCAD footprint files (other KiCad files supported in the future).


![Basic Footprint Example](img/basic_footprint_example.png)

## Features

- Parse KiCad library files
- Modify KiCad library files
- Validate library files
- Generate library files

## Installation

```bash
pip install kicad-lib-parse
# OR
uv sync
```

## Basic Usage

Currently, `main.py` will:
- Open a sample [`0603` footprint](test/samples/0603.kicad_mod).
- Parse the footprint into pydantic model.
- Modify the part, add pads, move around some lines, update a polygon.
- Writes the properly formatted data to a file, which can be opened by KiCAD.


```bash
uv run python3 src/main.py
```



## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/kornpow/kicad-lib-parse.git
cd kicad-lib-parse

# Install development dependencies
uv sync --all-groups
```

### Testing

```bash
# Run tests
pytest
```

Setup precommit hooks:
```
# setup the hook, using configuration from .pre-commit-config.yaml
pre-commit install


# Run the hook manually
# Full test suite / pre-commit-hook
# black, mypy, flake8
pre-commit run --all-files
```

## Related Projects

- [SparkFun KiCad Libraries](https://github.com/sparkfun/SparkFun-KiCad-Libraries) - A collection of KiCad libraries for SparkFun products
- [Sparkfun KiCad Boards](https://github.com/kornpow/sparkfun-kicad) - Manually converted to KiCad format

## License
MIT
