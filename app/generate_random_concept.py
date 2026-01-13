import random
from datetime import datetime, timedelta

def generate_random_raw_concept(concept_name):
    """
    Generates a random RawConcept object based on TAK Schema v24.
    
    Args:
        concept_name (str): The name of the concept.
        
    Returns:
        dict: A dictionary containing the concept name, type, and specific allowed values.
    """
    
    # Defined types from TAK Schema [cite: 41, 538]
    concept_types = [
        "rawOrdinal",
        "rawBoolean",
        "rawNominal",
        "rawNumeric",
        "rawDateTime"
    ]

    # for now the project is able to generate only these types of concepts
    concept_types = [
        "rawOrdinal"
    ]
    
    selected_type = random.choice(concept_types)
    
    result = {
        "concept_name": concept_name,
        "concept_type": selected_type,
        "allowed_values": {}
    }

    # Generate values based on specific class definitions in the PDF
    
    if selected_type == "rawOrdinal":
        # OrdinalRawConcept: Symbolic values with order [cite: 307]
        # Example sets
        options = [
            ["Low", "Medium", "High"],
            ["Trace", "1+", "2+", "3+"],
            ["Stage I", "Stage II", "Stage III", "Stage IV"]
        ]
        values = random.choice(options)
        # Structure matches OrdinalAllowedValues 
        result["allowed_values"] = {
            "values": values,
            "ordering": "asc" # Default is asc [cite: 312]
        }

    elif selected_type == "rawBoolean":
        # BooleanRawConcept: True/False only [cite: 333]
        # Structure matches BooleanAllowedValues [cite: 341]
        result["allowed_values"] = {
            "values": [True, False]
        }

    elif selected_type == "rawNominal":
        # NominalRawConcept: Symbolic values without order 
        # Example sets
        options = [
            ["Male", "Female"],
            ["Type A", "Type B", "Type AB", "Type O"],
            ["Positive", "Negative", "Inconclusive"]
        ]
        # Structure matches NominalAllowedValues 
        result["allowed_values"] = {
            "values": random.choice(options)
        }

    elif selected_type == "rawNumeric":
        # NumericRawConcept: Quantitative interval [cite: 288]
        # Structure matches NumericAllowedValues 
        min_val = random.randint(0, 50)
        max_val = random.randint(100, 500)
        units = random.choice(["mg/dL", "kg", "cm", "cells/mL", "degrees C"])
        
        result["allowed_values"] = {
            "minValue": min_val,
            "maxValue": max_val,
            "units": units,
            "scale": "Ratio" # Default is Ratio [cite: 299]
        }

    elif selected_type == "rawDateTime":
        # DateTimeRawConcept: Date ranges [cite: 346]
        # Structure matches DateTimeAllowedValues 
        result["allowed_values"] = {
            "min": "1900-01-01T00:00:00",
            "max": "2099-12-31T23:59:59"
        }

    return result

# --- Usage Example ---
# Generate 3 random concepts to demonstrate variety
for i in range(3):
    concept = generate_random_raw_concept(f"TestConcept_{i+1}")
    print(f"Generated: {concept}")