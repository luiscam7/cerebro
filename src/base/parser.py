import abc
from mne.io import Raw


class Parser(abc.ABC):
    """
    Abstract base class for objects that interact with MNE in parsing EEG data
    from various systems across physiological datasets.
    """

    @abc.abstractmethod
    def read_eeg(self, filepath: str) -> Raw:
        """
        Abstract method to load EEG data from a file.
        :param filepath: Path to the file
        """
        pass

    @abc.abstractmethod
    def load_eeg(self, raw: Raw) -> Raw:
        """
        Abstract method to perform initial processing on the raw EEG data.
        :param raw: Raw EEG data
        """
        pass

    @abc.abstractmethod
    def reconfigure_eeg_channels(self, raw: Raw) -> Raw:
        """
        Abstract method to reconfigure EEG channels in the raw data.
        :param raw: Raw EEG data
        """
        pass
