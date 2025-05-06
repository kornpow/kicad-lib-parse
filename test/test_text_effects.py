import pytest
from pydantic import ValidationError
from sexpdata import Symbol

from src.models import Font, TextEffects


# Test data fixtures
@pytest.fixture
def basic_font_test_cases():
    return [
        (["effects", ["font", ["size", "1.0", "1.0"]]], TextEffects(font=Font())),
        (
            ["effects", ["font", ["face", '"KiCad Font"'], ["size", "1.0", "1.0"]]],
            TextEffects(font=Font(face="KiCad Font")),
        ),
        (
            [
                "effects",
                [
                    "font",
                    ["size", "2.0", "1.5"],
                    ["thickness", "0.2"],
                    "bold",
                    "italic",
                ],
            ],
            TextEffects(font=Font(height=2.0, width=1.5, thickness=0.2, bold=True, italic=True)),
        ),
    ]


@pytest.fixture
def justify_test_cases():
    return [
        (
            ["effects", ["font", ["size", "1.0", "1.0"]], ["justify", "left"]],
            TextEffects(font=Font(), justify_horizontal="left"),
        ),
        (
            ["effects", ["font", ["size", "1.0", "1.0"]], ["justify", "right", "top"]],
            TextEffects(font=Font(), justify_horizontal="right", justify_vertical="top"),
        ),
        (
            [
                "effects",
                ["font", ["size", "1.0", "1.0"]],
                ["justify", "left", "bottom", "mirror"],
            ],
            TextEffects(
                font=Font(),
                justify_horizontal="left",
                justify_vertical="bottom",
                mirror=True,
            ),
        ),
    ]


@pytest.fixture
def hide_test_cases():
    return [
        (
            ["effects", ["font", ["size", "1.0", "1.0"]], "hide"],
            TextEffects(font=Font(), hide=True),
        ),
        (
            ["effects", ["font", ["size", "1.0", "1.0"]], ["justify", "left"], "hide"],
            TextEffects(font=Font(), justify_horizontal="left", hide=True),
        ),
    ]


# Convert lists to Symbol format
def symbolize(data):
    """Convert string tokens to Symbols in test data."""
    if isinstance(data, list):
        return [symbolize(item) for item in data]
    elif isinstance(data, str) and not data.startswith('"'):
        return Symbol(data)
    return data


# Test functions
def test_basic_font_parsing(basic_font_test_cases):
    """Test basic font settings parsing."""
    for sexp, expected in basic_font_test_cases:
        result = TextEffects.from_sexp(symbolize(sexp))
        assert result == expected


def test_justify_parsing(justify_test_cases):
    """Test justification settings parsing."""
    for sexp, expected in justify_test_cases:
        result = TextEffects.from_sexp(symbolize(sexp))
        assert result == expected


def test_hide_parsing(hide_test_cases):
    """Test hide setting parsing."""
    for sexp, expected in hide_test_cases:
        result = TextEffects.from_sexp(symbolize(sexp))
        assert result == expected


def test_round_trip_conversion():
    """Test that converting to sexp and back produces the same result."""
    test_cases = [
        TextEffects(font=Font()),
        TextEffects(font=Font(face="KiCad Font", height=2.0, width=1.5, thickness=0.2, bold=True)),
        TextEffects(font=Font(), justify_horizontal="left", justify_vertical="top", mirror=True),
        TextEffects(font=Font(), hide=True),
    ]

    for original in test_cases:
        sexp = original.to_sexp()
        result = TextEffects.from_sexp(symbolize(sexp))
        assert result == original


def test_font_validation():
    """Test Pydantic validation for Font model."""
    # Test valid values
    Font(height=1.0, width=1.0)
    Font(thickness=0.1)
    Font(line_spacing=1.5)

    # Test invalid values
    with pytest.raises(ValidationError):
        Font(height=-1.0)
    with pytest.raises(ValidationError):
        Font(width=-1.0)
    with pytest.raises(ValidationError):
        Font(thickness=-0.1)
    with pytest.raises(ValidationError):
        Font(line_spacing=-1.5)


def test_text_effects_validation():
    """Test Pydantic validation for TextEffects model."""
    # Test valid values
    TextEffects(font=Font())
    TextEffects(font=Font(), justify_horizontal="left")
    TextEffects(font=Font(), justify_vertical="top")

    # Test invalid values
    with pytest.raises(ValidationError):
        TextEffects(font=Font(), justify_horizontal="invalid")
    with pytest.raises(ValidationError):
        TextEffects(font=Font(), justify_vertical="invalid")


@pytest.mark.parametrize(
    "sexp,expected_error",
    [
        (["effects"], "Missing font settings"),
        (["effects", ["font"]], "Missing font settings"),
        (["effects", ["font", ["size", "1.0"]]], "Missing font settings"),
        (["effects", ["font", ["size", "1.0", "1.0"], ["justify", "invalid"]]], None),
    ],
)
def test_error_cases(sexp, expected_error):
    """Test that invalid inputs raise appropriate errors."""
    if expected_error:
        with pytest.raises(ValueError, match=expected_error):
            TextEffects.from_sexp(symbolize(sexp))
    else:
        # For cases where we expect parsing to succeed but with default values
        result = TextEffects.from_sexp(symbolize(sexp))
        assert isinstance(result, TextEffects)
