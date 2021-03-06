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

import os.path
import unittest
import astropy.units as u

from astro_metadata_translator.tests import MetadataAssertHelper

TESTDIR = os.path.abspath(os.path.dirname(__file__))


class DecamTestCase(unittest.TestCase, MetadataAssertHelper):
    datadir = os.path.join(TESTDIR, "data")

    def test_decam_translator(self):
        test_data = (("fitsheader-decam.yaml",
                      dict(telescope="CTIO 4.0-m telescope",
                           instrument="DECam",
                           boresight_rotation_coord="unknown",
                           dark_time=201.15662*u.s,
                           detector_exposure_id=22938825,
                           detector_name="S1",
                           detector_num=25,
                           detector_serial="S3-111_107419-8-3",
                           exposure_id=229388,
                           exposure_time=200.0*u.s,
                           object="DES supernova hex SN-S1 tiling 22",
                           observation_id="ct4m20130901t060255",
                           observation_type="science",
                           physical_filter="z DECam SDSS c0004 9260.0 1520.0",
                           pressure=779.0*u.hPa,
                           relative_humidity=23.0,
                           science_program="2012B-0001",
                           temperature=11.9*u.deg_C,
                           visit_id=229388,
                           wcs_params=dict(max_sep=1.5))),
                     ("fitsheader-decam-0160496.yaml",
                      dict(telescope="CTIO 4.0-m telescope",
                           instrument="DECam",
                           boresight_rotation_coord="unknown",
                           dark_time=0.0407898*u.s,
                           detector_exposure_id=None,
                           detector_name="S1",
                           detector_num=25,
                           detector_serial="S3-111_107419-8-3",
                           exposure_id=None,
                           exposure_time=0.0*u.s,
                           object="postflats-BIAS",
                           observation_id="ct4m20121211t220632",
                           observation_type="zero",
                           physical_filter="Y DECam c0005 10095.0 1130.0",
                           pressure=777.0*u.hPa,
                           relative_humidity=38.0,
                           science_program="2012B-0416",
                           temperature=17.0*u.deg_C,
                           visit_id=None,
                           wcs_params=dict(max_sep=1.5))),
                     ("fitsheader-decam-calexp-0412037_10.yaml",
                      dict(telescope="CTIO 4.0-m telescope",
                           instrument="DECam",
                           boresight_rotation_coord="unknown",
                           dark_time=87.1054702*u.s,
                           detector_exposure_id=41203701,
                           detector_name="S29",
                           detector_num=1,
                           detector_serial="S3-06_123195-15-3",
                           exposure_id=412037,
                           exposure_time=86.0*u.s,
                           object="Blind15A_03",
                           observation_id="ct4m20150220t004721",
                           observation_type="science",
                           physical_filter="g",
                           pressure=777.0*u.hPa,
                           relative_humidity=76.0,
                           science_program="2015A-0608",
                           temperature=9.0*u.deg_C,
                           visit_id=412037,
                           wcs_params=dict(max_sep=5.0))),
                     )
        for file, expected in test_data:
            with self.subTest(f"Testing {file}"):
                self.assertObservationInfoFromYaml(file, dir=self.datadir, **expected)


if __name__ == "__main__":
    unittest.main()
