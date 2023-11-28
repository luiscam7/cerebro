import json
import h5py
import numpy as np


from typing import Any, Dict


def dict_to_json(data: Dict[str, Any], filename: str) -> None:
    """
    Writes a dictionary to a JSON file.

    :param data: Dictionary to be written to a JSON file.
    :param filename: Path to the output JSON file.
    """
    with open(filename, "w") as json_file:
        json.dump(data, json_file)


def dict_to_hdf5(data: Dict[str, Any], filename: str) -> None:
    """
    Writes a dictionary to an HDF5 file.

    :param data: Dictionary with data to be written to the HDF5 file.
    :param filename: Path to the output HDF5 file.
    """
    with h5py.File(filename, "w") as hdf:
        for key, value in data.items():
            # Ensure the value is an array-like structure
            if not isinstance(value, (list, np.ndarray)):
                raise ValueError(
                    f"The value for key '{key}' is not a list or NumPy array."
                )

            # Convert lists to NumPy arrays for consistency
            if isinstance(value, list):
                value = np.array(value)

            hdf.create_dataset(key, data=value)
