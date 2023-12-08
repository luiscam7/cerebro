"""Extends QEEG Aanalysis with peak detection and spectral analysis of resting state EEG, currently investigating alpha band activity (8-13 Hz)"""
from cerebrus.qeeg import QeegAnalysis
from fooof import FOOOFGroup


class SpectralAnalysis(QeegAnalysis):
    def __init__(self):
        super().__init__()
        pass
