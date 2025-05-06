import pytest
from pathlib import Path
import sexpdata
from src.models import (
    FootprintModel,
    Layer,
    Property,
    Polygon,
    Line,
    Pad,
    Points,
    Point,
    Stroke,
)
from sexpdata import Symbol


def test_footprint_from_sexp():
    """Test parsing footprint from s-expression."""
    # Read the sample file
    sample_path = Path(__file__).parent / "samples" / "0603.kicad_mod"
    with open(sample_path, "r") as f:
        content = f.read()

    # Parse the sexpdata
    data = sexpdata.loads(content)

    # Create FootprintModel
    footprint = FootprintModel.from_sexp(data)

    # Verify basic attributes
    assert footprint.name == "0603"
    assert footprint.version == "20240108"
    assert footprint.generator == "pcbnew"
    assert footprint.generator_version == "8.0"
    assert footprint.layer == Layer.F_CU
    assert "Generic 1608 (0603) package" in footprint.description

    # Verify properties
    assert len(footprint.properties) == 5
    ref_prop = next(p for p in footprint.properties if p.key == "Reference")
    assert ref_prop.value == "REF**"
    assert ref_prop.uuid == "314dcf13-2e3b-4297-bfe7-41e232820fd9"

    # Verify polygons
    assert len(footprint.polygons) == 3
    adhes_poly = next(p for p in footprint.polygons if p.layer == Layer.F_ADHES)
    assert len(adhes_poly.points.points) == 4
    assert adhes_poly.fill == "solid"
    assert adhes_poly.uuid == "4730c81d-f4ad-4788-8015-fd6db48f4259"

    # Verify lines
    assert len(footprint.lines) == 6
    crtyd_lines = [l for l in footprint.lines if l.layer == Layer.F_CRTYD]
    assert len(crtyd_lines) == 4

    # Verify pads
    assert len(footprint.pads) == 2
    pad1 = next(p for p in footprint.pads if p.number == "1")
    assert pad1.type == "smd"
    assert pad1.shape == "roundrect"
    assert pad1.uuid == "b5f44151-f7b6-4818-aa7a-f2f8a749283e"


def test_footprint_to_sexp():
    """Test converting footprint to s-expression."""
    # Create a footprint
    footprint = FootprintModel(
        name="0603",
        version="20240108",
        generator="pcbnew",
        generator_version="8.0",
        layer=Layer.F_CU,
        description="Test footprint",
        properties=[
            Property(key="Reference", value="REF**"),
            Property(key="Value", value="0603"),
        ],
        polygons=[
            Polygon(
                points=Points(
                    points=[
                        Point(x=-0.1999, y=0.3),
                        Point(x=0.1999, y=0.3),
                        Point(x=0.1999, y=-0.3),
                        Point(x=-0.1999, y=-0.3),
                    ]
                ),
                stroke=Stroke(width=0, type="default"),
                fill="solid",
                layer=Layer.F_ADHES,
            )
        ],
    )

    # Convert to s-expression
    sexp = footprint.to_sexp()

    # Verify the structure
    assert sexp[0] == Symbol("footprint")
    assert sexp[1] == "0603"
    assert sexp[2] == [Symbol("version"), "20240108"]
    assert sexp[3] == [Symbol("generator"), "pcbnew"]
    assert sexp[4] == [Symbol("generator_version"), "8.0"]
    assert sexp[5] == [Symbol("layer"), "F.Cu"]
    assert sexp[6] == [Symbol("descr"), "Test footprint"]

    # Verify properties
    assert sexp[7][0] == Symbol("property")
    assert sexp[7][1] == "Reference"
    assert sexp[7][2] == "REF**"

    # Verify polygon
    assert sexp[9][0] == Symbol("fp_poly")
    assert sexp[9][1][0] == Symbol("pts")
    assert len(sexp[9][1]) == 5  # pts + 4 points
