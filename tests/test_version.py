import unittest
from unittest.mock import mock_open, patch

import toml

# Assuming your get_version function is in a module named 'version'
from cerebro import version


class TestGetVersion(unittest.TestCase):
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data='[tool.poetry]\nversion = "1.2.3"',
    )
    @patch("toml.load")
    def test_get_version(self, mock_toml_load, mock_open):
        # Mock the toml.load to return a specific dictionary structure
        mock_toml_load.return_value = {"tool": {"poetry": {"version": "1.2.3"}}}

        expected_version = "1.2.3"
        actual_version = version.get_version()

        self.assertEqual(actual_version, expected_version)


if __name__ == "__main__":
    unittest.main()
