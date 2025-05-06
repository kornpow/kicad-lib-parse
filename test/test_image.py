import pytest

from src.models import UUID, Image, Layer, PositionIdentifier


def test_image_from_sexpr():
    """Test parsing image from s-expression."""
    # Test basic image with required fields
    sexpr = '(image (at 10 20 0) (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
    image = Image.from_sexpr(sexpr)
    assert image.at.x == 10
    assert image.at.y == 20
    assert image.at.angle == 0
    assert image.scale is None
    assert image.layer is None
    assert image.uuid.value == "123e4567-e89b-12d3-a456-426614174000"
    assert image.data == "base64data"

    # Test image with all optional fields
    sexpr = '(image (at 10 20 0) (scale 2.5) (layer "F.SilkS") (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
    image = Image.from_sexpr(sexpr)
    assert image.scale == 2.5
    assert image.layer == Layer.F_SILKS

    # Test image without angle
    sexpr = '(image (at 10 20) (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
    image = Image.from_sexpr(sexpr)
    assert image.at.angle is None


def test_image_to_sexpr():
    """Test converting image to s-expression."""
    # Test basic image with required fields
    image = Image(
        at=PositionIdentifier(x=10, y=20, angle=0),
        uuid=UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        data="base64data",
    )
    sexpr = image.to_sexpr()
    assert (
        sexpr
        == '(image (at 10.0 20.0 0.0) (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
    )

    # Test image with all optional fields
    image = Image(
        at=PositionIdentifier(x=10, y=20, angle=0),
        scale=2.5,
        layer=Layer.F_SILKS,
        uuid=UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        data="base64data",
    )
    sexpr = image.to_sexpr()
    assert (
        sexpr
        == '(image (at 10.0 20.0 0.0) (scale 2.5) (layer "F.SilkS") (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
    )

    # Test image without angle
    image = Image(
        at=PositionIdentifier(x=10, y=20),
        uuid=UUID(value="123e4567-e89b-12d3-a456-426614174000"),
        data="base64data",
    )
    sexpr = image.to_sexpr()
    assert (
        sexpr
        == '(image (at 10.0 20.0) (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
    )


def test_image_validation():
    """Test image validation."""
    # Test invalid scale (negative)
    with pytest.raises(ValueError, match="Scale must be positive"):
        Image(
            at=PositionIdentifier(x=10, y=20),
            scale=-2.5,
            uuid=UUID(value="123e4567-e89b-12d3-a456-426614174000"),
            data="base64data",
        )

    # Test invalid scale (zero)
    with pytest.raises(ValueError, match="Scale must be positive"):
        Image(
            at=PositionIdentifier(x=10, y=20),
            scale=0,
            uuid=UUID(value="123e4567-e89b-12d3-a456-426614174000"),
            data="base64data",
        )


def test_image_invalid_sexpr():
    """Test handling of invalid s-expressions."""
    # Test missing required components
    with pytest.raises(ValueError, match="Missing required image components"):
        Image.from_sexpr("(image (at 10 20))")

    # Test invalid format
    with pytest.raises(ValueError, match="Invalid image format"):
        Image.from_sexpr(
            '(not_an_image (at 10 20) (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
        )

    # Test invalid scale format
    with pytest.raises(ValueError, match="could not convert string to float"):
        Image.from_sexpr(
            '(image (at 10 20) (scale abc) (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
        )

    # Test invalid layer
    with pytest.raises(ValueError, match="is not a valid Layer"):
        Image.from_sexpr(
            '(image (at 10 20) (layer "InvalidLayer") (uuid "123e4567-e89b-12d3-a456-426614174000") (data "base64data"))'
        )
