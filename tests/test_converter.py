"""
Unit tests for HL7 to FHIR converter
"""

import pytest
from src.hl7_parser import HL7Parser, HL7ParserError
from src.fhir_builder import FHIRBuilder, FHIRBuilderError
from src.converter import HL7ToFHIRConverter, ConverterError, convert_hl7_to_fhir, convert_hl7_to_fhir_json


# Sample HL7 ADT message
SAMPLE_HL7 = """MSH|^~\\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20240115103000||ADT^A01|MSG00001|P|2.5
EVN|A01|20240115103000
PID|1||123456789^^^MRN||DOE^JOHN^ALEXANDER||19800515|M|||123 MAIN ST^^ANYTOWN^CA^12345^USA||(555)123-4567|(555)987-6543||M|NON|12345678|||||||||||||||||||
NK1|1|DOE^JANE^|SPO|123 MAIN ST^^ANYTOWN^CA^12345^USA|(555)123-4567
PV1|1|I|WRD^1^1^HOSPITAL||||12345^SMITH^ROBERT^J^^^DR|||SUR||||ADM|A0|12345678||||||||||||||||||||||||||20240115100000"""


class TestHL7Parser:
    """Test cases for HL7Parser class."""
    
    def test_parse_valid_message(self):
        """Test parsing a valid HL7 message."""
        parser = HL7Parser(SAMPLE_HL7)
        assert parser.message is not None
    
    def test_parse_invalid_message(self):
        """Test parsing an invalid HL7 message raises error."""
        with pytest.raises(HL7ParserError):
            HL7Parser("invalid message")
    
    def test_get_segment(self):
        """Test getting a specific segment."""
        parser = HL7Parser(SAMPLE_HL7)
        pid = parser.get_segment('PID')
        assert pid is not None
        assert str(pid[0]) == 'PID'
    
    def test_get_missing_segment(self):
        """Test getting a non-existent segment returns None."""
        parser = HL7Parser(SAMPLE_HL7)
        segment = parser.get_segment('ZZZ')
        assert segment is None
    
    def test_parse_patient_demographics(self):
        """Test parsing patient demographics."""
        parser = HL7Parser(SAMPLE_HL7)
        patient_data = parser.parse_patient_demographics()
        
        assert patient_data['identifier']['value'] == '123456789'
        assert patient_data['name']['family'] == 'DOE'
        assert patient_data['name']['given'] == 'JOHN'
        assert patient_data['name']['middle'] == 'ALEXANDER'
        assert patient_data['birth_date'] == '1980-05-15'
        assert patient_data['gender'] == 'male'
        assert patient_data['address']['line'] == '123 MAIN ST'
        assert patient_data['address']['city'] == 'ANYTOWN'
        assert patient_data['address']['state'] == 'CA'
        assert patient_data['address']['postal_code'] == '12345'
        assert patient_data['telecom']['home'] == '(555)123-4567'
        assert patient_data['telecom']['work'] == '(555)987-6543'
    
    def test_parse_message_header(self):
        """Test parsing message header."""
        parser = HL7Parser(SAMPLE_HL7)
        header = parser.parse_message_header()
        
        assert header['sending_application'] == 'SENDING_APP'
        assert header['sending_facility'] == 'SENDING_FACILITY'
        assert header['receiving_application'] == 'RECEIVING_APP'
        assert header['receiving_facility'] == 'RECEIVING_FACILITY'
        assert header['message_control_id'] == 'MSG00001'
        assert header['version'] == '2.5'
    
    def test_map_gender_male(self):
        """Test gender mapping for male."""
        parser = HL7Parser(SAMPLE_HL7)
        assert parser._map_gender('M') == 'male'
    
    def test_map_gender_female(self):
        """Test gender mapping for female."""
        parser = HL7Parser(SAMPLE_HL7)
        assert parser._map_gender('F') == 'female'
    
    def test_map_gender_unknown(self):
        """Test gender mapping for unknown."""
        parser = HL7Parser(SAMPLE_HL7)
        assert parser._map_gender('U') == 'unknown'
        assert parser._map_gender('X') == 'unknown'


