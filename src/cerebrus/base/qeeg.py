import abc
from cerebrus.base import ICerebro
from typing import Dict


class IPowerSpectralAnalysis(ICerebro):
    def __init__(self):
        @abc.abstractmethod
        def compute_psd(self) -> None:
            """
            Compute Power Spectral Density for all 19 channels.
            :param None
            """
            pass

        @abc.abstractmethod
        def compute_regional_psds(self) -> None:
            """
            Compute Power Spectral Density for Frontal, Central, and Posterior regions.
            """
            pass
