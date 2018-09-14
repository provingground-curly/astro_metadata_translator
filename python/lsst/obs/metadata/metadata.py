# This file is part of obs_metadata.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (http://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Classes and support code for metadata translation"""

from abc import abstractmethod
import logging

log = logging.getLogger(__name__)


class MetadataMeta(type):
    """Register all subclasses with the base class"""

    @staticmethod
    def _makeConstMapping(standardKey, constant):
        def translator(header):
            return constant
        translator.__doc__ = f"""Returns constant value for '{standardKey}' property

        Parameters
        ----------
        header : `dict`-like
            Header values representing a FITS header.

        Returns
        -------
        translation : `str` or `numbers.Number`
            Always returns {constant}.
        """
        return translator

    @staticmethod
    def _makeUnitMapping(standardKey, fitsKey):
        def translator(header):
            return header[fitsKey]
        translator.__doc__ = f"""Map '{fitsKey}' FITS keyword to '{standardKey}' property

        Parameters
        ----------
        header : `dict`-like
            Header values representing a FITS header.

        Returns
        -------
        translation : `str` or `numbers.Number`
            Translated header value derived directly from the {fitsKey}
            header value.
        """
        return translator

    def __init__(self, name, bases, dct):
        super().__init__(name, bases, dct)

        if hasattr(self, "name") and self.name is not None:
            MetadataTranslator.translators[self.name] = self

        for standardKey, fitsKey in self._unitMap.items():
            translator = self._makeUnitMapping(standardKey, fitsKey)
            setattr(self, f"to{standardKey.capitalize()}", staticmethod(translator))

        for standardKey, constant in self._constMap.items():
            translator = self._makeConstMapping(standardKey, constant)
            setattr(self, f"to{standardKey.capitalize()}", staticmethod(translator))


class MetadataTranslator(metaclass=MetadataMeta):
    """Per-instrument metadata translation support"""

    _unitMap = {}
    """Dict of one-to-one mappings for header translation from standard
    property to corresponding FITS keyword."""

    _constMap = {}
    """Dict defining a constant for specified standard properties."""

    translators = dict()
    """All registered metadata translation classes."""

    supportedInstrument = None
    """Name of instrument understood by this translation class."""

    @classmethod
    @abstractmethod
    def canTranslate(cls, header):
        """Indicate whether this translation class can translate the
        supplied header.

        Parameters
        ----------
        header : `dict`-like
           Header to convert to standardized form.

        Returns
        -------
        can : `bool`
            `True` if the header is recognized by this class. `False`
            otherwise.
        """
        raise NotImplementedError()


class VisitInfo:
    """Standardized representation of an instrument FITS header.

    Parameters
    ----------
    header : `dict`-like
        Representation of an instrument FITS header accessible as a `dict`.
    translator : `MetadataTranslator`-class, `optional`
        If not `None`, the class to use to translate the supplied headers
        into standard form. Otherwise each registered translator class will
        be asked in turn if it knows how to translate the supplied header.

    Raises
    ------
    ValueError
        The supplied header was not recognized by any of the registered
        translators.
    """

    def __init__(self, header, translator=None):
        if translator is None:
            for name, trans in MetadataTranslator.translators.items():
                if trans.canTranslate(header):
                    log.debug(f"Using translation class {name}")
                    translator = trans
                    break
            else:
                raise ValueError("None of the registered translation classes understood this header")

        # Loop over each translation (not final form -- this should be
        # defined in one place and consistent with translation classes)
        translations = ("telescope", "instrument", "datetime_begin", "datetime_end")
        for t in translations:
            # prototype code
            method = f"to{t.capitalize()}"
            property = f"_{t}"

            try:
                print(f"Assigning {property} via {method}")
                setattr(self, property, getattr(translator, method)(header))
            except (AttributeError, KeyError):
                # For now assign None
                setattr(self, property, None)

    @property
    def datetime_begin(self):
        return self._datetime_begin

    @property
    def datetime_end(self):
        return self._datetime_end

    @property
    def instrument(self):
        return self._instrument

    @property
    def telescope(self):
        return self._telescope
