import mne
import numpy as np
from cerebrus.qeeg import (
    calculate_psd,
)


def create_test_raw_data(n_channels=19, n_samples=10000, sfreq=200):
    """
    Create a test Raw object with simulated data.
    """
    data = np.random.randn(n_channels, n_samples)
    info = mne.create_info(n_channels, sfreq, ch_types="eeg")
    raw = mne.io.RawArray(data, info)
    return raw


def test_calculate_psd():
    # Create a test Raw object
    raw = create_test_raw_data()

    # Run the calculate_psd function
    psd_dict, psd, freqs = calculate_psd(raw)

    # Check if the outputs are in the expected format
    assert isinstance(psd_dict, dict), "PSD dictionary should be of type dict"
    assert psd.shape == (19, len(freqs)), "PSD array shape is incorrect"
    assert len(freqs) > 0, "Frequency array should have elements"
    # assert all(
    #     f <= 0 or f >= 100 for f in freqs
    # ), "Frequency values should not be between 0 and 100 Hz"

    # Additional checks can be added to validate the contents of the PSD data,
    # such as checking if the frequency values are within the expected range,
    # and if the PSD values are non-negative, etc.


# Add more tests as needed for different scenarios or edge cases
