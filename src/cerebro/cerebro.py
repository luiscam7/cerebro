"""
Cerebro is a central class designed for efficient parsing and preprocessing of EEG data, 
facilitating rapid research and development in neurological data analysis and application development. 
Leveraging the power of MNE-Python, Cerebro offers a streamlined approach to handling EEG datasets from 
various sources, providing essential functionalities for data loading, preprocessing, and analysis. 
Its modular design caters to the needs of EEG data analysts, researchers, and clinicians, 
accelerating the transition from raw data to insightful neurological interpretations.
"""
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Dict

import numpy as np
from mne.io import Raw

from cerebro.base import ICerebro
from cerebro.parser import ChbmpParser, TdbrainParser, TuhParser
from cerebro.preprocessing import (
    eeg_filter,
    remove_ecg_interference,
    remove_powerline_noise,
)
from cerebro.utils.writers import dict_to_json
from cerebro.version import __version__


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

        info = self.raw_data.info

        self.analysis["filepath"] = filepath.split("/")[-1]
        self.analysis["source"] = source
        self.analysis["measuring_date"] = info["meas_date"].isoformat()
        self.analysis["processed_date"] = datetime.now().isoformat()
        self.analysis["version"] = __version__
        self.analysis["sampling_rate"] = info["sfreq"]

        return self.raw_data.set_eeg_reference("average")

    def preprocess_data(self) -> Raw:
        """
        Preprocess the loaded data to remove or reduce the contamination from non-neurological noises coming from movement, bad EEG setup, powerline noise, and ecg interference.
        Essential step before processing the EEG data for neurological insights.
        :return: MNE Raw object containing the processed data.
        """
        if self.raw_data is None:
            raise ValueError("No raw data to preprocess. Please load the data first.")

        raw_eeg = self.raw_data.copy()
        self.filt_data = eeg_filter(raw_eeg)
        (
            self.filt_data,
            self.analysis["powerline_noise_detected"],
        ) = remove_powerline_noise(self.filt_data)
        self.filt_data, self.analysis["ecg_noise_detected"] = remove_ecg_interference(
            self.filt_data
        )

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

    def write_json(self, filename: str) -> None:
        """
        Save stored analysis data in JSON file format.
        """
        dict_to_json(self.analysis, filename)
