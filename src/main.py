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
    FontEffects,
    Points,
)
from typing import List, Dict, Any, Tuple

footprint_root = Path(
    "~/Downloads/SparkFun_dToF-TMF8820_v10/SparkFun_dToF-TMF8820/SparkFun_dToF-TMF8820.pretty"
).expanduser()


def parse_point(xy_data: List[Any]) -> Point:
    """Convert sexpdata point format to Point model."""
    return Point(x=float(xy_data[1]), y=float(xy_data[2]))


def parse_stroke(stroke_data: List[Any]) -> Stroke:
    """Convert sexpdata stroke format to Stroke model."""
    width = float(stroke_data[1][1])
    type_ = stroke_data[2][1]
    return Stroke(width=width, type=type_)


def parse_font_effects(effects_data: List[Any]) -> FontEffects:
    """Convert sexpdata font effects format to FontEffects model."""
    font_data = effects_data[1]
    size = (float(font_data[1][1]), float(font_data[1][2]))
    thickness = float(font_data[2][1])
    justify = effects_data[2][1] if len(effects_data) > 2 else None
    return FontEffects(size=size, thickness=thickness, justify=justify)


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


if __name__ == "__main__":
    data = main()
    import code

    code.interact(local=locals())
