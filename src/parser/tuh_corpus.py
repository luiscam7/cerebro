import re
import logging
from . import EdfParser
from mne.io import Raw
from ..utils.params import CHANNELS_10_20

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


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

        # Set channel types
        channel_types = {channel: "eeg" for channel in CHANNELS_10_20}

        # Check for ecg channel
        ecg_pattern = re.compile(r"e[ck]g", re.IGNORECASE)

        # Check each channel name
        for ch_name in raw.ch_names:
            if ecg_pattern.search(ch_name):
                # If found, rename the channel to 'ECG' and set its type
                raw.rename_channels({ch_name: "ECG"})
                raw.set_channel_types({"ECG": "ecg"})
                break
            else:
                logging.info("No ECG channel present in the recording.")

        # Check if reference clips are present in the channels.
        if {"A1", "A2"}.issubset(set(raw.ch_names)):
            channel_types["A1"] = "misc"
            channel_types["A2"] = "misc"
        else:
            logging.info("No reference channels designated A1 or A2.")

        raw.set_channel_types(channel_types)

        # Pick only channels specified by the 10-20 system
        raw.pick(picks=CHANNELS_10_20 + ["ECG", "A1", "A2"])
        return raw
