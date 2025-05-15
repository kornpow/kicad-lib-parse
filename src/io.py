from pathlib import Path
from typing import Any, List

import sexpdata


def write_footprint_to_file(footprint_list: List[Any], output_path: Path) -> None:
    """Write a footprint list to a sexp file format.

    Args:
        footprint_list: List containing the footprint data in sexp format
        output_path: Path where the file should be written
    """
    # Convert the list to a string representation
    sexp_str = sexpdata.dumps(footprint_list)

    # Write to file
    with open(output_path, "w") as f:
        f.write(sexp_str)
