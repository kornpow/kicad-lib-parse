"""KiCad library parser package."""

from .io import write_footprint_to_file
from .models import (  # Enums; Base Models; Complex Models
    UUID,
    Font,
    Footprint,
    FootprintModel,
    Image,
    Layer,
    Line,
    Pad,
    PadShape,
    PageSettings,
    PaperSize,
    Point,
    Points,
    Polygon,
    PositionIdentifier,
    Property,
    Stroke,
    StrokeType,
    SymbolValueModel,
    TextEffects,
)

__all__ = [
    # Functions
    "write_footprint_to_file",
    # Enums
    "Layer",
    "PadShape",
    "PaperSize",
    "StrokeType",
    # Base Models
    "Font",
    "Point",
    "PositionIdentifier",
    "Stroke",
    "TextEffects",
    "UUID",
    # Complex Models
    "Footprint",
    "FootprintModel",
    "Image",
    "Line",
    "Pad",
    "PageSettings",
    "Points",
    "Polygon",
    "Property",
    "SymbolValueModel",
]
