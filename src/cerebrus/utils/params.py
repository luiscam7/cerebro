"""Organize all of the variables that correspond to constants and configurations across the project."""
import numpy as np


# Configuration constants

# Threshold for determining certain EEG phenotypes

# Describes the ratio between frontal and posterior relative power.
FRONTAL_GENERATOR_THRESHOLD = 0.7

# If the scale across all regions falls below this value in terms of microvolts, case is classified as Low voltage
LOW_VOLTAGE_THRESHOLD = 2.5

# Set precision for all float outputs
DEFAULT_FLOAT_PRECISION = 2

# EEG Band definitions

EEG_SPECTRUM_BANDS = {
    "delta": (0.5, 4),
    "theta": (4, 8),
    "alpha": (8, 13),
    "beta": (13, 30),
}


# Set ECG interference threshold (0 to 1). A value near 1 implies a higher likelihood of ECG interference. This threshold guides ICA removal of ECG artifacts. Higher values decrease the risk of incorrect ICA application.
ECG_ARTIFACT_ICA_DETECTION_THRESHOLD = 0.75

# List the 19 channels that correspond to the 10-20 system.

CHANNELS_10_20 = [
    "Fp1",
    "Fp2",
    "F3",
    "F4",
    "C3",
    "C4",
    "P3",
    "P4",
    "O1",
    "O2",
    "F7",
    "F8",
    "T3",
    "T4",
    "T5",
    "T6",
    "Fz",
    "Cz",
    "Pz",
]

# Maps EEG channels from 10-10 system to their 10-20 equivalent.

CONVERT_TO_10_20 = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F3": "F3",
    "F4": "F4",
    "C3": "C3",
    "C4": "C4",
    "P3": "P3",
    "P4": "P4",
    "O1": "O1",
    "O2": "O2",
    "F7": "F7",
    "F8": "F8",
    "T7": "T3",  # T7 in 10-10 corresponds to T3 in 10-20
    "T8": "T4",  # T8 in 10-10 corresponds to T4 in 10-20
    "P7": "T5",  # P7 in 10-10 corresponds to T5 in 10-20
    "P8": "T6",  # P8 in 10-10 corresponds to T6 in 10-20
    "Fz": "Fz",
    "Cz": "Cz",
    "Pz": "Pz",
}

TDBRAIN_CHANNEL_MAPPING = {
    "Fp1": "Fp1",
    "Fp2": "Fp2",
    "F7": "F7",
    "F3": "F3",
    "Fz": "Fz",
    "F4": "F4",
    "F8": "F8",
    "T7": "T3",
    "C3": "C3",
    "Cz": "Cz",
    "C4": "C4",
    "T8": "T4",
    "P7": "T5",
    "P3": "P3",
    "Pz": "Pz",
    "P4": "P4",
    "P8": "T6",
    "O1": "O1",
    "Oz": "Oz",
    "O2": "O2",
}

# Assign sensors to regions in the EEG

STABLE_FRONTAL_SENSORS = ["Fz", "F3", "F4"]
STABLE_CENTRAL_SENSORS = ["Cz", "C3", "C4"]
STABLE_POSTERIOR_SENSORS = ["Pz", "P3", "P4", "O1", "O2"]


ALL_FRONTAL_SENSORS = ["Fz", "F3", "F4", "F7", "F8", "Fp1", "Fp2"]
ALL_CENTRAL_SENSORS = ["Cz", "C3", "C4", "T3", "T4"]
ALL_POSTERIOR_SENSORS = ["Pz", "P3", "P4", "O1", "O2"]
