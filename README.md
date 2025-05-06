# KiCad Library Parser

A Python library for parsing KiCad library files.

## Features

- Parse KiCad library files
- Convert between KiCad library formats
- Validate library files
- Generate library files

## Installation

```bash
pip install kicad-lib-parse
```

## Usage

```python
from kicad_lib_parse import parse_library

# Parse a library file
library = parse_library("path/to/library.kicad_mod")
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
  - [Pull Requests](https://github.com/sparkfun/SparkFun-KiCad-Libraries/pulls) - View and contribute to SparkFun KiCad Libraries

## License
MIT

## Example KiCad Libraries
