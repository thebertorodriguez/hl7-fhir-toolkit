"""
FHIR R4 Patient Resource Builder

This module provides functionality to build FHIR R4 Patient resources
from parsed HL7 v2 data.
"""

from typing import Dict, Any, List, Optional
from fhir.resources.patient import Patient
from fhir.resources.humanname import HumanName
from fhir.resources.address import Address
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.identifier import Identifier


class FHIRBuilderError(Exception):
    """Custom exception for FHIR building errors."""
    pass


class FHIRBuilder:
    """Builder for FHIR R4 Patient resources."""
    
    @staticmethod
    def build_patient(patient_data: Dict[str, Any]) -> Patient:
        """
        Build a FHIR R4 Patient resource from parsed HL7 data.
        
        Args:
            patient_data: Dictionary containing patient demographic information
            
        Returns:
            FHIR R4 Patient resource
            
        Raises:
            FHIRBuilderError: If patient resource cannot be built
        """
        try:
            # Build identifier
            identifiers = []
            if patient_data.get('identifier', {}).get('value'):
                identifier = Identifier(
                    system=f"urn:oid:2.16.840.1.113883.4.1",  # Example OID for MRN
                    value=patient_data['identifier']['value'],
                    type={
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": patient_data['identifier'].get('system', 'MRN'),
                            "display": "Medical Record Number"
                        }]
                    }
                )
                identifiers.append(identifier)
            
            # Build name
            names = []
            name_data = patient_data.get('name', {})
            if name_data.get('family') or name_data.get('given'):
                given_names = []
                if name_data.get('given'):
                    given_names.append(name_data['given'])
                if name_data.get('middle'):
                    given_names.append(name_data['middle'])
                
                name = HumanName(
                    use="official",
                    family=name_data.get('family', ''),
                    given=given_names if given_names else None
                )
                names.append(name)
            
            # Build address
            addresses = []
            address_data = patient_data.get('address', {})
            if any(address_data.values()):
                address_lines = []
                if address_data.get('line'):
                    address_lines.append(address_data['line'])
                
                address = Address(
                    use="home",
                    type="physical",
                    line=address_lines if address_lines else None,
                    city=address_data.get('city') or None,
                    state=address_data.get('state') or None,
                    postalCode=address_data.get('postal_code') or None,
                    country=address_data.get('country') or None
                )
                addresses.append(address)
            
            # Build telecom (phone numbers)
            telecoms = []
            telecom_data = patient_data.get('telecom', {})
            
            if telecom_data.get('home'):
                home_phone = ContactPoint(
                    system="phone",
                    value=telecom_data['home'],
                    use="home"
                )
                telecoms.append(home_phone)
            
            if telecom_data.get('work'):
                work_phone = ContactPoint(
                    system="phone",
                    value=telecom_data['work'],
                    use="work"
                )
                telecoms.append(work_phone)
            
            # Build patient resource
            patient = Patient(
                resourceType="Patient",
                identifier=identifiers if identifiers else None,
                name=names if names else None,
                gender=patient_data.get('gender') or None,
                birthDate=patient_data.get('birth_date') or None,
                address=addresses if addresses else None,
                telecom=telecoms if telecoms else None
            )
            
            return patient
            
        except Exception as e:
            raise FHIRBuilderError(f"Error building FHIR Patient resource: {str(e)}")
    
    @staticmethod
    def patient_to_json(patient: Patient) -> str:
        """
        Convert FHIR Patient resource to JSON string.
        
        Args:
            patient: FHIR R4 Patient resource
            
        Returns:
            JSON string representation of the Patient resource
        """
        return patient.json(indent=2, exclude_none=True)
    
    @staticmethod
    def patient_to_dict(patient: Patient) -> Dict[str, Any]:
        """
        Convert FHIR Patient resource to dictionary.
        
        Args:
            patient: FHIR R4 Patient resource
            
        Returns:
            Dictionary representation of the Patient resource
        """
        return patient.dict(exclude_none=True)
