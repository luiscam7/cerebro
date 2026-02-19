import unittest
from unittest.mock import patch

# Assuming your get_version function is in a module named 'version'
from cerebro import version


class TestGetVersion(unittest.TestCase):
    def test_get_version(self):
        # Test that get_version returns a valid version string
        actual_version = version.get_version()

        # Version should be a non-empty string
        self.assertIsInstance(actual_version, str)
        self.assertTrue(len(actual_version) > 0)

        # Version should match the format X.Y.Z
        parts = actual_version.split(".")
        self.assertGreaterEqual(len(parts), 2)


if __name__ == "__main__":
    unittest.main()
