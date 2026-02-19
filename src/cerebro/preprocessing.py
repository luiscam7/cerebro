"""
A collection of functions pertaining to processing EEG data for the removal of signal contamination from movement, muscle tension, and other sources of non-neurological signals.
"""

import logging

import numpy as np
from cerebro.utils.params import ECG_ARTIFACT_ICA_DETECTION_THRESHOLD
from mne.io import Raw
from typing import Tuple
from mne.preprocessing import ICA, create_ecg_epochs

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def eeg_filter(raw: Raw, l_freq: float = 1.0, h_freq: float = 25.0) -> Raw:
    """
    Bandpass filter on the raw eeg data

    Parameters:
    raw (Raw): The raw EEG data.
    l_freq (float): Low frequency cut off parameter. Frequencies below this value will be attenuated in the EEG spectrum.
    h_freq (float): High frequency cut off parameter. Frequencies above this value will be attenuated in the EEG spectrum. Default is 25.0 Hz (preserves delta to beta bands).


    Returns:
    Raw: The EEG data after bandpass filtering.
    """
    filtered_raw = raw.filter(
        l_freq=l_freq,
        h_freq=h_freq,
        picks="eeg",
        method="iir",
    )

    return filtered_raw


def remove_powerline_noise(raw: Raw) -> Tuple[Raw, bool]:
    """
    Removes power line noise from EEG data using a notch filter if necessary.

    Parameters:
    raw (Raw): The raw EEG data.

    Returns:
    Raw: The EEG data after potential notch filtering.
    bool: Boolean regarding wether powerline noise was detected and removed.
    """
    try:
        POWERLINE_NOISE_DETECTED_AND_REMOVED = False

        # Compute the power spectrum density (PSD) across all channels
        spectrum = raw.compute_psd(method="welch", picks="eeg", fmin=4, fmax=100)
        psd, freqs = spectrum.get_data(return_freqs=True)

        # Average the PSD across channels
        avg_psd = np.mean(psd, axis=0)

        # Define the frequency bins for 50 Hz and 60 Hz noise
        f_bin_50 = (freqs >= 48) & (freqs <= 52)
        f_bin_60 = (freqs >= 58) & (freqs <= 62)

        # Calculate the area under the curve using Simpson's rule
        max_amplitude_50 = max(avg_psd[f_bin_50])
        max_amplitude_60 = max(avg_psd[f_bin_60])

        # Calculate the total area excluding the 50 Hz and 60 Hz bins
        max_amplitude_full_spectrum = max(avg_psd[~(f_bin_50 | f_bin_60)])

        # Apply notch filters based on the energy in the specified bins
        freqs_to_notch = []
        if max_amplitude_50 > max_amplitude_full_spectrum:
            freqs_to_notch.append(50)
        if max_amplitude_60 > max_amplitude_full_spectrum:
            freqs_to_notch.append(60)

        if freqs_to_notch:
            logging.info(
                f"Powerline noise detected around frequencies {freqs_to_notch} Hz, notch filter will be applied."
            )
            filtered_raw = raw.copy().notch_filter(freqs=freqs_to_notch)
            POWERLINE_NOISE_DETECTED_AND_REMOVED = True
        else:
            logging.info("No Powerline noise detected in the EEG.")
            filtered_raw = raw.copy()

        return filtered_raw, POWERLINE_NOISE_DETECTED_AND_REMOVED
    except Exception as e:
        logging.error(
            f"An error occurred while removing powerline noise: {e} \nReturning original raw object."
        )
        return raw, POWERLINE_NOISE_DETECTED_AND_REMOVED


def remove_ecg_interference(
    raw: Raw,
    n_components: int = 15,
    method: str = "fastica",
    random_state: int = 7,
    ecg_threshold: float = ECG_ARTIFACT_ICA_DETECTION_THRESHOLD,
) -> Tuple[Raw, bool]:
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
    bool: A boolean regarding wether ecg contamination was detected and removed with ICA.
    """
    try:
        ECG_NOISE_DETECTED_AND_REMOVED = False
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
            logging.info(
                "ECG components detected, electrocargiographic interference removed with ICA."
            )
            ica.exclude.extend(ecg_inds)
            raw_ica = ica.apply(raw.copy())
            ECG_NOISE_DETECTED_AND_REMOVED = True
        else:
            raw_ica = raw.copy()

        return raw_ica, ECG_NOISE_DETECTED_AND_REMOVED

    except Exception as e:
        logging.error(
            f"An error occurred while removing ECG artifacts: {e} \nReturning original raw object."
        )
        return raw, ECG_NOISE_DETECTED_AND_REMOVED
