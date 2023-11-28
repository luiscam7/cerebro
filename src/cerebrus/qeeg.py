"""A module dedicated to organizing commonly used algorithms in QEEG analysis."""

import mne
import numpy as np
import pandas as pd
from numpy.typing import NDArray

from cerebrus.cerebro import Cerebro
from cerebrus.utils.params import (
    CHANNELS_10_20,
    NYQUIST_LIMIT,
    EEG_SPECTRUM,
    STABLE_FRONTAL_SENSORS,
    STABLE_CENTRAL_SENSORS,
    STABLE_POSTERIOR_SENSORS,
    FRONTAL_GENERATOR_THRESHOLD,
    LOW_VOLTAGE_THRESHOLD,
)

from cerebrus.utils.decorators import set_precision
from cerebrus.utils.dsp_utils import calculate_total_area_under_curve
from scipy.integrate import simps
from typing import Dict, List, Tuple, Any


class QeegAnalysis(Cerebro):
    def __init__(self):
        super().__init__()
        self.spectrum = None
        self.psd_data = None
        self.magnitude_data = None
        self.delta_power = None
        self.theta_power = None
        self.alpha_power = None
        self.beta_power = None
        self.delta_relative_power = None
        self.theta_relative_power = None
        self.alpha_relative_power = None
        self.beta_relative_power = None

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
            fmax=NYQUIST_LIMIT,
            n_overlap=256,
            n_per_seg=512,
        )

        # Store PSD data in pandas dataframe, make it easier to process and convert data
        self.psd_data = self.spectrum.to_data_frame()

        self.analysis["power_spectral_density"] = self.psd_data.to_dict(orient="list")

        return self.psd_data

    def compute_magnitude_spectra_from_psd(self) -> pd.DataFrame:
        """
        Calculate the Power Spectral Density (PSD) for each channel in Raw MNE object.
        """
        if self.psd_data is None:
            raise ValueError(
                "Power Spectral Density data is not available. Must be calculated first before converting to Magnitude "
            )

        columns_to_apply = self.psd_data.columns.difference(["freqs"])

        # Convert to microvolts, transform Power Spectral data to Magnitude spectral data.
        self.magnitude_data = (self.psd_data[columns_to_apply] * 1e12) ** 0.5

        self.analysis["magnitude_spectral_density"] = self.magnitude_data.to_dict(
            orient="list"
        )

        return self.magnitude_data

    def compute_absolute_power(self) -> None:
        """
        Computes the absolute power for each frequency band in EEG_SPECTRUM
        and updates the analysis dictionary with global and regional absolute power values.
        """
        self.analysis["absolute_power"] = {}
        columns_to_apply = self.psd_data.columns.difference(["freqs"])

        for frequency_band, band_range in EEG_SPECTRUM.items():
            band_absolute_power_df = self.psd_data[columns_to_apply].apply(
                lambda column: calculate_absolute_power(column, band_range), axis=0
            )
            self.analysis["absolute_power"][frequency_band] = band_absolute_power_df[
                CHANNELS_10_20
            ].to_dict()

            # Set the attribute for each power band
            setattr(
                self, f"{frequency_band}_power", band_absolute_power_df[CHANNELS_10_20]
            )

    def compute_relative_power(self) -> Dict:
        # Ensure absolute power for each band has been computed
        if "absolute_power" not in self.analysis:
            raise ValueError("Absolute power must be computed before relative power.")

        total_power = (
            self.delta_power + self.theta_power + self.alpha_power + self.beta_power
        )

        self.delta_relative_power = self.delta_power / total_power
        self.theta_relative_power = self.theta_power / total_power
        self.alpha_relative_power = self.alpha_power / total_power
        self.beta_relative_power = self.beta_power / total_power

        relative_power = {
            "delta": self.delta_relative_power.to_dict(),
            "theta": self.theta_relative_power.to_dict(),
            "alpha": self.alpha_relative_power.to_dict(),
            "beta": self.beta_relative_power.to_dict(),
        }

        self.analysis["relative_power"] = relative_power

        return relative_power

    def compute_power_ratios(self) -> Dict:
        """
        Computes power ratios between different EEG frequency bands.
        """
        # Ensure relative power for each band has been computed
        if "relative_power" not in self.analysis:
            raise ValueError("Relative power must be computed before power ratios.")

        # Compute power ratios
        theta_beta_ratio = self.theta_relative_power / self.beta_relative_power
        alpha_theta_ratio = self.alpha_relative_power / self.theta_relative_power

        # Store the results in the analysis dictionary
        power_ratios = {
            "theta_beta_ratio": theta_beta_ratio.to_dict(),
            "alpha_theta_ratio": alpha_theta_ratio.to_dict(),
        }

        self.analysis["power_ratios"] = power_ratios

        return power_ratios

    def determine_frontal_generator(self) -> bool:
        frontal_relative_alpha_power = self.alpha_relative_power[
            STABLE_FRONTAL_SENSORS
        ].mean()
        posterior_relative_alpha_power = self.alpha_relative_power[
            STABLE_POSTERIOR_SENSORS
        ].mean()

        frontal_posterior_power_ratio = (
            frontal_relative_alpha_power / posterior_relative_alpha_power
        )

        self.analysis["frontal_relative_alpha_power"] = frontal_relative_alpha_power
        self.analysis[
            "posterior_relative__alpha_power"
        ] = posterior_relative_alpha_power

        self.analysis["frontal_posterior_power_ratio"] = frontal_posterior_power_ratio
        self.analysis["frontal_generator"] = False

        if frontal_posterior_power_ratio >= FRONTAL_GENERATOR_THRESHOLD:
            self.analysis["frontal_generator"] = True

        return self.analysis["frontal_generator"]

    def determine_low_voltage(self) -> bool:
        frontal_alpha_scale = (
            self.magnitude_data[STABLE_FRONTAL_SENSORS]
            .mean(axis=1)
            .values[EEG_SPECTRUM["alpha"]]
        ).max()
        central_alpha_scale = (
            self.magnitude_data[STABLE_CENTRAL_SENSORS]
            .mean(axis=1)
            .values[EEG_SPECTRUM["alpha"]]
        ).max()
        posterior_alpha_scale = (
            self.magnitude_data[STABLE_POSTERIOR_SENSORS]
            .mean(axis=1)
            .values[EEG_SPECTRUM["alpha"]]
        ).max()

        self.analysis["low_voltage"] = False

        alpha_psd_scales = {
            "frontal": float(frontal_alpha_scale),
            "central": float(central_alpha_scale),
            "posterior": float(posterior_alpha_scale),
        }

        self.analysis["alpha_scales"] = alpha_psd_scales

        if (
            (frontal_alpha_scale <= LOW_VOLTAGE_THRESHOLD)
            and (central_alpha_scale <= LOW_VOLTAGE_THRESHOLD)
            and (posterior_alpha_scale <= LOW_VOLTAGE_THRESHOLD)
        ):
            self.analysis["low_voltage"] = True

        return self.analysis["low_voltage"]

    def analyze_data(self) -> Dict:
        super().analyze_data()
        self.compute_power_spectra()
        self.compute_magnitude_spectra_from_psd()
        self.compute_absolute_power()
        self.compute_relative_power()
        self.compute_power_ratios()
        self.determine_frontal_generator()
        self.determine_low_voltage()


def calculate_absolute_power(
    psd: np.ndarray, frequency_band: NDArray[np.bool_]
) -> float:
    partial_psd = psd[frequency_band]
    absolute_power = calculate_total_area_under_curve(partial_psd)
    return absolute_power
