import pytest
from src.models import PageSettings, PaperSize


# Test data fixtures
@pytest.fixture
def standard_size_test_cases():
    return [
        ("(paper A4)", PageSettings(size=PaperSize.A4)),
        ("(paper A4 portrait)", PageSettings(size=PaperSize.A4, portrait=True)),
        ("(paper A0)", PageSettings(size=PaperSize.A0)),
        ("(paper A0 portrait)", PageSettings(size=PaperSize.A0, portrait=True)),
    ]


@pytest.fixture
def custom_size_test_cases():
    return [
        ("(paper 297 210)", PageSettings(size=(297.0, 210.0))),
        ("(paper 297 210 portrait)", PageSettings(size=(297.0, 210.0), portrait=True)),
        ("(paper 841 1189)", PageSettings(size=(841.0, 1189.0))),
        (
            "(paper 841 1189 portrait)",
            PageSettings(size=(841.0, 1189.0), portrait=True),
        ),
    ]


@pytest.fixture
def whitespace_test_cases():
    return [
        ("(paper  A4  )", PageSettings(size=PaperSize.A4)),
        ("(paper  A4  portrait  )", PageSettings(size=PaperSize.A4, portrait=True)),
        ("(paper  297  210  )", PageSettings(size=(297.0, 210.0))),
        (
            "(paper  297  210  portrait  )",
            PageSettings(size=(297.0, 210.0), portrait=True),
        ),
    ]


@pytest.fixture
def error_test_cases():
    return [
        ("(paper)", "Page settings must have at least one component"),
        ("(paper invalid)", "Invalid paper size"),
        ("(paper 297)", "Invalid paper size"),
        ("(paper 297 210 300)", "Invalid paper size"),
        ("(paper -297 210)", "Invalid numeric values in page settings"),
        ("(paper 297 -210)", "Invalid numeric values in page settings"),
        ("paper A4", "Invalid page settings format"),
    ]


# Test functions
def test_standard_size_parsing(standard_size_test_cases):
    """Test parsing of standard paper sizes."""
    for sexpr, expected in standard_size_test_cases:
        result = PageSettings.from_sexpr(sexpr)
        assert result == expected


def test_custom_size_parsing(custom_size_test_cases):
    """Test parsing of custom paper sizes."""
    for sexpr, expected in custom_size_test_cases:
        result = PageSettings.from_sexpr(sexpr)
        assert result == expected


def test_whitespace_variations(whitespace_test_cases):
    """Test parsing with different whitespace patterns."""
    for sexpr, expected in whitespace_test_cases:
        result = PageSettings.from_sexpr(sexpr)
        assert result == expected


def test_round_trip_conversion():
    """Test that converting to sexpr and back produces the same result."""
    test_cases = [
        PageSettings(size=PaperSize.A4),
        PageSettings(size=PaperSize.A4, portrait=True),
        PageSettings(size=(297.0, 210.0)),
        PageSettings(size=(297.0, 210.0), portrait=True),
    ]

    for original in test_cases:
        sexpr = original.to_sexpr()
        result = PageSettings.from_sexpr(sexpr)
        assert result == original


@pytest.mark.parametrize(
    "sexpr,expected_error",
    [
        ("(paper)", "Page settings must have at least one component"),
        ("(paper invalid)", "Invalid paper size"),
        ("(paper 297)", "Invalid paper size"),
        ("(paper 297 210 300)", "Invalid numeric values in page settings"),
        ("(paper -297 210)", "Invalid numeric values in page settings"),
        ("(paper 297 -210)", "Invalid numeric values in page settings"),
        ("paper A4", "Invalid page settings format"),
    ],
)
def test_error_cases(sexpr, expected_error):
    """Test that invalid inputs raise appropriate errors."""
    with pytest.raises(ValueError, match=expected_error):
        PageSettings.from_sexpr(sexpr)
