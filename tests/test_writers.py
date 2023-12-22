import json
import os
import unittest

import numpy as np

from cerebro.utils.writers import dict_to_json


class TestWriters(unittest.TestCase):
    def setUp(self):
        self.test_data = {"a": 1, "b": [1, 2, 3], "c": np.array([1, 2, 3])}
        self.json_filename = "test.json"

    def tearDown(self):
        if os.path.exists(self.json_filename):
            os.remove(self.json_filename)

    def test_dict_to_json(self):
        dict_to_json(self.test_data, self.json_filename)
        self.assertTrue(os.path.exists(self.json_filename))

        with open(self.json_filename, "r") as f:
            data = json.load(f)
        self.assertEqual(data, self.test_data)


if __name__ == "__main__":
    unittest.main()
