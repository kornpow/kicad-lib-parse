import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import sexpdata
from sexpdata import Symbol

from models import (
    Footprint,
    Layer,
    Line,
    Pad,
    Point,
    Points,
    Polygon,
    Property,
    Stroke,
    SymbolValueModel,
    TextEffects,
)

footprint_root = Path("~/Documents/repos/kicad-lib-parse/test/samples").expanduser()


def main():
    # Example usage
    footprint_path = Path(f"{footprint_root}/0603.kicad_mod")
    if footprint_path.exists():
        footprint = parse_kicad_footprint(footprint_path)
        print("Footprint parsed successfully!")
        return footprint
    else:
        print(f"File not found: {footprint_path}")
        return None


def my_parse():
    footprint_path = Path(f"{footprint_root}/0603.kicad_mod")
    with open(footprint_path, "r") as f:
        content = f.read()

    data = sexpdata.loads(content)

    version_model = SymbolValueModel.from_sexp(data[2], "version")
    generator_model = SymbolValueModel.from_sexp(data[3], "generator")
    generator_version_model = SymbolValueModel.from_sexp(data[4], "generator_version")
    layer_model = Layer.from_sexp_list(data[5])
    description_model = SymbolValueModel.from_sexp(data[6], "descr")
    ref_property = Property.from_sexp(data[7])
    value_property = Property.from_sexp(data[8])
    footprint_property = Property.from_sexp(data[9])
    datasheet_property = Property.from_sexp(data[10])
    description_property = Property.from_sexp(data[11])
    poly1 = Polygon.from_sexp(data[12])
    line1 = Line.from_sexp(data[13])
    line2 = Line.from_sexp(data[14])
    line3 = Line.from_sexp(data[15])
    line4 = Line.from_sexp(data[16])
    line5 = Line.from_sexp(data[17])
    line6 = Line.from_sexp(data[18])
    poly2 = Polygon.from_sexp(data[19])
    poly3 = Polygon.from_sexp(data[20])
    pad1 = Pad.from_sexp(data[21])
    pad1.size = (1.7, 1.5)
    pad2 = Pad.from_sexp(data[22])
    pad2.size = (0.5, 3)

    # Join all models into a single s-expression list
    sexp_list = [
        Symbol("footprint"),
        f"0603-edit-{datetime.datetime.now().timestamp()}",  # Added timestamp using datetime
        version_model.to_sexp(wrap_symbol=True),
        generator_model.to_sexp(),
        generator_version_model.to_sexp(),
        layer_model.to_sexp(),
        description_model.to_sexp(),
        ref_property.to_sexp(),
        value_property.to_sexp(),
        footprint_property.to_sexp(),
        datasheet_property.to_sexp(),
        description_property.to_sexp(),
        poly1.to_sexp(),
        line1.to_sexp(),
        line2.to_sexp(),
        line3.to_sexp(),
        line4.to_sexp(),
        line5.to_sexp(),
        line6.to_sexp(),
        poly2.to_sexp(),
        poly3.to_sexp(),
        pad1.to_sexp(),
        pad2.to_sexp(),
    ]

    # Convert the list to a string representation
    sexp_str = sexpdata.dumps(sexp_list)
    print(sexp_str)
    return sexp_list

    # import code
    # code.interact(local={**locals(), **globals()})


def write_footprint_to_file(footprint_list: List[Any], output_path: Path) -> None:
    """Write a footprint list to a sexp file format.

    Args:
        footprint_list: List containing the footprint data in sexp format
        output_path: Path where the file should be written
    """
    # Convert the list to a string representation
    sexp_str = sexpdata.dumps(footprint_list)

    # Write to file
    with open(output_path, "w") as f:
        f.write(sexp_str)


if __name__ == "__main__":
    # data = main()
    result = my_parse()

    # Write the modified footprint to a new file
    output_path = Path(f"{footprint_root}/editted/0603-edit3.kicad_mod")
    write_footprint_to_file(result, output_path)

    import code

    code.interact(local=locals())
