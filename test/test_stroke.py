import sexpdata
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent))
from src.models import Stroke
from sexpdata import Symbol


def test_parse_stroke_basic():
    """Test basic stroke parsing with required attributes."""
    sample_path = Path(__file__).parent / "samples" / "stroke.sexp"
    with open(sample_path, "r") as f:
        content = f.read()

    data = sexpdata.loads(content)
    stroke = Stroke.from_sexp(data)

    assert stroke.width == 0.1016
    assert stroke.type == "solid"
    assert stroke.color is None


def test_parse_stroke_full():
    """Test stroke parsing with all attributes including color."""
    sample_path = Path(__file__).parent / "samples" / "stroke_full.sexp"
    with open(sample_path, "r") as f:
        content = f.read()

    data = sexpdata.loads(content)
    stroke = Stroke.from_sexp(data)

    assert stroke.width == 0.1016
    assert stroke.type == "dash"
    assert stroke.color == (255, 0, 0, 255)


def test_stroke_types():
    """Test all valid stroke types."""
    valid_types = ["default", "solid", "dash", "dot", "dash_dot", "dash_dot_dot"]

    for type_ in valid_types:
        data = ["stroke", ["width", "0.1"], ["type", type_]]
        stroke = Stroke.from_sexp(data)
        assert stroke.type == type_


def test_stroke_validation():
    """Test stroke validation and error cases."""
    # Test invalid width
    try:
        data = ["stroke", ["width", "invalid"], ["type", "solid"]]
        Stroke.from_sexp(data)
        assert False, "Should raise ValueError for invalid width"
    except ValueError:
        pass

    # Test invalid type
    try:
        data = ["stroke", ["width", "0.1"], ["type", "invalid_type"]]
        Stroke.from_sexp(data)
        assert False, "Should raise ValueError for invalid type"
    except ValueError:
        pass

    # Test invalid color values
    try:
        data = [
            "stroke",
            ["width", "0.1"],
            ["type", "solid"],
            ["color", "255", "invalid", "0", "255"],
        ]
        Stroke.from_sexp(data)
        assert False, "Should raise ValueError for invalid color values"
    except ValueError:
        pass


def test_stroke_roundtrip():
    """Test roundtrip conversion of stroke data."""
    # Test basic stroke
    data = [Symbol("stroke"), [Symbol("width"), "0.1016"], [Symbol("type"), "solid"]]
    stroke = Stroke.from_sexp(data)
    sexp = stroke.to_sexp()
    assert sexp[0] == Symbol("stroke")
    assert sexp[1][0] == Symbol("width")
    assert float(sexp[1][1]) == 0.1016
    assert sexp[2][0] == Symbol("type")
    assert sexp[2][1] == "solid"

    # Test stroke with color
    data = [
        Symbol("stroke"),
        [Symbol("width"), "0.1016"],
        [Symbol("type"), "dash"],
        [Symbol("color"), "255", "0", "0", "255"],
    ]
    stroke = Stroke.from_sexp(data)
    sexp = stroke.to_sexp()
    assert sexp[0] == Symbol("stroke")
    assert sexp[1][0] == Symbol("width")
    assert float(sexp[1][1]) == 0.1016
    assert sexp[2][0] == Symbol("type")
    assert sexp[2][1] == "dash"
    assert sexp[3][0] == Symbol("color")
    assert [str(x) for x in sexp[3][1:]] == ["255", "0", "0", "255"]


if __name__ == "__main__":
    test_parse_stroke_basic()
    test_parse_stroke_full()
    test_stroke_types()
    test_stroke_validation()
    test_stroke_roundtrip()
    print("All tests passed!")
