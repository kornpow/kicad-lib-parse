from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union, Tuple, Any, Literal
from enum import Enum
from sexpdata import Symbol
import re

class Layer(str, Enum):
    F_CU = "F.Cu"
    F_PASTE = "F.Paste"
    F_MASK = "F.Mask"
    F_SILKS = "F.SilkS"
    F_FAB = "F.Fab"
    F_CRTYD = "F.CrtYd"
    F_ADHES = "F.Adhes"

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

    @field_validator('thickness', 'line_spacing')
    @classmethod
    def validate_positive(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be positive')
        return v

class TextEffects(BaseModel):
    """Represents KiCad text effects with font and justification settings."""
    font: Font
    justify_horizontal: Optional[Literal["left", "right"]] = None
    justify_vertical: Optional[Literal["top", "bottom"]] = None
    mirror: bool = False
    hide: bool = False

    @classmethod
    def from_sexp(cls, data: List[Any]) -> 'TextEffects':
        """Parse sexpdata format into TextEffects model."""
        if not isinstance(data, list) or len(data) < 2:
            raise ValueError("Missing font settings")
            
        if not isinstance(data[0], Symbol) or data[0].value() != 'effects':
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
                if str(item[0]) == 'font':
                    if len(item) < 2:
                        raise ValueError("Missing font settings")
                    font_data = item
                elif str(item[0]) == 'justify':
                    for j in item[1:]:
                        j_str = str(j)
                        if j_str in ['left', 'right']:
                            justify_h = j_str
                        elif j_str in ['top', 'bottom']:
                            justify_v = j_str
                        elif j_str == 'mirror':
                            mirror = True
            elif str(item) == 'hide':
                hide = True
                
        if font_data is None:
            raise ValueError("Missing font settings")
            
        font = cls._parse_font(font_data)
        return cls(font=font, justify_horizontal=justify_h, justify_vertical=justify_v,
                  mirror=mirror, hide=hide)

    @staticmethod
    def _parse_font(data: List[Any]) -> Font:
        """Parse font settings from sexpdata format."""
        font_data = {
            'face': None,
            'height': 1.0,
            'width': 1.0,
            'thickness': None,
            'bold': False,
            'italic': False,
            'line_spacing': None
        }
        
        for item in data[1:]:
            if isinstance(item, list):
                if len(item) < 2:
                    continue
                item_type = str(item[0])
                if item_type == 'face':
                    font_data['face'] = str(item[1]).strip('"')
                elif item_type == 'size':
                    if len(item) < 3:
                        raise ValueError("Missing font settings")
                    font_data['height'] = float(item[1])
                    font_data['width'] = float(item[2])
                elif item_type == 'thickness':
                    if len(item) < 2:
                        raise ValueError("Missing font settings")
                    font_data['thickness'] = float(item[1])
                elif item_type == 'line_spacing':
                    if len(item) < 2:
                        raise ValueError("Missing font settings")
                    font_data['line_spacing'] = float(item[1])
            elif str(item) == 'bold':
                font_data['bold'] = True
            elif str(item) == 'italic':
                font_data['italic'] = True
                
        return Font(**font_data)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = ['effects']
        
        # Font settings
        font_parts = ['font']
        if self.font.face:
            font_parts.append(['face', f'"{self.font.face}"'])
        font_parts.append(['size', str(self.font.height), str(self.font.width)])
        if self.font.thickness:
            font_parts.append(['thickness', str(self.font.thickness)])
        if self.font.bold:
            font_parts.append('bold')
        if self.font.italic:
            font_parts.append('italic')
        if self.font.line_spacing:
            font_parts.append(['line_spacing', str(self.font.line_spacing)])
        result.append(font_parts)
        
        # Justification and other settings
        if self.justify_horizontal or self.justify_vertical or self.mirror:
            justify_parts = ['justify']
            if self.justify_horizontal:
                justify_parts.append(self.justify_horizontal)
            if self.justify_vertical:
                justify_parts.append(self.justify_vertical)
            if self.mirror:
                justify_parts.append('mirror')
            result.append(justify_parts)
            
        if self.hide:
            result.append('hide')
            
        return result

class Property(BaseModel):
    name: str
    value: str
    at: Tuple[float, float, float]
    layer: Layer
    effects: Optional[TextEffects] = None
    unlocked: Optional[bool] = None
    hide: Optional[bool] = None
    uuid: Optional[str] = None

class Stroke(BaseModel):
    """Model for stroke definitions in KiCad format."""
    width: float
    type: StrokeType = StrokeType.SOLID
    color: Optional[Tuple[int, int, int, int]] = None  # RGBA color values

    @classmethod
    def from_sexp(cls, data: List[Any]) -> 'Stroke':
        """Parse sexpdata format into Stroke model.
        
        Args:
            data: List in format [Symbol('stroke'), [Symbol('width'), value], [Symbol('type'), value], [Symbol('color'), r, g, b, a]]
        """
        print(data)
        if not isinstance(data, list) or len(data) < 3:
            raise ValueError("Invalid stroke data format")
            
        # if not isinstance(data[0], Symbol) or
        if str(data[0]) != 'stroke':
            raise ValueError("Stroke data must start with 'stroke' symbol")
            
        width_data = data[1]
        type_data = data[2]
        
        if not isinstance(width_data, list) or len(width_data) != 2:
            raise ValueError(f"Invalid width format: {width_data}")
        if not isinstance(type_data, list) or len(type_data) != 2:
            raise ValueError(f"Invalid type format: {type_data}")
            
        # if not isinstance(width_data[0], Symbol) or 
        if str(width_data[0]) != 'width':
            raise ValueError(f"Width must start with 'width' symbol: {width_data}")
        # if not isinstance(type_data[0], Symbol) or 
        if str(type_data[0]) != 'type':
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
            if str(color_data[0]) != 'color':
                raise ValueError(f"Color must start with 'color' symbol: {color_data}")
            try:
                color = (
                    int(color_data[1]),
                    int(color_data[2]),
                    int(color_data[3]),
                    int(color_data[4])
                )
            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid color values: {color_data}") from e
                
        return cls(width=width, type=type_, color=color)

    def to_sexp(self) -> List[Any]:
        """Convert to sexpdata format."""
        result = [
            'stroke',
            ['width', str(self.width)],
            ['type', self.type]
        ]
        if self.color is not None:
            result.append(['color'] + [str(c) for c in self.color])
        return result

class Point(BaseModel):
    x: float
    y: float

class Points(BaseModel):
    """Model for a list of X/Y coordinate points in KiCad format."""
    points: List[Point] = Field(description="List of X/Y coordinate points")

    @classmethod
    def from_sexp(cls, data: List[Any]) -> 'Points':
        """Parse sexpdata format into Points model.
        
        Args:
            data: List in format [Symbol('pts'), [Symbol('xy'), x1, y1], [Symbol('xy'), x2, y2], ...]
        """
        if not isinstance(data, list) or len(data) < 2:
            raise ValueError("Invalid points data format")
            
        if not isinstance(data[0], Symbol) or data[0].value() != 'pts':
            raise ValueError("Points data must start with 'pts' symbol")
            
        points = []
        for item in data[1:]:
            if not isinstance(item, list) or len(item) != 3:
                raise ValueError(f"Invalid point format: {item}")
                
            if not isinstance(item[0], Symbol) or item[0].value() != 'xy':
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
        return ['pts'] + [['xy', str(pt.x), str(pt.y)] for pt in self.points]

class Polygon(BaseModel):
    points: Points
    stroke: Optional[Stroke] = None
    fill: str = "solid"
    layer: Layer
    uuid: Optional[str] = None

class Line(BaseModel):
    start: Point
    end: Point
    stroke: Stroke
    layer: Layer
    uuid: Optional[str] = None

class Pad(BaseModel):
    number: str
    type: str
    shape: str
    at: Tuple[float, float, float]
    size: Tuple[float, float]
    layers: List[Layer]
    roundrect_rratio: Optional[float] = None
    solder_mask_margin: Optional[float] = None
    thermal_bridge_angle: Optional[float] = None
    uuid: Optional[str] = None

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

class PositionIdentifier(BaseModel):
    """Represents a KiCad position identifier with X, Y coordinates and optional angle."""
    x: float
    y: float
    angle: Optional[float] = None

    @classmethod
    def from_sexpr(cls, sexpr: str) -> 'PositionIdentifier':
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
        sexpr = re.sub(r'\s+', ' ', sexpr.strip())
        
        # Basic format validation
        if not sexpr.startswith('(at') or not sexpr.endswith(')'):
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

