from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Tuple, Any, Literal
from enum import Enum
from sexpdata import Symbol
import re
import uuid


class Layer(str, Enum):
    F_CU = "F.Cu"
    F_PASTE = "F.Paste"
    F_MASK = "F.Mask"
    F_SILKS = "F.SilkS"
    F_FAB = "F.Fab"
    F_CRTYD = "F.CrtYd"
    F_ADHES = "F.Adhes"

    @classmethod
    def from_sexp(cls, data: str) -> "Layer":
        """Parse sexpdata format into Layer model.

        Args:
            data: String representing the layer name

        Returns:
            Layer enum value

        Raises:
            ValueError: If the layer name is invalid
        """
        try:
            return cls(data)
        except ValueError:
            raise ValueError(f"Invalid layer name: {data}")

    @classmethod
    def from_sexp_list(cls, data: List[Any]) -> "Layer":
        """Parse sexpdata list format into Layer model.

        Args:
            data: List in format [Symbol('layer'), value]

        Returns:
            Layer enum value

        Raises:
            ValueError: If the data format is invalid or layer name is invalid
        """
        if not isinstance(data, list) or len(data) != 2:
            raise ValueError("Invalid layer data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "layer":
            raise ValueError("Layer data must start with 'layer' symbol")

        try:
            return cls(str(data[1]))
        except ValueError:
            raise ValueError(f"Invalid layer name: {data[1]}")

    def to_sexp(self) -> str:
        """Convert Layer enum to sexpdata format.

        Returns:
            String representation of the layer name
        """
        return [Symbol("layer"), self.value]


class StrokeType(str, Enum):
    DEFAULT = "default"
    SOLID = "solid"
    DASH = "dash"
    DOT = "dot"
    DASH_DOT = "dash_dot"
    DASH_DOT_DOT = "dash_dot_dot"  # from version 7


class Font(BaseModel):
    """Represents font settings for text effects."""

    face: Optional[str] = None
    height: float = Field(default=1.0, ge=0)
    width: float = Field(default=1.0, ge=0)
    thickness: Optional[float] = Field(default=None, ge=0)
    bold: bool = False
    italic: bool = False
    line_spacing: Optional[float] = Field(default=None, ge=0)

    @field_validator("thickness", "line_spacing")
    @classmethod
    def validate_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError("Value must be positive")
        return v


class TextEffects(BaseModel):
    """Represents KiCad text effects with font and justification settings."""

    font: Font
    justify_horizontal: Optional[Literal["left", "right"]] = None
    justify_vertical: Optional[Literal["top", "bottom"]] = None
    mirror: bool = False
    hide: bool = False

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "TextEffects":
        """Parse sexpdata format into TextEffects model."""
        if not isinstance(data, list) or len(data) < 2:
            raise ValueError("Missing font settings")

        if not isinstance(data[0], Symbol) or data[0].value() != "effects":
            raise ValueError("Missing font settings")

        font_data = None
        justify_h = None
        justify_v = None
        mirror = False
        hide = False

        for item in data[1:]:
            if isinstance(item, list):
                if len(item) < 1:
                    continue
                if str(item[0]) == "font":
                    if len(item) < 2:
                        raise ValueError("Missing font settings")
                    font_data = item
                elif str(item[0]) == "justify":
                    for j in item[1:]:
                        j_str = str(j)
                        if j_str in ["left", "right"]:
                            justify_h = j_str
                        elif j_str in ["top", "bottom"]:
                            justify_v = j_str
                        elif j_str == "mirror":
                            mirror = True
            elif str(item) == "hide":
                hide = True

        if font_data is None:
            raise ValueError("Missing font settings")

        font = cls._parse_font(font_data)
        return cls(
            font=font,
            justify_horizontal=justify_h,
            justify_vertical=justify_v,
            mirror=mirror,
            hide=hide,
        )

    @staticmethod
    def _parse_font(data: List[Any]) -> Font:
        """Parse font settings from sexpdata format."""
        font_data = {
            "face": None,
            "height": 1.0,
            "width": 1.0,
            "thickness": None,
            "bold": False,
            "italic": False,
            "line_spacing": None,
        }

        for item in data[1:]:
            if isinstance(item, list):
                if len(item) < 2:
                    continue
                item_type = str(item[0])
                if item_type == "face":
                    font_data["face"] = str(item[1]).strip('"')
                elif item_type == "size":
                    if len(item) < 3:
                        raise ValueError("Missing font settings")
                    font_data["height"] = float(item[1])
                    font_data["width"] = float(item[2])
                elif item_type == "thickness":
                    if len(item) < 2:
                        raise ValueError("Missing font settings")
                    font_data["thickness"] = float(item[1])
                elif item_type == "line_spacing":
                    if len(item) < 2:
                        raise ValueError("Missing font settings")
                    font_data["line_spacing"] = float(item[1])
            elif str(item) == "bold":
                font_data["bold"] = True
            elif str(item) == "italic":
                font_data["italic"] = True

        return Font(**font_data)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [Symbol("effects")]

        # Font settings
        font_parts = [Symbol("font")]
        if self.font.face:
            font_parts.append([Symbol("face"), f'"{self.font.face}"'])
        font_parts.append([Symbol("size"), self.font.height, self.font.width])
        if self.font.thickness:
            font_parts.append([Symbol("thickness"), self.font.thickness])
        if self.font.bold:
            font_parts.append(Symbol("bold"))
        if self.font.italic:
            font_parts.append(Symbol("italic"))
        if self.font.line_spacing:
            font_parts.append(["line_spacing", str(self.font.line_spacing)])
        result.append(font_parts)

        # Justification and other settings
        if self.justify_horizontal or self.justify_vertical or self.mirror:
            justify_parts = [Symbol("justify")]
            if self.justify_horizontal:
                justify_parts.append(Symbol(self.justify_horizontal))
            if self.justify_vertical:
                justify_parts.append(Symbol(self.justify_vertical))
            if self.mirror:
                justify_parts.append(Symbol("mirror"))
            result.append(justify_parts)

        if self.hide:
            result.append(Symbol("hide"))

        return result


class PositionIdentifier(BaseModel):
    """Represents a KiCad position identifier with X, Y coordinates and optional angle."""

    x: float
    y: float
    angle: Optional[float] = None

    @classmethod
    def from_sexpr(cls, sexpr: str) -> "PositionIdentifier":
        """
        Parse a position identifier from an s-expression string.

        Args:
            sexpr: String in format "(at X Y [ANGLE])"

        Returns:
            PositionIdentifier object

        Raises:
            ValueError: If the s-expression is malformed
        """
        # Remove whitespace and newlines
        sexpr = re.sub(r"\s+", " ", sexpr.strip())

        # Basic format validation
        if not sexpr.startswith("(at") or not sexpr.endswith(")"):
            raise ValueError("Invalid position identifier format")

        # Extract the content between parentheses
        content = sexpr[3:-1].strip()

        # Split into components
        parts = content.split()

        if len(parts) < 2 or len(parts) > 3:
            raise ValueError("Position identifier must have 2 or 3 components")

        try:
            x = float(parts[0])
            y = float(parts[1])
            angle = float(parts[2]) if len(parts) == 3 else None
            return cls(x=x, y=y, angle=angle)
        except ValueError:
            raise ValueError("Invalid numeric values in position identifier")

    def to_sexpr(self) -> str:
        """Convert the position identifier to s-expression format."""
        if self.angle is not None:
            return f"(at {self.x} {self.y} {self.angle})"
        return f"(at {self.x} {self.y})"


class Property(BaseModel):
    key: str
    value: str
    at: Optional[PositionIdentifier] = None
    unlocked: bool = False
    layer: Optional[Layer] = None
    uuid: Optional[str] = None
    effects: Optional[TextEffects] = None
    hide: bool = False

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "Property":
        """Parse sexpdata format into Property model.

        Args:
            data: List in format [Symbol('property'), key, value, at?, unlocked?, layer?, uuid?, effects?, hide?]
        """
        if not isinstance(data, list) or len(data) < 3:
            raise ValueError("Invalid property data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "property":
            raise ValueError("Property data must start with 'property' symbol")

        key = str(data[1])
        value = str(data[2])
        at = None
        unlocked = False
        layer = None
        uuid = None
        effects = None
        hide = False

        # Parse optional fields
        for item in data[3:]:
            if isinstance(item, list):
                item_type = str(item[0])
                if item_type == "at":
                    at = PositionIdentifier(
                        x=float(item[1]),
                        y=float(item[2]),
                        angle=float(item[3]) if len(item) > 3 else None,
                    )
                elif item_type == "layer":
                    if len(item) != 2:
                        raise ValueError("Invalid layer format")
                    try:
                        layer = Layer(str(item[1]))
                    except ValueError:
                        raise ValueError("Invalid layer format")
                elif item_type == "effects":
                    effects = TextEffects.from_sexp(item)
                elif item_type == "uuid":
                    uuid = str(item[1])
                elif item_type == "unlocked":
                    unlocked = str(item[1]) == "yes"
            elif str(item) == "hide":
                hide = True
            else:
                raise ValueError("Invalid optional field format")

        return cls(
            key=key,
            value=value,
            at=at,
            unlocked=unlocked,
            layer=layer,
            uuid=uuid,
            effects=effects,
            hide=hide,
        )

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [Symbol("property"), self.key, self.value]

        if self.at:
            result.append(
                [Symbol("at"), self.at.x, self.at.y]
                + ([self.at.angle] if self.at.angle is not None else [])
            )

        if self.unlocked:
            result.append([Symbol("unlocked"), Symbol("yes")])

        if self.layer:
            result.append([Symbol("layer"), self.layer.value])

        if self.effects:
            result.append(self.effects.to_sexp())

        if self.uuid:
            result.append([Symbol("uuid"), self.uuid])

        if self.hide:
            result.append(Symbol("hide"))

        return result


class Stroke(BaseModel):
    """Model for stroke definitions in KiCad format."""

    width: float
    type: StrokeType = StrokeType.SOLID
    color: Optional[Tuple[int, int, int, int]] = None  # RGBA color values

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "Stroke":
        """Parse sexpdata format into Stroke model.

        Args:
            data: List in format [Symbol('stroke'), [Symbol('width'), value], [Symbol('type'), value], [Symbol('color'), r, g, b, a]]
        """
        print(data)
        if not isinstance(data, list) or len(data) < 3:
            raise ValueError("Invalid stroke data format")

        # if not isinstance(data[0], Symbol) or
        if str(data[0]) != "stroke":
            raise ValueError("Stroke data must start with 'stroke' symbol")

        width_data = data[1]
        type_data = data[2]

        if not isinstance(width_data, list) or len(width_data) != 2:
            raise ValueError(f"Invalid width format: {width_data}")
        if not isinstance(type_data, list) or len(type_data) != 2:
            raise ValueError(f"Invalid type format: {type_data}")

        # if not isinstance(width_data[0], Symbol) or
        if str(width_data[0]) != "width":
            raise ValueError(f"Width must start with 'width' symbol: {width_data}")
        # if not isinstance(type_data[0], Symbol) or
        if str(type_data[0]) != "type":
            raise ValueError(f"Type must start with 'type' symbol: {type_data}")

        try:
            width = float(width_data[1])
            type_ = str(type_data[1])
            if type_ not in [t.value for t in StrokeType]:
                raise ValueError(f"Invalid stroke type: {type_}")
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid stroke values: {data}") from e

        color = None
        if len(data) > 3:
            color_data = data[3]
            if not isinstance(color_data, list) or len(color_data) != 5:
                raise ValueError(f"Invalid color format: {color_data}")
            # if not isinstance(color_data[0], Symbol) or
            if str(color_data[0]) != "color":
                raise ValueError(f"Color must start with 'color' symbol: {color_data}")
            try:
                color = (
                    int(color_data[1]),
                    int(color_data[2]),
                    int(color_data[3]),
                    int(color_data[4]),
                )
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid color values: {color_data}") from e

        return cls(width=width, type=type_, color=color)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [
            Symbol("stroke"),
            [Symbol("width"), self.width],
            [Symbol("type"), Symbol(self.type.value)],
        ]
        if self.color:
            result.append([Symbol("color"), *[str(c) for c in self.color]])
        return result


class Point(BaseModel):
    x: float
    y: float


class Points(BaseModel):
    """Model for a list of X/Y coordinate points in KiCad format."""

    points: List[Point] = Field(description="List of X/Y coordinate points")

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "Points":
        """Parse sexpdata format into Points model.

        Args:
            data: List in format [Symbol('pts'), [Symbol('xy'), x1, y1], [Symbol('xy'), x2, y2], ...]
        """
        if not isinstance(data, list) or len(data) < 2:
            raise ValueError("Invalid points data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "pts":
            raise ValueError("Points data must start with 'pts' symbol")

        points = []
        for item in data[1:]:
            if not isinstance(item, list) or len(item) != 3:
                raise ValueError(f"Invalid point format: {item}")

            if not isinstance(item[0], Symbol) or item[0].value() != "xy":
                raise ValueError(f"Point must start with 'xy' symbol: {item}")

            try:
                x = float(item[1])
                y = float(item[2])
                points.append(Point(x=x, y=y))
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid point coordinates: {item}") from e

        return cls(points=points)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        return [Symbol("pts")] + [[Symbol("xy"), pt.x, pt.y] for pt in self.points]


class Polygon(BaseModel):
    """Model for polygon in KiCad format."""

    points: Points
    stroke: Optional[Stroke] = None
    fill: str = "solid"  # solid, outline, none
    layer: Layer
    uuid: Optional[str] = None

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "Polygon":
        """Parse sexpdata format into Polygon model.

        Args:
            data: List in format [Symbol('fp_poly'), Points, [Stroke], [fill], [layer], [uuid]]
        """
        if not isinstance(data, list) or len(data) < 4:
            raise ValueError("Invalid polygon data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "fp_poly":
            raise ValueError("Polygon data must start with 'fp_poly' symbol")

        # Parse points
        points = Points.from_sexp(data[1])

        # Parse stroke if present
        stroke = None
        current_index = 2
        if (
            isinstance(data[current_index], list)
            and isinstance(data[current_index][0], Symbol)
            and data[current_index][0].value() == "stroke"
        ):
            stroke = Stroke.from_sexp(data[current_index])
            current_index += 1

        # Parse fill
        fill_data = data[current_index]
        if (
            isinstance(fill_data, list)
            and len(fill_data) == 2
            and isinstance(fill_data[0], Symbol)
            and fill_data[0].value() == "fill"
        ):
            fill = str(fill_data[1])
        else:
            fill = str(fill_data)
        if fill not in ["solid", "outline", "none"]:
            raise ValueError("Invalid fill type")
        current_index += 1

        # Parse layer
        layer_data = data[current_index]
        if (
            isinstance(layer_data, list)
            and len(layer_data) == 2
            and isinstance(layer_data[0], Symbol)
            and layer_data[0].value() == "layer"
        ):
            layer = Layer(str(layer_data[1]))
        else:
            layer = Layer(str(layer_data))
        current_index += 1

        # Parse uuid if present
        uuid = None
        if (
            current_index < len(data)
            and isinstance(data[current_index], list)
            and isinstance(data[current_index][0], Symbol)
            and data[current_index][0].value() == "uuid"
        ):
            uuid = str(data[current_index][1])

        return cls(points=points, stroke=stroke, fill=fill, layer=layer, uuid=uuid)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [Symbol("fp_poly"), self.points.to_sexp()]

        if self.stroke:
            result.append(self.stroke.to_sexp())

        result.append([Symbol("fill"), Symbol(self.fill)])
        result.append([Symbol("layer"), self.layer.value])

        if self.uuid:
            result.append([Symbol("uuid"), self.uuid])

        return result


class Line(BaseModel):
    """Model for line in KiCad format."""

    start: Point
    end: Point
    stroke: Stroke
    layer: Layer
    uuid: Optional[str] = None

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "Line":
        """Parse sexpdata format into Line model.

        Args:
            data: List in format [Symbol('fp_line'), [Symbol('start'), x, y], [Symbol('end'), x, y], [stroke], [layer], [uuid]]
        """
        if not isinstance(data, list) or len(data) < 5:
            raise ValueError("Invalid line data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "fp_line":
            raise ValueError("Line data must start with 'fp_line' symbol")

        # Parse start point
        if (
            not isinstance(data[1], list)
            or len(data[1]) != 3
            or not isinstance(data[1][0], Symbol)
            or data[1][0].value() != "start"
        ):
            raise ValueError("Invalid start point format")
        start = Point(x=float(data[1][1]), y=float(data[1][2]))

        # Parse end point
        if (
            not isinstance(data[2], list)
            or len(data[2]) != 3
            or not isinstance(data[2][0], Symbol)
            or data[2][0].value() != "end"
        ):
            raise ValueError("Invalid end point format")
        end = Point(x=float(data[2][1]), y=float(data[2][2]))

        # Parse stroke
        if (
            not isinstance(data[3], list)
            or not isinstance(data[3][0], Symbol)
            or data[3][0].value() != "stroke"
        ):
            raise ValueError("Invalid stroke format")
        stroke = Stroke.from_sexp(data[3])

        # Parse layer
        layer_data = data[4]
        if (
            isinstance(layer_data, list)
            and len(layer_data) == 2
            and isinstance(layer_data[0], Symbol)
            and layer_data[0].value() == "layer"
        ):
            layer = Layer(str(layer_data[1]))
        else:
            layer = Layer(str(layer_data))

        # Parse uuid if present
        uuid = None
        if (
            len(data) > 5
            and isinstance(data[5], list)
            and isinstance(data[5][0], Symbol)
            and data[5][0].value() == "uuid"
        ):
            uuid = str(data[5][1])

        return cls(start=start, end=end, stroke=stroke, layer=layer, uuid=uuid)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [
            Symbol("fp_line"),
            [Symbol("start"), self.start.x, self.start.y],
            [Symbol("end"), self.end.x, self.end.y],
            self.stroke.to_sexp(),
            [Symbol("layer"), self.layer.value],
        ]

        if self.uuid:
            result.append([Symbol("uuid"), self.uuid])

        return result


class Pad(BaseModel):
    """Model for pad in KiCad format."""

    number: str
    type: str
    shape: str
    at: PositionIdentifier
    size: Tuple[float, float]
    layers: List[Layer]
    roundrect_rratio: Optional[float] = None
    solder_mask_margin: Optional[float] = None
    thermal_bridge_angle: Optional[float] = None
    uuid: Optional[str] = None

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "Pad":
        """Parse sexpdata format into Pad model.

        Args:
            data: List in format [Symbol('pad'), number, type, shape, at, size, layers, ...]
        """
        if not isinstance(data, list) or len(data) < 7:
            raise ValueError("Invalid pad data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "pad":
            raise ValueError("Pad data must start with 'pad' symbol")

        # Parse basic attributes
        number = str(data[1])
        type_ = str(data[2])
        shape = str(data[3])

        # Parse position
        if (
            not isinstance(data[4], list)
            or len(data[4]) < 3
            or not isinstance(data[4][0], Symbol)
            or data[4][0].value() != "at"
        ):
            raise ValueError("Invalid pad position format")
        at = PositionIdentifier(
            x=float(data[4][1]),
            y=float(data[4][2]),
            angle=float(data[4][3]) if len(data[4]) > 3 else None,
        )

        # Parse size
        if (
            not isinstance(data[5], list)
            or len(data[5]) != 3
            or not isinstance(data[5][0], Symbol)
            or data[5][0].value() != "size"
        ):
            raise ValueError("Invalid pad size format")
        size = (float(data[5][1]), float(data[5][2]))

        # Parse layers
        if (
            not isinstance(data[6], list)
            or len(data[6]) < 2
            or not isinstance(data[6][0], Symbol)
            or data[6][0].value() != "layers"
        ):
            raise ValueError("Invalid pad layers format")
        layers = [Layer(str(layer)) for layer in data[6][1:]]

        # Parse optional attributes
        roundrect_rratio = None
        solder_mask_margin = None
        thermal_bridge_angle = None
        uuid = None

        for item in data[7:]:
            if not isinstance(item, list) or len(item) < 2:
                continue

            item_type = str(item[0])
            if item_type == "roundrect_rratio":
                roundrect_rratio = float(item[1])
            elif item_type == "solder_mask_margin":
                solder_mask_margin = float(item[1])
            elif item_type == "thermal_bridge_angle":
                thermal_bridge_angle = float(item[1])
            elif item_type == "uuid":
                uuid = str(item[1])

        return cls(
            number=number,
            type=type_,
            shape=shape,
            at=at,
            size=size,
            layers=layers,
            roundrect_rratio=roundrect_rratio,
            solder_mask_margin=solder_mask_margin,
            thermal_bridge_angle=thermal_bridge_angle,
            uuid=uuid,
        )

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [
            Symbol("pad"),
            self.number,
            Symbol(self.type),
            Symbol(self.shape),
            [Symbol("at"), self.at.x, self.at.y]
            + ([self.at.angle] if self.at.angle is not None else []),
            [Symbol("size"), self.size[0], self.size[1]],
            [Symbol("layers")] + [layer.value for layer in self.layers],
        ]

        if self.roundrect_rratio is not None:
            result.append([Symbol("roundrect_rratio"), self.roundrect_rratio])

        if self.solder_mask_margin is not None:
            result.append([Symbol("solder_mask_margin"), self.solder_mask_margin])

        if self.thermal_bridge_angle is not None:
            result.append([Symbol("thermal_bridge_angle"), self.thermal_bridge_angle])

        if self.uuid:
            result.append([Symbol("uuid"), self.uuid])

        return result


class Footprint(BaseModel):
    name: str
    version: Union[str, int]  # Allow both string and integer versions
    generator: str
    generator_version: str
    layer: Layer
    description: str
    properties: List[Property]
    polygons: List[Polygon] = Field(default_factory=list)
    lines: List[Line] = Field(default_factory=list)
    pads: List[Pad] = Field(default_factory=list)


class PaperSize(str, Enum):
    """Valid paper sizes for KiCad documents."""

    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"
    A4 = "A4"
    A5 = "A5"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class PageSettings(BaseModel):
    """Represents KiCad page settings with size and orientation."""

    size: Union[
        PaperSize, Tuple[float, float]
    ]  # Either standard size or custom width/height
    portrait: bool = False  # False means landscape

    @field_validator("size")
    @classmethod
    def validate_size(cls, v):
        if isinstance(v, tuple):
            if len(v) != 2:
                raise ValueError("Custom size must be a tuple of (width, height)")
            width, height = v
            if width <= 0 or height <= 0:
                raise ValueError("Width and height must be positive")
        return v

    @classmethod
    def from_sexpr(cls, sexpr: str) -> "PageSettings":
        """
        Parse page settings from an s-expression string.

        Args:
            sexpr: String in format "(paper SIZE [portrait])" or "(paper WIDTH HEIGHT [portrait])"

        Returns:
            PageSettings object

        Raises:
            ValueError: If the s-expression is malformed
        """
        # Remove whitespace and newlines
        sexpr = re.sub(r"\s+", " ", sexpr.strip())

        # Basic format validation
        if not sexpr.startswith("(paper") or not sexpr.endswith(")"):
            raise ValueError("Invalid page settings format")

        # Extract the content between parentheses
        content = sexpr[6:-1].strip()

        # Split into components
        parts = content.split()

        if len(parts) < 1:
            raise ValueError("Page settings must have at least one component")

        # Check if it's a custom size (width height) or standard size
        try:
            if len(parts) >= 2 and all(
                part.replace(".", "").replace("-", "").isdigit() for part in parts[:2]
            ):
                # Validate number of components for custom size
                if len(parts) > 3 or (len(parts) == 3 and parts[2] != "portrait"):
                    raise ValueError("Invalid paper size")

                # Try to parse as custom size
                width = float(parts[0])
                height = float(parts[1])
                if width <= 0 or height <= 0:
                    raise ValueError("Invalid numeric values in page settings")
                size = (width, height)
                portrait = len(parts) == 3 and parts[2] == "portrait"
            else:
                # Validate number of components for standard size
                if len(parts) > 2 or (len(parts) == 2 and parts[1] != "portrait"):
                    raise ValueError("Invalid paper size")

                # Try to parse as standard size
                size = PaperSize(parts[0])
                portrait = len(parts) == 2 and parts[1] == "portrait"

            return cls(size=size, portrait=portrait)
        except ValueError as e:
            if "is not a valid PaperSize" in str(e):
                raise ValueError("Invalid paper size")
            raise ValueError("Invalid numeric values in page settings")

    def to_sexpr(self) -> str:
        """Convert the page settings to s-expression format."""
        if isinstance(self.size, tuple):
            width, height = self.size
            result = f"(paper {width} {height}"
        else:
            result = f"(paper {self.size.value}"

        if self.portrait:
            result += " portrait"

        result += ")"
        return result


class UUID(BaseModel):
    """
    Represents a KiCad UUID.
    Often described as: UNIQUE_IDENTIFIER in Kicad Docs
    """

    value: str

    @field_validator("value")
    @classmethod
    def validate_uuid(cls, v):
        """Validate that the UUID is in the correct format."""
        try:
            # Try to parse as UUID to validate format
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError("Invalid UUID format")

    @classmethod
    def from_sexpr(cls, sexpr: str) -> "UUID":
        """
        Parse a UUID from an s-expression string.

        Args:
            sexpr: String in format "(uuid UUID)"

        Returns:
            UUID object

        Raises:
            ValueError: If the s-expression is malformed
        """
        # Remove whitespace and newlines
        sexpr = re.sub(r"\s+", " ", sexpr.strip())

        # Basic format validation
        if not sexpr.startswith("(uuid") or not sexpr.endswith(")"):
            raise ValueError("Invalid UUID format")

        # Extract the content between parentheses
        content = sexpr[5:-1].strip()

        # Split into components
        parts = content.split()

        if len(parts) != 1:
            raise ValueError("UUID must have exactly one component")

        return cls(value=parts[0])

    def to_sexpr(self) -> str:
        """Convert the UUID to s-expression format."""
        return f"(uuid {self.value})"


class Image(BaseModel):
    """Represents a KiCad image with position, scale, layer, and data."""

    at: PositionIdentifier
    scale: Optional[float] = None
    layer: Optional[Layer] = None
    uuid: UUID
    data: str  # Base64 encoded image data

    @field_validator("scale")
    @classmethod
    def validate_scale(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Scale must be positive")
        return v

    @classmethod
    def from_sexpr(cls, sexpr: str) -> "Image":
        """
        Parse an image from an s-expression string.

        Args:
            sexpr: String in format "(image (at X Y [ANGLE]) [(scale SCALAR)] [(layer LAYER)] (uuid UUID) (data IMAGE_DATA))"

        Returns:
            Image object

        Raises:
            ValueError: If the s-expression is malformed
        """
        # Remove whitespace and newlines
        sexpr = re.sub(r"\s+", " ", sexpr.strip())

        # Basic format validation
        if not sexpr.startswith("(image") or not sexpr.endswith(")"):
            raise ValueError("Invalid image format")

        # Extract the content between parentheses
        content = sexpr[6:-1].strip()

        # Parse components
        at_match = re.search(r"\(at\s+([^)]+)\)", content)
        scale_match = re.search(r"\(scale\s+([^)]+)\)", content)
        layer_match = re.search(r'\(layer\s+"([^"]+)"\)', content)
        uuid_match = re.search(r'\(uuid\s+"([^"]+)"\)', content)
        data_match = re.search(r'\(data\s+"([^"]+)"\)', content)

        if not at_match or not uuid_match or not data_match:
            raise ValueError("Missing required image components")

        try:
            # Parse position
            at = PositionIdentifier.from_sexpr(at_match.group(0))

            # Parse scale if present
            scale = None
            if scale_match:
                scale = float(scale_match.group(1))

            # Parse layer if present
            layer = None
            if layer_match:
                layer = Layer(layer_match.group(1))

            # Parse UUID
            uuid = UUID.from_sexpr(f"(uuid {uuid_match.group(1)})")

            # Parse data
            data = data_match.group(1)

            return cls(at=at, scale=scale, layer=layer, uuid=uuid, data=data)
        except ValueError as e:
            raise ValueError(f"Invalid image values: {str(e)}")

    def to_sexpr(self) -> str:
        """Convert the image to s-expression format."""
        result = ["image", self.at.to_sexpr()]

        if self.scale is not None:
            result.append(f"(scale {self.scale})")

        if self.layer is not None:
            result.append(f'(layer "{self.layer.value}")')

        result.extend(
            [
                f'(uuid "{self.uuid.value}")',  # Add quotes around UUID
                f'(data "{self.data}")',
            ]
        )

        return "(" + " ".join(result) + ")"


class FootprintModel(BaseModel):
    """Model for a KiCad footprint module file."""

    name: str
    version: str
    generator: str
    generator_version: str
    layer: Layer
    description: str
    properties: List[Property]
    polygons: List[Polygon] = Field(default_factory=list)
    lines: List[Line] = Field(default_factory=list)
    pads: List[Pad] = Field(default_factory=list)

    @classmethod
    def from_sexp(cls, data: List[Any]) -> "FootprintModel":
        """Parse sexpdata format into FootprintModel.

        Args:
            data: List in format [Symbol('footprint'), name, [version], [generator], [generator_version], [layer], [description], properties, ...]
        """
        if not isinstance(data, list) or len(data) < 7:
            raise ValueError("Invalid footprint data format")

        if not isinstance(data[0], Symbol) or data[0].value() != "footprint":
            raise ValueError("Footprint data must start with 'footprint' symbol")

        # Parse basic attributes
        name = str(data[1])

        # Parse version
        if (
            not isinstance(data[2], list)
            or len(data[2]) != 2
            or not isinstance(data[2][0], Symbol)
            or data[2][0].value() != "version"
        ):
            raise ValueError("Invalid version format")
        version = str(data[2][1])

        # Parse generator
        if (
            not isinstance(data[3], list)
            or len(data[3]) != 2
            or not isinstance(data[3][0], Symbol)
            or data[3][0].value() != "generator"
        ):
            raise ValueError("Invalid generator format")
        generator = str(data[3][1])

        # Parse generator version
        if (
            not isinstance(data[4], list)
            or len(data[4]) != 2
            or not isinstance(data[4][0], Symbol)
            or data[4][0].value() != "generator_version"
        ):
            raise ValueError("Invalid generator version format")
        generator_version = str(data[4][1])

        # Parse layer
        if (
            not isinstance(data[5], list)
            or len(data[5]) != 2
            or not isinstance(data[5][0], Symbol)
            or data[5][0].value() != "layer"
        ):
            raise ValueError("Invalid layer format")
        layer = Layer(str(data[5][1]))

        # Parse description
        if (
            not isinstance(data[6], list)
            or len(data[6]) != 2
            or not isinstance(data[6][0], Symbol)
            or data[6][0].value() != "descr"
        ):
            raise ValueError("Invalid description format")
        description = str(data[6][1])

        # Parse properties, polygons, lines, and pads
        properties = []
        polygons = []
        lines = []
        pads = []

        for item in data[7:]:
            if not isinstance(item, list) or len(item) < 1:
                continue

            item_type = str(item[0])
            if item_type == "property":
                properties.append(Property.from_sexp(item))
            elif item_type == "fp_poly":
                polygons.append(Polygon.from_sexp(item))
            elif item_type == "fp_line":
                lines.append(Line.from_sexp(item))
            elif item_type == "pad":
                pads.append(Pad.from_sexp(item))

        return cls(
            name=name,
            version=version,
            generator=generator,
            generator_version=generator_version,
            layer=layer,
            description=description,
            properties=properties,
            polygons=polygons,
            lines=lines,
            pads=pads,
        )

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [
            Symbol("footprint"),
            self.name,
            [Symbol("version"), self.version],
            [Symbol("generator"), self.generator],
            [Symbol("generator_version"), self.generator_version],
            [Symbol("layer"), self.layer.value],
            [Symbol("descr"), self.description],
        ]

        # Add properties
        for prop in self.properties:
            result.append(prop.to_sexp())

        # Add polygons
        for poly in self.polygons:
            result.append(poly.to_sexp())

        # Add lines
        for line in self.lines:
            result.append(line.to_sexp())

        # Add pads
        for pad in self.pads:
            result.append(pad.to_sexp())

        return result


class SymbolValueModel(BaseModel):
    """Base model for s-expression data with a symbol and value."""

    symbol: str
    value: str

    @classmethod
    def from_sexp(cls, data: List[Any], expected_symbol: str) -> "SymbolValueModel":
        """Parse sexpdata format into SymbolValueModel.

        Args:
            data: List in format [Symbol(symbol), value]
            expected_symbol: The expected symbol name

        Returns:
            SymbolValueModel object

        Raises:
            ValueError: If the data format is invalid
        """
        if not isinstance(data, list) or len(data) != 2:
            raise ValueError("Invalid data format")

        if not isinstance(data[0], Symbol) or data[0].value() != expected_symbol:
            raise ValueError(f"Data must start with '{expected_symbol}' symbol")

        return cls(symbol=expected_symbol, value=str(data[1]))

    def to_sexp(self, wrap_symbol: bool = False) -> List[Any]:
        """Convert to sexpdata format."""
        return [
            Symbol(self.symbol),
            self.value if not wrap_symbol else Symbol(self.value),
        ]
