import json
import numpy as np


from typing import Any, Dict


def dict_to_json(data: Dict[str, Any], filename: str) -> None:
    """
    Writes a dictionary to a JSON file.

    :param data: Dictionary to be written to a JSON file.
    :param filename: Path to the output JSON file.
    """
    # Convert any NumPy arrays in self.analysis to lists

    with open(filename, "w") as json_file:
        for key, value in data.items():
            # Convert lists to NumPy arrays for consistency
            if isinstance(value, np.ndarray):
                data[key] = value.tolist()

        json.dump(data, json_file)
