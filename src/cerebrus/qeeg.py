"""A module dedicated to organizing commonly used algorithms in QEEG analysis."""

import mne
from typing import Dict, List, Tuple, Any


def calculate_psd(
    raw: mne.io.Raw,
) -> Tuple[Dict[str, List[float]], Any, Any]:
    """
    Calculate the Power Spectral Density (PSD) for each channel in Raw MNE object.

    :param raw: MNE Raw object containing EEG data.
    :return: Dictionary where keys are frequencies and values are lists of PSD values for each channel.
    """
    # Calculate PSD
    spectrum = raw.compute_psd(method="welch", picks="eeg", fmin=0, fmax=100)

    psd_df = spectrum.to_data_frame()
    psd, freqs = spectrum.get_data(return_freqs=True)

    # Convert DataFrame to Dictionary
    psd_dict = psd_df.to_dict(orient="list")

    return psd_dict, psd, freqs
