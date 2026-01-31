"""
HL7 to FHIR Converter Toolkit

A Python toolkit for converting HL7 v2 ADT messages to FHIR R4 Patient resources.
"""

from .converter import (
    HL7ToFHIRConverter,
    ConverterError,
    convert_hl7_to_fhir,
    convert_hl7_to_fhir_json
)
from .hl7_parser import HL7Parser, HL7ParserError
from .fhir_builder import FHIRBuilder, FHIRBuilderError

__all__ = [
    'HL7ToFHIRConverter',
    'ConverterError',
    'convert_hl7_to_fhir',
    'convert_hl7_to_fhir_json',
    'HL7Parser',
    'HL7ParserError',
    'FHIRBuilder',
    'FHIRBuilderError'
]

__version__ = '0.1.0'
