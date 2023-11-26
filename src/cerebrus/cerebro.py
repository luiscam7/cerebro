"""
Cerebro is a central class designed for efficient parsing and preprocessing of EEG data, 
facilitating rapid research and development in neurological data analysis and application development. 
Leveraging the power of MNE-Python, Cerebro offers a streamlined approach to handling EEG datasets from 
various sources, providing essential functionalities for data loading, preprocessing, and analysis. 
Its modular design caters to the needs of EEG data analysts, researchers, and clinicians, 
accelerating the transition from raw data to insightful neurological interpretations.
"""
from dataclasses import dataclass
from mne.io import Raw
from cerebrus.base import ICerebro
from cerebrus.parser import ChbmpParser, TuhParser, TdbrainParser
from cerebrus.preprocessing import (
    eeg_filter,
    remove_powerline_noise,
    remove_ecg_interference,
)
from cerebrus.utils.params import DEFAULT_SAMPLING_RATE
from typing import Dict


@dataclass
class Cerebro(ICerebro):
    """
    Concrete class for interacting with MNE for neurological data analysis and visualization.
    """

    def __init__(self):
        self.raw_data = None
        self.filt_data = None
        self.data = None
        self.analysis = {}

    def load_data(self, filepath: str, source: str = "tuh") -> Raw:
        """
        Load data from a file using MNE's Raw object.
        :param filepath: path to the EEG data file.
        :return MNE Raw object contianing the loaded EEG data.
        """

        if source == "chbmp":
            parser = ChbmpParser()
        elif source == "tuh":
            parser = TuhParser()
        elif source == "tdbrain":
            parser = TdbrainParser()
        else:
            raise KeyError("Cerebro does not currently support EEG from data source.")

        self.raw_data = parser.read_eeg(filepath)

        return self.raw_data

    def preprocess_data(self) -> Raw:
        """
        Preprocess the loaded data to remove or reduce the contamination from non-neurological noises coming from movement, bad EEG setup, powerline noise, and ecg interference.
        Essential step before processing the EEG data for neurological insights.
        :return: MNE Raw object containing the processed data.
        """
        if self.raw_data is None:
            raise ValueError("No raw data to preprocess. Please load the data first.")

        self.raw_data.resample(sfreq=DEFAULT_SAMPLING_RATE)
        self.filt_data = eeg_filter(self.raw_data)
        self.filt_data, self.analysis['powerline_noise_detected'] = remove_powerline_noise(self.filt_data)
        self.filt_data, self.analysis['ecg_noise_detected'] = remove_ecg_interference(self.filt_data)

        return self.filt_data

    def analyze_data(self) -> Dict:
        """
        Analyze the preprocessed data. This could include power spectral
        density analysis, ERP analysis, etc.
        :return: Analysis results
        """
        if self.raw_data is None and self.filt_data is None:
            raise ValueError("No raw or processed EEG data to analyze.")
        if self.raw_data:
            self.data = self.raw_data
        if self.filt_data:
            self.data = self.filt_data
