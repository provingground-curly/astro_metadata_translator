# This file is part of astro_metadata_translator.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the LICENSE file at the top-level directory of this distribution
# for details of code ownership.
#
# Use of this source code is governed by a 3-clause BSD-style
# license that can be found in the LICENSE file.

import unittest

from astro_metadata_translator import merge_headers


class HeadersTestCase(unittest.TestCase):

    def setUp(self):
        # Define reference headers
        self.h1 = dict(
            ORIGIN="LSST",
            KEY0=0,
            KEY1=1,
            KEY2=3,
            KEY3=3.1415,
            KEY4="a",
        )

        self.h2 = dict(
            ORIGIN="LSST",
            KEY0="0",
            KEY2=4,
            KEY5=42
        )
        self.h3 = dict(
            ORIGIN="AUXTEL",
            KEY3=3.1415,
            KEY2=50,
            KEY5=42,
        )
        self.h4 = dict(
            KEY6="New",
            KEY1="Exists",
        )

        # Add keys for sorting by time
        # Sorted order: h2, h1, h4, h3
        self.h1["MJD-OBS"] = 50000.0
        self.h2["MJD-OBS"] = 49000.0
        self.h3["MJD-OBS"] = 53000.0
        self.h4["MJD-OBS"] = 52000.0

    def test_fail(self):
        with self.assertRaises(ValueError):
            merge_headers([self.h1, self.h2], mode="wrong")

        with self.assertRaises(ValueError):
            merge_headers([])

    def test_one(self):
        merged = merge_headers([self.h1], mode="drop")
        self.assertEqual(merged, self.h1)

    def test_merging_overwrite(self):
        merged = merge_headers([self.h1, self.h2], mode="overwrite")

        expected = {
            "MJD-OBS": self.h2["MJD-OBS"],
            "ORIGIN": self.h2["ORIGIN"],
            "KEY0": self.h2["KEY0"],
            "KEY1": self.h1["KEY1"],
            "KEY2": self.h2["KEY2"],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
        }
        self.assertEqual(merged, expected)

        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="overwrite")

        expected = {
            "MJD-OBS": self.h4["MJD-OBS"],
            "ORIGIN": self.h3["ORIGIN"],
            "KEY0": self.h2["KEY0"],
            "KEY1": self.h4["KEY1"],
            "KEY2": self.h3["KEY2"],
            "KEY3": self.h3["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h3["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

    def test_merging_first(self):
        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="first")

        expected = {
            "MJD-OBS": self.h1["MJD-OBS"],
            "ORIGIN": self.h1["ORIGIN"],
            "KEY0": self.h1["KEY0"],
            "KEY1": self.h1["KEY1"],
            "KEY2": self.h1["KEY2"],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

    def test_merging_drop(self):
        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="drop")

        expected = {
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

        # Sorting the headers should make no difference to drop mode
        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="drop", sort=True)
        self.assertEqual(merged, expected)

        # Now retain some headers
        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="drop", sort=False, first=["ORIGIN"], last=["KEY2", "KEY1"])

        expected = {
            "KEY2": self.h3["KEY2"],
            "ORIGIN": self.h1["ORIGIN"],
            "KEY1": self.h4["KEY1"],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
            "KEY6": self.h4["KEY6"],
        }
        self.assertEqual(merged, expected)

        # Now retain some headers with sorting
        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="drop", sort=True, first=["ORIGIN"], last=["KEY2", "KEY1"])

        expected = {
            "KEY2": self.h3["KEY2"],
            "ORIGIN": self.h2["ORIGIN"],
            "KEY1": self.h4["KEY1"],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
            "KEY6": self.h4["KEY6"],
        }
        self.assertEqual(merged, expected)

    def test_merging_append(self):
        # Try with two headers first
        merged = merge_headers([self.h1, self.h2], mode="append")

        expected = {
            "MJD-OBS": [self.h1["MJD-OBS"], self.h2["MJD-OBS"]],
            "ORIGIN": self.h1["ORIGIN"],
            "KEY0": [self.h1["KEY0"], self.h2["KEY0"]],
            "KEY1": self.h1["KEY1"],
            "KEY2": [self.h1["KEY2"], self.h2["KEY2"]],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
        }

        self.assertEqual(merged, expected)

        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="append")

        expected = {
            "MJD-OBS": [self.h1["MJD-OBS"], self.h2["MJD-OBS"], self.h3["MJD-OBS"], self.h4["MJD-OBS"]],
            "ORIGIN": [self.h1["ORIGIN"], self.h2["ORIGIN"], self.h3["ORIGIN"], None],
            "KEY0": [self.h1["KEY0"], self.h2["KEY0"], None, None],
            "KEY1": [self.h1["KEY1"], None, None, self.h4["KEY1"]],
            "KEY2": [self.h1["KEY2"], self.h2["KEY2"], self.h3["KEY2"], None],
            "KEY3": self.h3["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h3["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

    def test_merging_overwrite_sort(self):
        merged = merge_headers([self.h1, self.h2], mode="overwrite", sort=True)

        expected = {
            "MJD-OBS": self.h1["MJD-OBS"],
            "ORIGIN": self.h1["ORIGIN"],
            "KEY0": self.h1["KEY0"],
            "KEY1": self.h1["KEY1"],
            "KEY2": self.h1["KEY2"],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
        }
        self.assertEqual(merged, expected)

        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="overwrite", sort=True)

        expected = {
            "MJD-OBS": self.h3["MJD-OBS"],
            "ORIGIN": self.h3["ORIGIN"],
            "KEY0": self.h1["KEY0"],
            "KEY1": self.h4["KEY1"],
            "KEY2": self.h3["KEY2"],
            "KEY3": self.h3["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h3["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

        # Changing the order should not change the result
        merged = merge_headers([self.h4, self.h1, self.h3, self.h2],
                               mode="overwrite", sort=True)

        self.assertEqual(merged, expected)

    def test_merging_first_sort(self):
        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="first", sort=True)

        expected = {
            "MJD-OBS": self.h2["MJD-OBS"],
            "ORIGIN": self.h2["ORIGIN"],
            "KEY0": self.h2["KEY0"],
            "KEY1": self.h1["KEY1"],
            "KEY2": self.h2["KEY2"],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

    def test_merging_append_sort(self):
        # Try with two headers first
        merged = merge_headers([self.h1, self.h2], mode="append", sort=True)

        expected = {
            "MJD-OBS": [self.h2["MJD-OBS"], self.h1["MJD-OBS"]],
            "ORIGIN": self.h1["ORIGIN"],
            "KEY0": [self.h2["KEY0"], self.h1["KEY0"]],
            "KEY1": self.h1["KEY1"],
            "KEY2": [self.h2["KEY2"], self.h1["KEY2"]],
            "KEY3": self.h1["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h2["KEY5"],
        }

        self.assertEqual(merged, expected)

        merged = merge_headers([self.h1, self.h2, self.h3, self.h4],
                               mode="append", sort=True)

        expected = {
            "MJD-OBS": [self.h2["MJD-OBS"], self.h1["MJD-OBS"], self.h4["MJD-OBS"], self.h3["MJD-OBS"]],
            "ORIGIN": [self.h2["ORIGIN"], self.h1["ORIGIN"], None, self.h3["ORIGIN"]],
            "KEY0": [self.h2["KEY0"], self.h1["KEY0"], None, None],
            "KEY1": [None, self.h1["KEY1"], self.h4["KEY1"], None],
            "KEY2": [self.h2["KEY2"], self.h1["KEY2"], None, self.h3["KEY2"]],
            "KEY3": self.h3["KEY3"],
            "KEY4": self.h1["KEY4"],
            "KEY5": self.h3["KEY5"],
            "KEY6": self.h4["KEY6"],
        }

        self.assertEqual(merged, expected)

        # Order should not matter
        merged = merge_headers([self.h4, self.h3, self.h2, self.h1],
                               mode="append", sort=True)
        self.assertEqual(merged, expected)


if __name__ == "__main__":
    unittest.main()
