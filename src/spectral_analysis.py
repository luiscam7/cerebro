"""Extends QEEG Aanalysis with peak detection and spectral analysis of resting state EEG, currently investigating alpha band activity (8-13 Hz)"""

import pandas as pd
from cerebro.qeeg import QeegAnalysis
from cerebro.utils.params import CHANNELS_10_20, ALPHA_BAND
from fooof import FOOOFGroup
from typing import Dict


class SpectralAnalysis(QeegAnalysis):
    def __init__(self):
        super().__init__()

    def peak_detection(self) -> pd.DataFrame:
        foo = FOOOFGroup()

        freq = self.power_spectrum["freq"].values
        power_spectra = self.power_spectrum[CHANNELS_10_20].values.T

        foo.fit(freq, power_spectra, freq_range=ALPHA_BAND)

        peak_data = foo.get_params(name="peak_params")

        peak_df = pd.DataFrame(
            peak_data, columns=("freq", "power", "bandwidth", "channel_idx")
        )
        peak_df["channel"] = peak_df["channel_idx"].apply(
            lambda x: CHANNELS_10_20[int(x)]
        )

        peak_df["q_factor"] = peak_df["power"] / peak_df["bandwidth"]

        self.analysis["foof_results"] = peak_df.to_dict(orient="list")
        return peak_df

    def analyze_data(self) -> Dict:
        super().analyze_data()
        self.peak_detection()
