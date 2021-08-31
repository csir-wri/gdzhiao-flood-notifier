"""Flood alert model."""

import collections
from .alertprocessor import AlertProcessor
from .recipient import Recipient

Version = collections.namedtuple(
    "Version", ["major", "minor", "revision", "releaselevel"])

__version__ = Version(1, 0, 0, "a")
__author__ = "Franz Alex Gaisie-Essilfie"
