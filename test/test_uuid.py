import pytest
from src.models import UUID
import uuid


# Test data fixtures
@pytest.fixture
def valid_uuid_test_cases():
    return [
        (
            "(uuid 00000000-0000-0000-0000-000000000000)",
            UUID(value="00000000-0000-0000-0000-000000000000"),
        ),
        (
            "(uuid 123e4567-e89b-12d3-a456-426614174000)",
            UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        ),
        (
            "(uuid 550e8400-e29b-41d4-a716-446655440000)",
            UUID(value="550e8400-e29b-41d4-a716-446655440000"),
        ),
    ]


@pytest.fixture
def whitespace_test_cases():
    return [
        (
            "(uuid  123e4567-e89b-12d3-a456-426614174000  )",
            UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        ),
        (
            "(uuid\t123e4567-e89b-12d3-a456-426614174000\t)",
            UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        ),
    ]


@pytest.fixture
def error_test_cases():
    return [
        ("(uuid)", "UUID must have exactly one component"),
        (
            "(uuid 123e4567-e89b-12d3-a456-426614174000 extra)",
            "UUID must have exactly one component",
        ),
        ("(uuid invalid-uuid)", "Invalid UUID format"),
        ("uuid 123e4567-e89b-12d3-a456-426614174000", "Invalid UUID format"),
    ]


# Test functions
def test_valid_uuid_parsing(valid_uuid_test_cases):
    """Test parsing of valid UUIDs."""
    for sexpr, expected in valid_uuid_test_cases:
        result = UUID.from_sexpr(sexpr)
        assert result == expected


def test_whitespace_variations(whitespace_test_cases):
    """Test parsing with different whitespace patterns."""
    for sexpr, expected in whitespace_test_cases:
        result = UUID.from_sexpr(sexpr)
        assert result == expected


def test_round_trip_conversion():
    """Test that converting to sexpr and back produces the same result."""
    test_cases = [
        UUID(value="00000000-0000-0000-0000-000000000000"),
        UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        UUID(value="550e8400-e29b-41d4-a716-446655440000"),
    ]

    for original in test_cases:
        sexpr = original.to_sexpr()
        result = UUID.from_sexpr(sexpr)
        assert result == original


@pytest.mark.parametrize(
    "sexpr,expected_error",
    [
        ("(uuid)", "UUID must have exactly one component"),
        (
            "(uuid 123e4567-e89b-12d3-a456-426614174000 extra)",
            "UUID must have exactly one component",
        ),
        ("(uuid invalid-uuid)", "Invalid UUID format"),
        ("uuid 123e4567-e89b-12d3-a456-426614174000", "Invalid UUID format"),
    ],
)
def test_error_cases(sexpr, expected_error):
    """Test that invalid inputs raise appropriate errors."""
    with pytest.raises(ValueError, match=expected_error):
        UUID.from_sexpr(sexpr)
