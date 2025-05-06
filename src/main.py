import sexpdata
from pathlib import Path
from models import (
    Footprint,
    Property,
    Polygon,
    Line,
    Pad,
    Layer,
    Point,
    Stroke,
    TextEffects,
    Points,
    SymbolValueModel,
)
from sexpdata import Symbol
from typing import List, Dict, Any, Tuple

footprint_root = Path("~/Documents/repos/kicad-lib-parse/test/samples").expanduser()


def parse_point(xy_data: List[Any]) -> Point:
    """Convert sexpdata point format to Point model."""
    return Point(x=float(xy_data[1]), y=float(xy_data[2]))


def parse_stroke(stroke_data: List[Any]) -> Stroke:
    """Convert sexpdata stroke format to Stroke model."""
    width = float(stroke_data[1][1])
    type_ = stroke_data[2][1]
    return Stroke(width=width, type=type_)


def parse_font_effects(effects_data: List[Any]) -> TextEffects:
    """Convert sexpdata font effects format to FontEffects model."""
    font_data = effects_data[1]
    size = (float(font_data[1][1]), float(font_data[1][2]))
    thickness = float(font_data[2][1])
    justify = effects_data[2][1] if len(effects_data) > 2 else None
    return TextEffects(size=size, thickness=thickness, justify=justify)


def parse_property(prop_data: List[Any]) -> Property:
    """Convert sexpdata property format to Property model."""
    name = prop_data[1]
    value = prop_data[2]
    at = (float(prop_data[3][1]), float(prop_data[3][2]), float(prop_data[3][3]))
    layer = Layer(prop_data[4][1])

    effects = None
    unlocked = None
    hide = None
    uuid = None

    for item in prop_data[5:]:
        if item[0] == "effects":
            effects = parse_font_effects(item[1:])
        elif item[0] == "unlocked":
            unlocked = item[1] == "yes"
        elif item[0] == "hide":
            hide = item[1] == "yes"
        elif item[0] == "uuid":
            uuid = item[1]

    return Property(
        name=name,
        value=value,
        at=at,
        layer=layer,
        effects=effects,
        unlocked=unlocked,
        hide=hide,
        uuid=uuid,
    )


def parse_polygon(poly_data: List[Any]) -> Polygon:
    """Convert sexpdata polygon format to Polygon model."""
    points = Points.from_sexp(poly_data[1])

    stroke = None
    fill = "solid"
    layer = None
    uuid = None

    for item in poly_data[2:]:
        if item[0] == "stroke":
            stroke = parse_stroke(item[1:])
        elif item[0] == "fill":
            fill = item[1]
        elif item[0] == "layer":
            layer = Layer(item[1])
        elif item[0] == "uuid":
            uuid = item[1]

    return Polygon(points=points, stroke=stroke, fill=fill, layer=layer, uuid=uuid)


def parse_line(line_data: List[Any]) -> Line:
    """Convert sexpdata line format to Line model."""
    start = parse_point(line_data[1])
    end = parse_point(line_data[2])
    stroke = parse_stroke(line_data[3][1:])
    layer = Layer(line_data[4][1])
    uuid = line_data[5][1] if len(line_data) > 5 else None

    return Line(start=start, end=end, stroke=stroke, layer=layer, uuid=uuid)


def parse_pad(pad_data: List[Any]) -> Pad:
    """Convert sexpdata pad format to Pad model."""
    number = pad_data[1]
    type_ = pad_data[2]
    shape = pad_data[3]
    at = (float(pad_data[4][1]), float(pad_data[4][2]), float(pad_data[4][3]))
    size = (float(pad_data[5][1]), float(pad_data[5][2]))
    layers = [Layer(layer) for layer in pad_data[6][1:]]

    roundrect_rratio = None
    solder_mask_margin = None
    thermal_bridge_angle = None
    uuid = None

    for item in pad_data[7:]:
        if item[0] == "roundrect_rratio":
            roundrect_rratio = float(item[1])
        elif item[0] == "solder_mask_margin":
            solder_mask_margin = float(item[1])
        elif item[0] == "thermal_bridge_angle":
            thermal_bridge_angle = float(item[1])
        elif item[0] == "uuid":
            uuid = item[1]

    return Pad(
        number=number,
        type=type_,
        shape=shape,
        at=at,
        size=size,
        layers=layers,
        roundrect_rratio=roundrect_rratio,
        solder_mask_margin=solder_mask_margin,
        thermal_bridge_angle=thermal_bridge_angle,
        uuid=uuid,
    )


def parse_kicad_footprint(file_path: Path) -> Footprint:
    """Parse a KiCad footprint file and return a Footprint model."""
    with open(file_path, "r") as f:
        content = f.read()

    data = sexpdata.loads(content)

    # Extract basic footprint information
    name = data[1]
    version = data[2][1]
    generator = data[3][1]
    generator_version = data[4][1]
    layer = Layer(data[5][1])
    description = data[6][1]

    properties = []
    polygons = []
    lines = []
    pads = []

    import code

    code.interact(local=locals())

    # Parse all elements
    for item in data[7:]:
        if item[0] == "property":
            properties.append(parse_property(item[1:]))
        elif item[0] == "fp_poly":
            polygons.append(parse_polygon(item[1:]))
        elif item[0] == "fp_line":
            lines.append(parse_line(item[1:]))
        elif item[0] == "pad":
            pads.append(parse_pad(item[1:]))

    return Footprint(
        name=name,
        version=version,
        generator=generator,
        generator_version=generator_version,
        layer=layer,
        description=description,
        properties=properties,
        polygons=polygons,
        lines=lines,
        pads=pads,
    )


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

    import datetime

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
    output_path = Path(f"{footprint_root}/editted/0603-edit2.kicad_mod")
    write_footprint_to_file(result, output_path)

    import code

    code.interact(local=locals())
