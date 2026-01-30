"""
HL7 v2 to FHIR R4 Converter

This module provides the main conversion logic to transform HL7 v2 ADT messages
into FHIR R4 Patient resources.
"""

from typing import Dict, Any, Optional
from fhir.resources.patient import Patient

from .hl7_parser import HL7Parser, HL7ParserError
from .fhir_builder import FHIRBuilder, FHIRBuilderError


class ConverterError(Exception):
    """Custom exception for conversion errors."""
    pass


class HL7ToFHIRConverter:
    """Converter for transforming HL7 v2 ADT messages to FHIR R4 Patient resources."""
    
    def __init__(self):
        """Initialize the converter."""
        self.parser: Optional[HL7Parser] = None
        self.builder = FHIRBuilder()
    
    def convert(self, hl7_message: str) -> Patient:
        """
        Convert an HL7 v2 ADT message to a FHIR R4 Patient resource.
        
        Args:
            hl7_message: Raw HL7 v2 message string
            
        Returns:
            FHIR R4 Patient resource
            
        Raises:
            ConverterError: If conversion fails
        """
        try:
            # Parse HL7 message
            self.parser = HL7Parser(hl7_message)
            
            # Extract patient demographics
            patient_data = self.parser.parse_patient_demographics()
            
            # Build FHIR Patient resource
            patient = self.builder.build_patient(patient_data)
            
            return patient
            
        except HL7ParserError as e:
            raise ConverterError(f"HL7 parsing error: {str(e)}")
        except FHIRBuilderError as e:
            raise ConverterError(f"FHIR building error: {str(e)}")
        except Exception as e:
            raise ConverterError(f"Unexpected conversion error: {str(e)}")
    
    def convert_to_json(self, hl7_message: str) -> str:
        """
        Convert an HL7 v2 ADT message to a FHIR R4 Patient resource JSON string.
        
        Args:
            hl7_message: Raw HL7 v2 message string
            
        Returns:
            JSON string representation of the FHIR R4 Patient resource
            
        Raises:
            ConverterError: If conversion fails
        """
        patient = self.convert(hl7_message)
        return self.builder.patient_to_json(patient)
    
    def convert_to_dict(self, hl7_message: str) -> Dict[str, Any]:
        """
        Convert an HL7 v2 ADT message to a FHIR R4 Patient resource dictionary.
        
        Args:
            hl7_message: Raw HL7 v2 message string
            
        Returns:
            Dictionary representation of the FHIR R4 Patient resource
            
        Raises:
            ConverterError: If conversion fails
        """
        patient = self.convert(hl7_message)
        return self.builder.patient_to_dict(patient)
    
    def get_message_info(self) -> Optional[Dict[str, Any]]:
        """
        Get message header information from the last parsed message.
        
        Returns:
            Dictionary containing message header information, or None if no message parsed
        """
        if self.parser:
            try:
                return self.parser.parse_message_header()
            except HL7ParserError:
                return None
        return None


def convert_hl7_to_fhir(hl7_message: str) -> Patient:
    """
    Convenience function to convert an HL7 v2 ADT message to a FHIR R4 Patient resource.
    
    Args:
        hl7_message: Raw HL7 v2 message string
        
    Returns:
        FHIR R4 Patient resource
        
    Raises:
        ConverterError: If conversion fails
    """
    converter = HL7ToFHIRConverter()
    return converter.convert(hl7_message)


def convert_hl7_to_fhir_json(hl7_message: str) -> str:
    """
    Convenience function to convert an HL7 v2 ADT message to a FHIR R4 Patient resource JSON.
    
    Args:
        hl7_message: Raw HL7 v2 message string
        
    Returns:
        JSON string representation of the FHIR R4 Patient resource
        
    Raises:
        ConverterError: If conversion fails
    """
    converter = HL7ToFHIRConverter()
    return converter.convert_to_json(hl7_message)
