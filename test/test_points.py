from pathlib import Path

import pytest
import sexpdata
from sexpdata import Symbol

from src.models import Point, Points


def test_parse_points():
    # Read the sample file
    sample_path = Path(__file__).parent / "samples" / "pts.sexp"
    with open(sample_path, "r") as f:
        content = f.read()

    # Parse the sexpdata
    data = sexpdata.loads(content)
    print(data)

    # Create Points model
    points = Points.from_sexp(data)
    print(points)
    # Verify the points
    assert len(points.points) == 2
    assert points.points[0] == Point(x=66.6, y=67.7)
    assert points.points[1] == Point(x=66.7, y=70.1)

    # Test roundtrip conversion
    sexp = points.to_sexp()
    assert sexp[0] == Symbol("pts")
    assert sexp[1][0] == Symbol("xy")
    assert float(sexp[1][1]) == 66.6
    assert float(sexp[1][2]) == 67.7
    assert sexp[2][0] == Symbol("xy")
    assert float(sexp[2][1]) == 66.7
    assert float(sexp[2][2]) == 70.1


if __name__ == "__main__":
    test_parse_points()
    print("All tests passed!")
