import mne
from mne.io import Raw

from cerebro.base.parser import Parser


class EdfParser(Parser):
    """
    Class for parsing EEG data from EDF files using MNE.
    """

    def read_eeg(self, filepath: str) -> Raw:
        """
        Load EEG data from an EDF file.
        :param filepath: Path to the EDF file
        """
        raw = mne.io.read_raw_edf(filepath, preload=True)
        self.reconfigure_eeg_channels(raw)
        return self.load_eeg(raw)

    def load_eeg(self, raw: Raw) -> Raw:
        """
        Apply the standard 10-20 montage to the raw EEG data.
        :param raw: Raw EEG data
        """
        montage = mne.channels.make_standard_montage("standard_1020")
        raw.set_montage(montage)
        return raw

    def reconfigure_eeg_channels(self, raw: Raw) -> Raw:
        """
        Default implementation of reconfiguring EEG channels.
        This can be overridden in subclasses for specific behavior.
        :param raw: Raw EEG data
        """
        return raw
