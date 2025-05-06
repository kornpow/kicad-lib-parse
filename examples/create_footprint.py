#!/usr/bin/env python3
"""
Example script demonstrating how to create a new KiCad footprint.
This example creates a 0603 resistor footprint with:
- Basic footprint information
- Properties (Reference, Value, etc.)
- Courtyard outline
- Silkscreen markings
- Pads
"""

from src.models import (
    Font,
    FootprintModel,
    Layer,
    Line,
    Pad,
    Point,
    Points,
    Polygon,
    PositionIdentifier,
    Property,
    Stroke,
    StrokeType,
    TextEffects,
)


def create_0603_footprint():
    """Create a 0603 resistor footprint."""
    # Create the basic footprint
    footprint = FootprintModel(
        name="0603",
        version="20240108",
        generator="pcbnew",
        generator_version="8.0",
        layer=Layer.F_CU,
        description="Generic 1608 (0603) package",
        properties=[
            Property(
                key="Reference",
                value="REF**",
                effects=TextEffects(
                    font=Font(
                        face="KiCad",
                        height=1.0,
                        width=0.2,
                        thickness=0.15,
                        bold=True,
                    ),
                    justify_horizontal="left",
                    justify_vertical="bottom",
                ),
            ),
            Property(
                key="Value",
                value="0603",
                effects=TextEffects(
                    font=Font(
                        face="KiCad",
                        height=1.0,
                        width=0.2,
                        thickness=0.15,
                    ),
                    justify_horizontal="left",
                    justify_vertical="top",
                ),
            ),
        ],
    )

    # Add courtyard outline (polygon)
    courtyard = Polygon(
        points=Points(
            points=[
                Point(x=-0.8, y=0.4),
                Point(x=0.8, y=0.4),
                Point(x=0.8, y=-0.4),
                Point(x=-0.8, y=-0.4),
            ]
        ),
        stroke=Stroke(width=0.05, type=StrokeType.DEFAULT),
        fill="outline",
        layer=Layer.F_CRTYD,
    )
    footprint.polygons.append(courtyard)

    # Add silkscreen markings (lines)
    silkscreen_lines = [
        # Top line
        Line(
            start=Point(x=-0.3, y=0.2),
            end=Point(x=0.3, y=0.2),
            stroke=Stroke(width=0.1, type=StrokeType.DEFAULT),
            layer=Layer.F_SILKS,
        ),
        # Bottom line
        Line(
            start=Point(x=-0.3, y=-0.2),
            end=Point(x=0.3, y=-0.2),
            stroke=Stroke(width=0.1, type=StrokeType.DEFAULT),
            layer=Layer.F_SILKS,
        ),
    ]
    footprint.lines.extend(silkscreen_lines)

    # Add pads
    pads = [
        # Pad 1
        Pad(
            number="1",
            type="smd",
            shape="roundrect",
            at=PositionIdentifier(x=-0.75, y=0),
            size=(0.6, 0.6),
            layers=[Layer.F_CU, Layer.F_PASTE, Layer.F_MASK],
            roundrect_rratio=0.25,
        ),
        # Pad 2
        Pad(
            number="2",
            type="smd",
            shape="roundrect",
            at=PositionIdentifier(x=0.75, y=0),
            size=(0.6, 0.6),
            layers=[Layer.F_CU, Layer.F_PASTE, Layer.F_MASK],
            roundrect_rratio=0.25,
        ),
    ]
    footprint.pads.extend(pads)

    return footprint


def main():
    """Main function to create and save the footprint."""
    # Create the footprint
    footprint = create_0603_footprint()

    # Convert to s-expression format
    sexp = footprint.to_sexp()

    # Print the s-expression
    print("Generated footprint s-expression:")
    print(sexp)

    # Save to file
    output_file = "0603_example.kicad_mod"
    with open(output_file, "w") as f:
        f.write(str(sexp))
    print(f"\nSaved footprint to {output_file}")


if __name__ == "__main__":
    main()
