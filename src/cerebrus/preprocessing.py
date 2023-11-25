""" 
A collection of functions pertaining to processing EEG data for the removal of signal contamination from movement, muscle tension, and other sources of non-neurological signals.
"""
import logging

import numpy as np
from cerebrus.utils.params import ECG_ARTIFACT_ICA_DETECTION_THRESHOLD
from mne.io import Raw
from mne.preprocessing import ICA, create_ecg_epochs
from scipy.integrate import simps

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def eeg_filter(raw: Raw, l_freq: float = 1, h_freq: float = None) -> Raw:
    filtered_raw = raw.filter(
        l_freq=l_freq,
        h_freq=h_freq,
        picks="eeg",
        method="iir",
    )

    return filtered_raw


def remove_powerline_noise(raw: Raw) -> Raw:
    """
    Removes power line noise from EEG data using a notch filter if necessary.

    Parameters:
    raw (Raw): The raw EEG data.

    Returns:
    Raw: The EEG data after potential notch filtering.
    """
    # Compute the power spectrum density (PSD) across all channels
    spectrum = raw.compute_psd(method="welch", picks="eeg", fmin=4, fmax=100)
    psd, freqs = spectrum.get_data(return_freqs=True)

    # Average the PSD across channels
    avg_psd = np.mean(psd, axis=0)

    # Define the frequency bins for 50 Hz and 60 Hz noise
    f_bin_50 = (freqs >= 48) & (freqs <= 52)
    f_bin_60 = (freqs >= 58) & (freqs <= 62)

    # Calculate the area under the curve using Simpson's rule
    area_50 = simps(avg_psd[f_bin_50], dx=freqs[1] - freqs[0])
    area_60 = simps(avg_psd[f_bin_60], dx=freqs[1] - freqs[0])

    # Calculate the total area excluding the 50 Hz and 60 Hz bins
    total_area = simps(avg_psd[~(f_bin_50 | f_bin_60)], dx=freqs[1] - freqs[0])

    # Apply notch filters based on the energy in the specified bins
    freqs_to_notch = []
    if area_50 > total_area:
        freqs_to_notch.append(50)
    if area_60 > total_area:
        freqs_to_notch.append(60)

    if freqs_to_notch:
        filtered_raw = raw.copy().notch_filter(freqs=freqs_to_notch)
    else:
        filtered_raw = raw.copy()

    return filtered_raw


def remove_ecg_interference(
    raw: Raw,
    n_components: int = 15,
    method: str = "fastica",
    random_state: int = 7,
    ecg_threshold: float = ECG_ARTIFACT_ICA_DETECTION_THRESHOLD,
) -> Raw:
    """
    Detect and remove ECG interference from EEG data using ICA.

    Parameters:
    raw (Raw): The raw EEG data.
    n_components (int): Number of ICA components to compute. Default is 15.
    method (str): The ICA method to use. Default is 'fastica'.
    random_state (int): Random state for reproducibility. Default is 7.
    ecg_threshold (float | 0.75): Value above which a feature is classified as outlier.

    Returns:
    Raw: The EEG data after ECG artifact removal.
    """
    try:
        # Filtering the data for ICA analysis
        filt_raw = raw.copy().filter(l_freq=1.0, h_freq=30, verbose="warning")

        # Fit ICA
        ica = ICA(n_components=n_components, method=method, random_state=random_state)
        ica.fit(filt_raw)

        # Detect the ECG artifacts
        ecg_epochs = create_ecg_epochs(filt_raw, tmin=-0.5, tmax=0.5, baseline=None)
        ecg_inds, scores = ica.find_bads_ecg(
            ecg_epochs, method="ctps", threshold=ecg_threshold
        )
        # If ECG components detected, remove them
        if ecg_inds:
            ica.exclude.extend(ecg_inds)
            raw_ica = ica.apply(raw.copy())
        else:
            raw_ica = raw.copy()

        return raw_ica

    except Exception as e:
        logging.error(f"An error occurred while removing ECG artifacts: {e}")
        return raw
