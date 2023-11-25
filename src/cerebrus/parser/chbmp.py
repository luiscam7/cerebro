from cerebrus.parser.edf import EdfParser
from mne.io import Raw
from cerebrus.utils.params import (
    CHANNELS_10_20,
    CONVERT_TO_10_20,
)


class CHBMP(EdfParser):
    def read_eeg(self, filepath: str) -> Raw:
        """
        Reads an EDF file and extracts channels according to the 10-20 system.
        """
        return super().read_eeg(filepath)

    def reconfigure_eeg_channels(self, raw: Raw) -> Raw:
        """
        Custom configuration for EEG channels specific to CHBMP.
        """
        # Rename channels by removing "-REF" and extra spaces
        channels_10_10 = {
            channel: channel.replace("-REF", "").strip(" ") for channel in raw.ch_names
        }
        raw.rename_channels(channels_10_10)

        # Rename channels as per 10-20 system
        raw.rename_channels(CONVERT_TO_10_20)

        # Pick only channels specified by the 10-20 system
        raw.pick(picks=CHANNELS_10_20)

        return raw
