import pytest
from src.models import Polygon, Points, Point, Stroke, Layer, StrokeType
from sexpdata import Symbol


def test_polygon_from_sexp():
    """Test parsing polygon from s-expression."""
    # Test basic polygon
    sexp = [
        Symbol("fp_poly"),
        [
            Symbol("pts"),
            [Symbol("xy"), -0.1999, 0.3],
            [Symbol("xy"), 0.1999, 0.3],
            [Symbol("xy"), 0.1999, -0.3],
            [Symbol("xy"), -0.1999, -0.3],
        ],
        [Symbol("stroke"), [Symbol("width"), 0], [Symbol("type"), "default"]],
        "solid",
        "F.Adhes",
        [Symbol("uuid"), "4730c81d-f4ad-4788-8015-fd6db48f4259"],
    ]

    poly = Polygon.from_sexp(sexp)
    assert len(poly.points.points) == 4
    assert poly.points.points[0].x == -0.1999
    assert poly.points.points[0].y == 0.3
    assert poly.stroke.width == 0
    assert poly.stroke.type == StrokeType.DEFAULT
    assert poly.fill == "solid"
    assert poly.layer == Layer.F_ADHES
    assert poly.uuid == "4730c81d-f4ad-4788-8015-fd6db48f4259"


def test_polygon_to_sexp():
    """Test converting polygon to s-expression."""
    # Create a polygon
    points = Points(
        points=[
            Point(x=-0.1999, y=0.3),
            Point(x=0.1999, y=0.3),
            Point(x=0.1999, y=-0.3),
            Point(x=-0.1999, y=-0.3),
        ]
    )
    stroke = Stroke(width=0, type=StrokeType.DEFAULT)
    poly = Polygon(
        points=points,
        stroke=stroke,
        fill="solid",
        layer=Layer.F_ADHES,
        uuid="4730c81d-f4ad-4788-8015-fd6db48f4259",
    )

    # Convert to s-expression
    sexp = poly.to_sexp()

    # Verify the structure
    assert sexp[0] == Symbol("fp_poly")
    assert sexp[1][0] == Symbol("pts")
    assert len(sexp[1]) == 5  # pts + 4 points
    assert sexp[2][0] == Symbol("stroke")
    assert sexp[2][1][0] == Symbol("width")
    assert float(sexp[2][1][1]) == 0.0  # Compare as float
    assert sexp[2][2][0] == Symbol("type")
    assert sexp[2][2][1] == "default"
    assert sexp[3] == "solid"
    assert sexp[4] == "F.Adhes"
    assert sexp[5][0] == Symbol("uuid")
    assert sexp[5][1] == "4730c81d-f4ad-4788-8015-fd6db48f4259"


def test_polygon_invalid_sexp():
    """Test handling of invalid s-expressions."""
    # Test missing required components
    with pytest.raises(ValueError, match="Invalid polygon data format"):
        Polygon.from_sexp([Symbol("fp_poly"), [Symbol("pts")]])

    # Test invalid format
    with pytest.raises(
        ValueError, match="Polygon data must start with 'fp_poly' symbol"
    ):
        Polygon.from_sexp(
            [
                Symbol("not_a_polygon"),
                [Symbol("pts")],
                [Symbol("stroke"), [Symbol("width"), "0"], [Symbol("type"), "default"]],
                "solid",
                "F.Adhes",
            ]
        )

    # Test invalid fill type
    with pytest.raises(ValueError, match="Invalid fill type"):
        Polygon.from_sexp(
            [
                Symbol("fp_poly"),
                [
                    Symbol("pts"),
                    [Symbol("xy"), 0, 0],
                    [Symbol("xy"), 1, 0],
                    [Symbol("xy"), 1, 1],
                    [Symbol("xy"), 0, 1],
                ],
                [Symbol("stroke"), [Symbol("width"), "0"], [Symbol("type"), "default"]],
                "invalid_fill",
                "F.Adhes",
            ]
        )

    # Test invalid layer
    with pytest.raises(ValueError, match="'InvalidLayer' is not a valid Layer"):
        Polygon.from_sexp(
            [
                Symbol("fp_poly"),
                [
                    Symbol("pts"),
                    [Symbol("xy"), 0, 0],
                    [Symbol("xy"), 1, 0],
                    [Symbol("xy"), 1, 1],
                    [Symbol("xy"), 0, 1],
                ],
                [Symbol("stroke"), [Symbol("width"), "0"], [Symbol("type"), "default"]],
                "solid",
                "InvalidLayer",
            ]
        )
