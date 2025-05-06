import pytest

from src.models import PositionIdentifier


# Test data fixtures
@pytest.fixture
def basic_test_cases():
    return [
        ("(at 1.0 2.0)", PositionIdentifier(x=1.0, y=2.0)),
        ("(at 1.0 2.0 90)", PositionIdentifier(x=1.0, y=2.0, angle=90.0)),
    ]


@pytest.fixture
def whitespace_test_cases():
    return [
        ("(at  1.0   2.0  )", PositionIdentifier(x=1.0, y=2.0)),
        ("(at 1.0 2.0 45.5)", PositionIdentifier(x=1.0, y=2.0, angle=45.5)),
    ]


@pytest.fixture
def negative_test_cases():
    return [
        ("(at -1.0 -2.0)", PositionIdentifier(x=-1.0, y=-2.0)),
        ("(at -1.0 -2.0 -90)", PositionIdentifier(x=-1.0, y=-2.0, angle=-90.0)),
    ]


@pytest.fixture
def error_test_cases():
    return [
        ("(at)", "Position identifier must have 2 or 3 components"),
        ("(at 1.0)", "Position identifier must have 2 or 3 components"),
        ("(at 1.0 2.0 3.0 4.0)", "Position identifier must have 2 or 3 components"),
        ("(at x y)", "Invalid numeric values in position identifier"),
        ("at 1.0 2.0", "Invalid position identifier format"),
    ]


# Test functions
def test_basic_parsing(basic_test_cases):
    """Test basic position identifier parsing."""
    for sexpr, expected in basic_test_cases:
        result = PositionIdentifier.from_sexpr(sexpr)
        assert result == expected


def test_whitespace_variations(whitespace_test_cases):
    """Test parsing with different whitespace patterns."""
    for sexpr, expected in whitespace_test_cases:
        result = PositionIdentifier.from_sexpr(sexpr)
        assert result == expected


def test_negative_values(negative_test_cases):
    """Test parsing with negative values."""
    for sexpr, expected in negative_test_cases:
        result = PositionIdentifier.from_sexpr(sexpr)
        assert result == expected


def test_round_trip_conversion():
    """Test that converting to sexpr and back produces the same result."""
    test_cases = [
        PositionIdentifier(x=1.0, y=2.0),
        PositionIdentifier(x=1.0, y=2.0, angle=90.0),
        PositionIdentifier(x=-1.0, y=-2.0),
        PositionIdentifier(x=-1.0, y=-2.0, angle=-90.0),
    ]

    for original in test_cases:
        sexpr = original.to_sexpr()
        result = PositionIdentifier.from_sexpr(sexpr)
        assert result == original


@pytest.mark.parametrize(
    "sexpr,expected_error",
    [
        ("(at)", "Position identifier must have 2 or 3 components"),
        ("(at 1.0)", "Position identifier must have 2 or 3 components"),
        ("(at 1.0 2.0 3.0 4.0)", "Position identifier must have 2 or 3 components"),
        ("(at x y)", "Invalid numeric values in position identifier"),
        ("at 1.0 2.0", "Invalid position identifier format"),
    ],
)
def test_error_cases(sexpr, expected_error):
    """Test that invalid inputs raise appropriate errors."""
    with pytest.raises(ValueError, match=expected_error):
        PositionIdentifier.from_sexpr(sexpr)
