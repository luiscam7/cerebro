import abc
from typing import Any, Dict
from mne.io import Raw


class ICerebro(abc.ABC):
    """
    Abstract base class for objects that interact with MNE for
    neurological data analysis and visualization.
    """

    @abc.abstractmethod
    def load_data(self, filepath: str) -> Raw:
        """
        Load data from a file.
        :param filepath: Path to the file.
        """
        pass

    @abc.abstractmethod
    def preprocess_data(self, **kwargs: Any) -> Raw:
        """
        Preprocess the loaded data.
        :param kwargs: Additional arguments for preprocessing.
        """
        pass

    @abc.abstractmethod
    def analyze_data(self) -> Dict:
        """
        Analyze the preprocessed data.
        """
        pass
