from cerebrus.parser import EdfParser
from mne.io import Raw
from cerebrus.utils.params import CHANNELS_10_20


class TuhParser(EdfParser):
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
        channels_10_20 = {
            channel: channel[4:].replace("-REF", "").strip(" ").capitalize()
            for channel in raw.ch_names
            if "EEG" in channel
        }
        raw.rename_channels(channels_10_20)
        raw.rename_channels({"Ekg1": "ECG"})

        # Set channel types
        channel_types = {channel: "eeg" for channel in CHANNELS_10_20}
        channel_types["ECG"] = "ecg"
        channel_types["A1"] = "misc"
        channel_types["A2"] = "misc"

        raw.set_channel_types(channel_types)

        # Pick only channels specified by the 10-20 system
        raw.pick(picks=CHANNELS_10_20 + ["ECG", "A1", "A2"])
        return raw
