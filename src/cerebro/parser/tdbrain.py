from mne.io import Raw
from . import BrainvisionParser
from ..utils.params import (
    CHANNELS_10_20,
    TDBRAIN_CHANNEL_MAPPING,
)


class TdbrainParser(BrainvisionParser):
    def read_eeg(self, filepath: str) -> Raw:
        """
        Reads an Brainvision file and extracts channels according to the 10-20 system.
        """
        return super().read_eeg(filepath)

    def reconfigure_eeg_channels(self, raw: Raw) -> Raw:
        """
        Custom configuration for EEG channels specific to TDBrain dataset.
        """

        # Rename channels as per 10-20 system
        raw.rename_channels(TDBRAIN_CHANNEL_MAPPING)

        # Pick only channels specified by the 10-20 system
        raw.pick(picks=CHANNELS_10_20)

        return raw
