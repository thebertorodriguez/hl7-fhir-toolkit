# HL7 to FHIR Converter Toolkit

A Python toolkit for converting HL7 v2 ADT (Admission, Discharge, Transfer) messages to FHIR R4 Patient resources. This project is designed as a learning resource for healthcare interoperability.

## Features

- **HL7 v2 Parser**: Parse ADT messages and extract patient demographics
- **FHIR R4 Builder**: Build compliant FHIR Patient resources
- **Type Safety**: Full type hints for better IDE support and code quality
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Easy to Use**: Simple API with convenience functions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/thebertorodriguez/hl7-fhir-toolkit.git
cd hl7-fhir-toolkit
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Conversion

```python
from src.converter import convert_hl7_to_fhir_json

# Read an HL7 message
with open('examples/sample_hl7.txt', 'r') as f:
    hl7_message = f.read()

# Convert to FHIR JSON
fhir_json = convert_hl7_to_fhir_json(hl7_message)
print(fhir_json)
```

### Using the Converter Class

```python
from src.converter import HL7ToFHIRConverter

converter = HL7ToFHIRConverter()

# Convert to FHIR Patient resource
patient = converter.convert(hl7_message)

# Convert to JSON
fhir_json = converter.convert_to_json(hl7_message)

# Convert to dictionary
fhir_dict = converter.convert_to_dict(hl7_message)

# Get message header info
message_info = converter.get_message_info()
```

### Parsing HL7 Messages Directly

```python
from src.hl7_parser import HL7Parser

parser = HL7Parser(hl7_message)

# Parse patient demographics
patient_data = parser.parse_patient_demographics()

# Parse message header
header_info = parser.parse_message_header()
```

### Building FHIR Resources Directly

```python
from src.fhir_builder import FHIRBuilder

patient_data = {
    "identifier": {"value": "123456789", "system": "MRN"},
    "name": {"family": "DOE", "given": "JOHN"},
    "birth_date": "1980-05-15",
    "gender": "male"
}

builder = FHIRBuilder()
patient = builder.build_patient(patient_data)
```

## Project Structure

```
hl7-fhir-toolkit/
├── src/
│   ├── __init__.py
│   ├── hl7_parser.py      # HL7 v2 message parser
│   ├── fhir_builder.py    # FHIR R4 Patient resource builder
│   └── converter.py       # Main conversion logic
├── examples/
│   └── sample_hl7.txt     # Sample HL7 ADT message
├── tests/
│   └── test_converter.py  # Unit tests
├── requirements.txt       # Project dependencies
├── .gitignore
└── README.md
```

## Dependencies

- **python-hl7**: HL7 v2 message parsing
- **fhir.resources**: FHIR R4 resource models
- **fastapi**: Web framework (for future API endpoints)
- **pytest**: Testing framework
- **uvicorn**: ASGI server (for FastAPI)

## Running Tests

```bash
pytest tests/
```

## Sample HL7 Message

The `examples/sample_hl7.txt` file contains a sample HL7 v2.5 ADT^A01 message with patient demographics including:
- Patient identification (MRN)
- Name (family, given, middle)
- Date of birth
- Gender
- Address
- Phone numbers

## Error Handling

The toolkit provides custom exceptions for different error scenarios:

- `HL7ParserError`: Raised when HL7 message parsing fails
- `FHIRBuilderError`: Raised when FHIR resource building fails
- `ConverterError`: Raised when conversion process fails

```python
from src.converter import HL7ToFHIRConverter, ConverterError

try:
    converter = HL7ToFHIRConverter()
    patient = converter.convert(hl7_message)
except ConverterError as e:
    print(f"Conversion failed: {e}")
```

## FHIR Mapping

The converter maps HL7 v2 segments to FHIR R4 Patient resource fields:

| HL7 Segment | HL7 Field | FHIR Field | Notes |
|-------------|-----------|------------|-------|
| PID-3 | Patient Identifier | identifier | MRN |
| PID-5 | Patient Name | name | family, given |
| PID-7 | Date of Birth | birthDate | Formatted as YYYY-MM-DD |
| PID-8 | Gender | gender | Mapped to FHIR codes |
| PID-11 | Address | address | line, city, state, postalCode, country |
| PID-13 | Home Phone | telecom | system="phone", use="home" |
| PID-14 | Work Phone | telecom | system="phone", use="work" |

## Future Enhancements

- REST API endpoint using FastAPI
- Support for additional HL7 segments (PV1, NK1, etc.)
- Support for other message types (ADT^A03, ADT^A08, etc.)
- Validation against FHIR profiles
- Batch conversion support
- Extended FHIR resource support (Encounter, Observation, etc.)

## License

This is a learning project for healthcare interoperability concepts.

## Contributing

This is a learning project. Feel free to fork and experiment!

## Resources

- [HL7 v2.5 Specification](http://www.hl7.org/implement/standards/product_brief.cfm?product_id=144)
- [FHIR R4 Specification](https://www.hl7.org/fhir/R4/)
- [FHIR Patient Resource](https://www.hl7.org/fhir/R4/patient.html)
