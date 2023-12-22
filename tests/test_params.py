from cerebro.utils.params import (
    CHANNELS_10_20,
    CONVERT_TO_10_20,
    ECG_ARTIFACT_ICA_DETECTION_THRESHOLD,
)


def test_ecg_artifact_ica_detection_threshold():
    assert (
        0 <= ECG_ARTIFACT_ICA_DETECTION_THRESHOLD <= 1
    ), "Threshold should be between 0 and 1"
    assert (
        ECG_ARTIFACT_ICA_DETECTION_THRESHOLD == 0.75
    ), "Expected ECG artifact ICA detection threshold is 0.75"


def test_channels_10_20():
    expected_channels = [
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
    assert (
        CHANNELS_10_20 == expected_channels
    ), "CHANNELS_10_20 does not match the expected 10-20 system channels"


def test_convert_to_10_20():
    expected_conversion = {
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
        "T7": "T3",
        "T8": "T4",
        "P7": "T5",
        "P8": "T6",
        "Fz": "Fz",
        "Cz": "Cz",
        "Pz": "Pz",
    }
    assert (
        CONVERT_TO_10_20 == expected_conversion
    ), "CONVERT_TO_10_20 does not match the expected channel mapping from 10-10 to 10-20 system"
