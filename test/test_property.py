import pytest
from sexpdata import Symbol

from src.models import Property


def test_property_from_sexp():
    """Test parsing property from s-expression."""
    # Test basic property
    sexp = [Symbol("property"), "Reference", "R1"]
    prop = Property.from_sexp(sexp)
    assert prop.key == "Reference"
    assert prop.value == "R1"


def test_property_to_sexp():
    """Test converting property to s-expression."""
    # Test basic property
    prop = Property(key="Reference", value="R1")
    sexp = prop.to_sexp()
    assert sexp == [Symbol("property"), "Reference", "R1"]


def test_property_invalid_sexp():
    """Test handling of invalid s-expressions."""
    # Test missing required components
    with pytest.raises(ValueError, match="Invalid property data format"):
        Property.from_sexp([Symbol("property"), "Reference"])

    # Test invalid format
    with pytest.raises(ValueError, match="Property data must start with 'property' symbol"):
        Property.from_sexp([Symbol("not_a_property"), "Reference", "R1"])

    # Test invalid optional field format
    with pytest.raises(ValueError, match="Invalid optional field format"):
        Property.from_sexp([Symbol("property"), "Reference", "R1", "InvalidLayer"])

    # Test invalid at field format
    with pytest.raises(ValueError):
        Property.from_sexp(
            [
                Symbol("property"),
                "Reference",
                "R1",
                [Symbol("at"), "invalid", "position"],
            ]
        )
