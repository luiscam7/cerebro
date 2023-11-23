import mne

def read_eeg_data(filepath: str):
    """
    Reads an EDF file and extracts channels according to the 10-20 system.

    :param filepath: Path to the EDF file.
    :return: Raw data object containing only the 10-20 system channels.
    """

    # Define the 10-20 system channels
    channels_10_20 = ["Fp1", "Fp2", "F3", "F4", "C3", "C4", "P3", "P4", "O1", "O2", 
                      "F7", "F8", "T3", "T4", "T5", "T6", "Fz", "Cz", "Pz"]

    # Load the EDF file
    raw = mne.io.read_raw_edf(filepath, preload=True)

    return raw