class TestFHIRBuilder:
    """Test cases for FHIRBuilder class."""
    
    def test_build_patient_basic(self):
        """Test building a basic patient resource."""
        patient_data = {
            "identifier": {"value": "123456789", "system": "MRN"},
            "name": {"family": "DOE", "given": "JOHN", "middle": ""},
            "birth_date": "1980-05-15",
            "gender": "male",
            "address": {},
            "telecom": {}
        }
        
        builder = FHIRBuilder()
        patient = builder.build_patient(patient_data)
        
        assert patient.resourceType == "Patient"
        assert patient.identifier[0].value == "123456789"
        assert patient.name[0].family == "DOE"
        assert patient.name[0].given[0] == "JOHN"
        assert patient.birthDate == "1980-05-15"
        assert patient.gender == "male"
    
    def test_build_patient_full(self):
        """Test building a patient resource with all fields."""
        patient_data = {
            "identifier": {"value": "123456789", "system": "MRN"},
            "name": {"family": "DOE", "given": "JOHN", "middle": "ALEXANDER"},
            "birth_date": "1980-05-15",
            "gender": "male",
            "address": {
                "line": "123 MAIN ST",
                "city": "ANYTOWN",
                "state": "CA",
                "postal_code": "12345",
                "country": "USA"
            },
            "telecom": {
                "home": "(555)123-4567",
                "work": "(555)987-6543"
            }
        }
        
        builder = FHIRBuilder()
        patient = builder.build_patient(patient_data)
        
        assert patient.resourceType == "Patient"
        assert patient.identifier[0].value == "123456789"
        assert patient.name[0].family == "DOE"
        assert len(patient.name[0].given) == 2
        assert patient.name[0].given[0] == "JOHN"
        assert patient.name[0].given[1] == "ALEXANDER"
        assert patient.birthDate == "1980-05-15"
        assert patient.gender == "male"
        assert patient.address[0].line[0] == "123 MAIN ST"
        assert patient.address[0].city == "ANYTOWN"
        assert patient.address[0].state == "CA"
        assert patient.address[0].postalCode == "12345"
        assert len(patient.telecom) == 2
    
    def test_patient_to_json(self):
        """Test converting patient to JSON."""
        patient_data = {
            "identifier": {"value": "123456789", "system": "MRN"},
            "name": {"family": "DOE", "given": "JOHN", "middle": ""},
            "birth_date": "1980-05-15",
            "gender": "male",
            "address": {},
            "telecom": {}
        }
        
        builder = FHIRBuilder()
        patient = builder.build_patient(patient_data)
        json_str = builder.patient_to_json(patient)
        
        assert '"resourceType": "Patient"' in json_str
        assert '"value": "123456789"' in json_str
    
    def test_patient_to_dict(self):
        """Test converting patient to dictionary."""
        patient_data = {
            "identifier": {"value": "123456789", "system": "MRN"},
            "name": {"family": "DOE", "given": "JOHN", "middle": ""},
            "birth_date": "1980-05-15",
            "gender": "male",
            "address": {},
            "telecom": {}
        }
        
        builder = FHIRBuilder()
        patient = builder.build_patient(patient_data)
        patient_dict = builder.patient_to_dict(patient)
        
        assert patient_dict['resourceType'] == 'Patient'
        assert patient_dict['identifier'][0]['value'] == '123456789'


class TestConverter:
    """Test cases for HL7ToFHIRConverter class."""
    
    def test_convert_basic(self):
        """Test basic conversion."""
        converter = HL7ToFHIRConverter()
        patient = converter.convert(SAMPLE_HL7)
        
        assert patient.resourceType == "Patient"
        assert patient.identifier[0].value == "123456789"
        assert patient.name[0].family == "DOE"
        assert patient.gender == "male"
    
    def test_convert_to_json(self):
        """Test conversion to JSON."""
        converter = HL7ToFHIRConverter()
        json_str = converter.convert_to_json(SAMPLE_HL7)
        
        assert '"resourceType": "Patient"' in json_str
        assert '"value": "123456789"' in json_str
    
    def test_convert_to_dict(self):
        """Test conversion to dictionary."""
        converter = HL7ToFHIRConverter()
        patient_dict = converter.convert_to_dict(SAMPLE_HL7)
        
        assert patient_dict['resourceType'] == 'Patient'
        assert patient_dict['identifier'][0]['value'] == '123456789'
    
    def test_get_message_info(self):
        """Test getting message info."""
        converter = HL7ToFHIRConverter()
        converter.convert(SAMPLE_HL7)
        message_info = converter.get_message_info()
        
        assert message_info is not None
        assert message_info['sending_application'] == 'SENDING_APP'
        assert message_info['message_control_id'] == 'MSG00001'
    
    def test_convert_invalid_message(self):
        """Test conversion with invalid message raises error."""
        converter = HL7ToFHIRConverter()
        with pytest.raises(ConverterError):
            converter.convert("invalid message")
    
    def test_convenience_function_convert(self):
        """Test convenience function convert_hl7_to_fhir."""
        patient = convert_hl7_to_fhir(SAMPLE_HL7)
        
        assert patient.resourceType == "Patient"
        assert patient.identifier[0].value == "123456789"
    
    def test_convenience_function_convert_json(self):
        """Test convenience function convert_hl7_to_fhir_json."""
        json_str = convert_hl7_to_fhir_json(SAMPLE_HL7)
        
        assert '"resourceType": "Patient"' in json_str
        assert '"value": "123456789"' in json_str


class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_conversion_pipeline(self):
        """Test the full conversion pipeline."""
        # Parse HL7
        parser = HL7Parser(SAMPLE_HL7)
        patient_data = parser.parse_patient_demographics()
        
        # Build FHIR
        builder = FHIRBuilder()
        patient = builder.build_patient(patient_data)
        
        # Verify result
        assert patient.resourceType == "Patient"
        assert patient.identifier[0].value == "123456789"
        assert patient.name[0].family == "DOE"
        assert patient.name[0].given[0] == "JOHN"
        assert patient.birthDate == "1980-05-15"
        assert patient.gender == "male"
        assert patient.address[0].city == "ANYTOWN"
        
    def test_sample_file_conversion(self):
        """Test conversion using the sample file."""
        import os
        
        sample_file = "/home/runner/work/hl7-fhir-toolkit/hl7-fhir-toolkit/examples/sample_hl7.txt"
        
        if os.path.exists(sample_file):
            with open(sample_file, 'r') as f:
                hl7_message = f.read()
            
            converter = HL7ToFHIRConverter()
            patient = converter.convert(hl7_message)
            
            assert patient.resourceType == "Patient"
            assert patient.identifier[0].value == "123456789"
