#!/usr/bin/env python3
"""
Example script demonstrating HL7 to FHIR conversion.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.converter import HL7ToFHIRConverter


def main():
    """Main function to demonstrate conversion."""
    # Read sample HL7 message
    sample_file = os.path.join(os.path.dirname(__file__), 'examples', 'sample_hl7.txt')
    
    with open(sample_file, 'r') as f:
        hl7_message = f.read()
    
    print("=" * 80)
    print("HL7 to FHIR Conversion Example")
    print("=" * 80)
    print("\nInput HL7 Message:")
    print("-" * 80)
    print(hl7_message)
    
    # Convert to FHIR
    converter = HL7ToFHIRConverter()
    
    # Get message info
    converter.convert(hl7_message)
    message_info = converter.get_message_info()
    
    print("\n" + "=" * 80)
    print("Message Information:")
    print("=" * 80)
    for key, value in message_info.items():
        print(f"{key}: {value}")
    
    # Convert to FHIR JSON
    fhir_json = converter.convert_to_json(hl7_message)
    
    print("\n" + "=" * 80)
    print("Output FHIR Patient Resource (JSON):")
    print("=" * 80)
    print(fhir_json)
    
    print("\n" + "=" * 80)
    print("Conversion completed successfully!")
    print("=" * 80)


if __name__ == '__main__':
    main()
