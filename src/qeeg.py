"""A module dedicated to organizing commonly used algorithms in QEEG analysis."""

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from cerebro.cerebro import Cerebro
from cerebro.utils.params import (
    CHANNELS_10_20,
    DELTA_BAND,
    THETA_BAND,
    ALPHA_BAND,
    BETA_BAND,
    EEG_SPECTRUM_BANDS,
    STABLE_FRONTAL_SENSORS,
    STABLE_CENTRAL_SENSORS,
    STABLE_POSTERIOR_SENSORS,
    FRONTAL_GENERATOR_THRESHOLD,
    LOW_VOLTAGE_THRESHOLD,
)

from neurodsp.spectral import (
    compute_absolute_power,
    compute_relative_power,
    compute_band_ratio,
    trim_spectrum,
)
from typing import Dict


class QeegAnalysis(Cerebro):
    def __init__(self):
        super().__init__()
        self.spectrum = None
        self.power_spectrum = None
        self.magnitude_spectrum = None

    def compute_power_spectra(self) -> pd.DataFrame:
        """
        Calculate the Power Spectral Density (PSD) for each channel in Raw MNE object.
        """
        if self.data is None:
            raise ValueError("No data available. Load data before computing PSD.")

        # Calculate PSD
        self.spectrum = self.data.compute_psd(
            method="welch",
            picks="eeg",
            fmin=0,
            fmax=100,
            n_overlap=256,
            n_per_seg=512,
        )

        # Store PSD data in pandas dataframe, make it easier to process and convert data
        self.power_spectrum = self.spectrum.to_data_frame()

        self.analysis["power_spectral_density"] = self.power_spectrum.to_dict(
            orient="list"
        )

        # Define frequency bands for downstream QEEG processing.
        self.set_frequency_indexing()

        return self.power_spectrum

    def set_frequency_indexing(self):
        """
        Set up boolean indexing to simplify QEEG processing logic across bands.
        """
        frequencies = self.power_spectrum["freq"].values

        for frequency_band, band_range in EEG_SPECTRUM_BANDS.items():
            f1, f2 = band_range

            # Set the attribute for each power band
            setattr(
                self, f"{frequency_band}_band", (frequencies > f1) & (frequencies <= f2)
            )

    def compute_magnitude_spectra_from_psd(self) -> pd.DataFrame:
        """
        Calculate the Power Spectral Density (PSD) for each channel in Raw MNE object.
        """
        if self.power_spectrum is None:
            raise ValueError(
                "Power Spectral Density data is not available. Must be calculated first before converting to Magnitude "
            )

        # Convert to microvolts, transform Power Spectral data to Magnitude spectral data.
        self.magnitude_spectrum = (self.power_spectrum[CHANNELS_10_20] * 1e12) ** 0.5
        self.magnitude_spectrum["freq"] = self.power_spectrum["freq"]

        self.analysis["magnitude_spectral_density"] = self.magnitude_spectrum.to_dict(
            orient="list"
        )

        return self.magnitude_spectrum

    def calculate_absolute_power(self) -> Dict:
        """
        Computes the absolute power for each frequency band in eeg spectrum (delta, theta, alpha, and beta)
        """
        absolute_power = {"delta": {}, "theta": {}, "alpha": {}, "beta": {}}

        frequencies = self.power_spectrum["freq"].values

        for channel in CHANNELS_10_20:
            channel_psd = self.power_spectrum[channel].values
            absolute_power["delta"][channel] = compute_absolute_power(
                frequencies, channel_psd, band=DELTA_BAND
            )
            absolute_power["theta"][channel] = compute_absolute_power(
                frequencies, channel_psd, band=THETA_BAND
            )
            absolute_power["alpha"][channel] = compute_absolute_power(
                frequencies, channel_psd, band=ALPHA_BAND
            )
            absolute_power["beta"][channel] = compute_absolute_power(
                frequencies, channel_psd, band=BETA_BAND
            )
        self.analysis["absolute_power"] = absolute_power

        return self.analysis["absolute_power"]

    def calculate_relative_power(self) -> Dict:
        """
        Computes the relative power for each frequency band in eeg spectrum (delta, theta, alpha, beta).
        """

        relative_power = {"delta": {}, "theta": {}, "alpha": {}, "beta": {}}

        frequencies = self.power_spectrum["freq"].values

        for channel in CHANNELS_10_20:
            channel_psd = self.power_spectrum[channel].values
            relative_power["delta"][channel] = compute_relative_power(
                frequencies,
                channel_psd,
                band=DELTA_BAND,
                norm_range=[DELTA_BAND[0], BETA_BAND[1]],
            )
            relative_power["theta"][channel] = compute_relative_power(
                frequencies,
                channel_psd,
                band=THETA_BAND,
                norm_range=[DELTA_BAND[0], BETA_BAND[1]],
            )
            relative_power["alpha"][channel] = compute_relative_power(
                frequencies,
                channel_psd,
                band=ALPHA_BAND,
                norm_range=[DELTA_BAND[0], BETA_BAND[1]],
            )
            relative_power["beta"][channel] = compute_relative_power(
                frequencies,
                channel_psd,
                band=BETA_BAND,
                norm_range=[DELTA_BAND[0], BETA_BAND[1]],
            )

        self.analysis["relative_power"] = relative_power

        return self.analysis["relative_power"]

    def calculate_power_ratios(self) -> Dict:
        """
        Computes power ratios between different EEG frequency bands.
        """

        power_ratios = {"theta_beta_ratio": {}, "alpha_theta_ratio": {}}

        frequencies = self.power_spectrum["freq"].values

        for channel in CHANNELS_10_20:
            channel_psd = self.power_spectrum[channel].values
            power_ratios["theta_beta_ratio"][channel] = compute_band_ratio(
                frequencies, channel_psd, THETA_BAND, BETA_BAND
            )
            power_ratios["alpha_theta_ratio"][channel] = compute_band_ratio(
                frequencies, channel_psd, ALPHA_BAND, THETA_BAND
            )

        self.analysis["power_ratios"] = power_ratios

        return self.analysis["power_ratios"]

    def determine_frontal_generator(self) -> bool:
        """
        Use the ratio between frontal abdolute power over posterior absolute power to determine frontal generators.
        """
        if self.analysis["relative_power"] is None:
            raise ValueError(
                "Relative power data not available. Required for determining frontal generator status."
            )

        alpha_relative_power = self.analysis["relative_power"]["alpha"]

        frontal_alpha_relative_power = np.mean(
            [alpha_relative_power[sensor] for sensor in STABLE_FRONTAL_SENSORS]
        )
        posterior_alpha_relative_power = np.mean(
            [alpha_relative_power[sensor] for sensor in STABLE_POSTERIOR_SENSORS]
        )

        frontal_posterior_power_ratio = (
            frontal_alpha_relative_power / posterior_alpha_relative_power
        )

        self.analysis["frontal_alpha_relative_power"] = frontal_alpha_relative_power
        self.analysis["posterior_alpha__relative_power"] = (
            posterior_alpha_relative_power
        )

        self.analysis["frontal_posterior_relative_power_ratio"] = (
            frontal_posterior_power_ratio
        )
        self.analysis["frontal_generator"] = False

        if frontal_posterior_power_ratio >= FRONTAL_GENERATOR_THRESHOLD:
            self.analysis["frontal_generator"] = True

        return self.analysis["frontal_generator"]

    def determine_low_voltage(self) -> bool:
        """
        Determine low voltage cases if every regional spectra is below 2.5 microvolts.
        """
        self.analysis["low_voltage"] = False

        frequencies = self.magnitude_spectrum["freq"].values
        magnitude_spectra = self.magnitude_spectrum[CHANNELS_10_20].values.T

        alpha_freq, alpha_magnitude_spectrum = trim_spectrum(
            frequencies, magnitude_spectra, f_range=[THETA_BAND[0], BETA_BAND[1]]
        )

        alpha_max_amp = np.max(alpha_magnitude_spectrum)
        self.analysis["max_amp_microvolts"] = float(alpha_max_amp)

        print(alpha_max_amp)

        if alpha_max_amp < LOW_VOLTAGE_THRESHOLD:
            self.analysis["low_voltage"] = True

        return self.analysis["low_voltage"]

    def analyze_data(self) -> Dict:
        super().analyze_data()
        self.compute_power_spectra()
        self.compute_magnitude_spectra_from_psd()
        self.calculate_absolute_power()
        self.calculate_relative_power()
        self.calculate_power_ratios()
        self.determine_frontal_generator()
        self.determine_low_voltage()
