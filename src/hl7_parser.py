"""
HL7 v2 ADT Message Parser

This module provides functionality to parse HL7 v2 ADT (Admission, Discharge, Transfer) messages
and extract patient demographic and administrative data.
"""

from typing import Dict, Optional, Any
import hl7


class HL7ParserError(Exception):
    """Custom exception for HL7 parsing errors."""
    pass


class HL7Parser:
    """Parser for HL7 v2 ADT messages."""
    
    def __init__(self, message: str):
        """
        Initialize the HL7 parser with a message.
        
        Args:
            message: Raw HL7 v2 message string
            
        Raises:
            HL7ParserError: If the message cannot be parsed
        """
        try:
            self.message = hl7.parse(message)
        except Exception as e:
            raise HL7ParserError(f"Failed to parse HL7 message: {str(e)}")
    
    def get_segment(self, segment_id: str) -> Optional[Any]:
        """
        Get a specific segment from the HL7 message.
        
        Args:
            segment_id: The segment identifier (e.g., 'PID', 'MSH')
            
        Returns:
            The segment if found, None otherwise
        """
        try:
            segments = [seg for seg in self.message if str(seg[0]) == segment_id]
            return segments[0] if segments else None
        except Exception:
            return None
    
    def parse_patient_demographics(self) -> Dict[str, Any]:
        """
        Parse patient demographics from PID segment.
        
        Returns:
            Dictionary containing patient demographic information
            
        Raises:
            HL7ParserError: If PID segment is missing or invalid
        """
        pid = self.get_segment('PID')
        if not pid:
            raise HL7ParserError("PID segment not found in message")
        
        try:
            # Parse patient name (PID.5)
            name = pid[5][0] if len(pid) > 5 and pid[5] else None
            family_name = str(name[0]) if name and len(name) > 0 else ""
            given_name = str(name[1]) if name and len(name) > 1 else ""
            middle_name = str(name[2]) if name and len(name) > 2 else ""
            
            # Parse patient identifier (PID.3)
            identifier = pid[3][0] if len(pid) > 3 and pid[3] else None
            patient_id = str(identifier[0]) if identifier and len(identifier) > 0 else ""
            id_system = str(identifier[3]) if identifier and len(identifier) > 3 else "MRN"
            
            # Parse birth date (PID.7)
            birth_date = str(pid[7]) if len(pid) > 7 and pid[7] else ""
            if birth_date and len(birth_date) >= 8:
                # Format YYYYMMDD to YYYY-MM-DD
                birth_date = f"{birth_date[:4]}-{birth_date[4:6]}-{birth_date[6:8]}"
            
            # Parse gender (PID.8)
            gender = str(pid[8]) if len(pid) > 8 and pid[8] else ""
            
            # Parse address (PID.11)
            address = pid[11][0] if len(pid) > 11 and pid[11] else None
            street = str(address[0]) if address and len(address) > 0 else ""
            city = str(address[2]) if address and len(address) > 2 else ""
            state = str(address[3]) if address and len(address) > 3 else ""
            postal_code = str(address[4]) if address and len(address) > 4 else ""
            country = str(address[5]) if address and len(address) > 5 else ""
            
            # Parse phone numbers (PID.13 - home, PID.14 - work)
            home_phone = str(pid[13][0]) if len(pid) > 13 and pid[13] else ""
            work_phone = str(pid[14][0]) if len(pid) > 14 and pid[14] else ""
            
            return {
                "identifier": {
                    "value": patient_id,
                    "system": id_system
                },
                "name": {
                    "family": family_name,
                    "given": given_name,
                    "middle": middle_name
                },
                "birth_date": birth_date,
                "gender": self._map_gender(gender),
                "address": {
                    "line": street,
                    "city": city,
                    "state": state,
                    "postal_code": postal_code,
                    "country": country
                },
                "telecom": {
                    "home": home_phone,
                    "work": work_phone
                }
            }
        except Exception as e:
            raise HL7ParserError(f"Error parsing patient demographics: {str(e)}")
    
    def parse_message_header(self) -> Dict[str, Any]:
        """
        Parse message header information from MSH segment.
        
        Returns:
            Dictionary containing message header information
            
        Raises:
            HL7ParserError: If MSH segment is missing
        """
        msh = self.get_segment('MSH')
        if not msh:
            raise HL7ParserError("MSH segment not found in message")
        
        try:
            return {
                "sending_application": str(msh[3]) if len(msh) > 3 else "",
                "sending_facility": str(msh[4]) if len(msh) > 4 else "",
                "receiving_application": str(msh[5]) if len(msh) > 5 else "",
                "receiving_facility": str(msh[6]) if len(msh) > 6 else "",
                "message_datetime": str(msh[7]) if len(msh) > 7 else "",
                "message_type": str(msh[9]) if len(msh) > 9 else "",
                "message_control_id": str(msh[10]) if len(msh) > 10 else "",
                "version": str(msh[12]) if len(msh) > 12 else ""
            }
        except Exception as e:
            raise HL7ParserError(f"Error parsing message header: {str(e)}")
    
    def _map_gender(self, hl7_gender: str) -> str:
        """
        Map HL7 gender code to FHIR gender code.
        
        Args:
            hl7_gender: HL7 gender code (M, F, O, U)
            
        Returns:
            FHIR gender code (male, female, other, unknown)
        """
        gender_map = {
            'M': 'male',
            'F': 'female',
            'O': 'other',
            'U': 'unknown',
            'A': 'other',  # Ambiguous
            'N': 'unknown'  # Not applicable
        }
        return gender_map.get(hl7_gender.upper(), 'unknown')
