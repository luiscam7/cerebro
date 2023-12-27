import unittest
from unittest.mock import MagicMock
from mne.io import Raw
from cerebro.base.parser import Parser


class MockParser(Parser):
    def read_eeg(self, filepath: str) -> Raw:
        return MagicMock(spec=Raw)  # Mock Raw object

    def load_eeg(self, raw: Raw) -> Raw:
        return raw  # Simple pass-through for testing

    def reconfigure_eeg_channels(self, raw: Raw) -> Raw:
        return raw  # Simple pass-through for testing


class ParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = MockParser()
        self.mock_raw = MagicMock(spec=Raw)

    def test_read_eeg(self):
        # Test read_eeg method
        result = self.parser.read_eeg("dummy_filepath")
        self.assertIsInstance(result, Raw)

    def test_load_eeg(self):
        # Test load_eeg method
        result = self.parser.load_eeg(self.mock_raw)
        self.assertEqual(result, self.mock_raw)

    def test_reconfigure_eeg_channels(self):
        # Test reconfigure_eeg_channels method
        result = self.parser.reconfigure_eeg_channels(self.mock_raw)
        self.assertEqual(result, self.mock_raw)


if __name__ == "__main__":
    unittest.main()
