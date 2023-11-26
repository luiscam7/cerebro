"""A module dedicated to organizing commonly used algorithms in QEEG analysis."""

import mne
from cerebrus.cerebro import Cerebro
from cerebrus.utils.params import (
    STABLE_FRONTAL_SENSORS,
    STABLE_CENTRAL_SENSORS,
    STABLE_POSTERIOR_SENSORS,
    NYQUIT_LIMIT
)

from typing import Dict, List, Tuple, Any


class PowerSpectralAnalysis(Cerebro):
    def __init__(self):
        super().__init__()
        self.spectrum = None
        self.psds = None
        self.freqs = None
        self.frontal_psds = None
        self.central_psds = None
        self.posterior_psds = None

    def compute_psd(self):
        """
        Calculate the Power Spectral Density (PSD) for each channel in Raw MNE object.
        """
        if self.data is None:
            raise ValueError("No data available. Load data before computing PSD.")

        # Calculate PSD
        self.spectrum = self.data.compute_psd(
            method="welch", picks="eeg", fmin=0, fmax=NYQUIT_LIMIT, n_overlap=256, n_per_seg=512
        )

        # Store PSD data in pandas dataframe, make it easier to process and convert data
        psd_df = self.spectrum.to_data_frame()
        self.psds, self.freqs = self.spectrum.get_data(return_freqs=True)

        # Convert DataFrame to Dictionary
        psd_dict = psd_df.to_dict(orient="list")

        self.analysis["power_spectral_density"] = psd_dict

    def compute_regional_psds(self):
        """
        Average out power spectrum density data across EEG channels by frontal, central, and posterior region.
        :param numpy array: Numpy array containing power spectral density data for EEG sensor data.
        """
        if self.spectrum is None:
            raise ValueError(
                "PSD data not available. Compute PSD before computing regional PSDs."
            )

        psd_df = self.spectrum.to_data_frame()

        # Average Power Spectral Density data from sensors by region.
        self.frontal_psds = psd_df[STABLE_FRONTAL_SENSORS].mean(axis=1)
        self.central_psds = psd_df[STABLE_CENTRAL_SENSORS].mean(axis=1)
        self.posterior_psds = psd_df[STABLE_POSTERIOR_SENSORS].mean(axis=1)

        regional_psd_dict = {
            "frontal": self.frontal_psds.tolist(),
            "central": self.central_psds.tolist(),
            "posterior": self.posterior_psds.tolist(),
            "freqs": self.freqs.tolist(),
        }

        self.analysis["regional_power_spectral_density"] = regional_psd_dict

    def analyze_data(self) -> Dict:
        super().analyze_data()
        self.compute_psd()
        self.compute_regional_psds()
        return self.analysis
