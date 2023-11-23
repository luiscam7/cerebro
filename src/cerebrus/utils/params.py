"""Organize all of the variables that correspond to constants and configurations across the module"""

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
