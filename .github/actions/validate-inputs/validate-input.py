import sys
import os
import pathlib

# Collects all validation error messages
errors = []

# Parses comma-separated key=value pairs into a dictionary
def parse_kv_string(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            errors.append(f"[ERROR] Invalid key=value pair: '{pair}'")
            continue
        k, v = pair.strip().split('=', 1)
        result[k.strip()] = v.strip()
    return result

# Parses a comma-separated list into a list of non-empty trimmed values
def parse_csv(s):
    return [i.strip() for i in s.split(',') if i.strip()]

# Parses typeValidations in the format type=key1 key2,... into a key-to-type dictionary
def parse_type_validation_grouped(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            errors.append(f"[ERROR] Invalid typeValidations format: '{pair}'")
            continue
        type_name, keys = pair.strip().split('=', 1)
        for key in keys.replace("'", "").replace('"', '').split():
            result[key.strip()] = type_name.strip()
    return result

# Parses rangeValidations in the format key=value1 value2,... into a dictionary
def parse_range_validation(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            errors.append(f"[ERROR] Invalid rangeValidations format: '{pair}'")
            continue
        key, values = pair.strip().split('=', 1)
        result[key.strip()] = values.strip().split()
    return result

def is_number_string(value):
    try:
        float(value)  # Try converting to float to allow integers and decimals
        return True
    except ValueError:
        return False

# === Validation Starts ===
print("\n*** [START] Validation Started ***")

# Load inputs from environment variables
inputs = parse_kv_string(os.environ.get('INPUT_ACTIONINPUTS', ''))
required = parse_csv(os.environ.get('INPUT_REQUIREDINPUTS', ''))
optional = parse_csv(os.environ.get('INPUT_OPTIONALINPUTS', ''))
file_keys = parse_csv(os.environ.get('INPUT_FILESPATHINPUTS', ''))
type_validation = parse_type_validation_grouped(os.environ.get('INPUT_TYPEVALIDATIONS', ''))
range_validation = parse_range_validation(os.environ.get('INPUT_RANGEVALIDATIONS', ''))

# Check that all required inputs exist and are non-empty
for key in required:
    if key not in inputs or inputs[key].strip() == '':
        errors.append(f"[ERROR] Missing or empty required input: '{key}'")

# Check that all specified file path inputs exist in the filesystem
for key in file_keys:
    value = inputs.get(key, '').strip()

    # If required: must exist and not be empty
    if key in required:
        if not value:
            errors.append(f"[ERROR] Required file input '{key}' is empty or missing")
        elif not pathlib.Path(value).exists():
            errors.append(f"[ERROR] Required file not found for key '{key}': {value}")
    else: # Optional: only validate if value is non-empty
        if value and not pathlib.Path(value).exists():
            errors.append(f"[ERROR] Optional file not found for key '{key}': {value}")


# Validate types of inputs based on declared expectations
for key, expected_type in type_validation.items():
    if key not in inputs:
        errors.append(f"[ERROR] Type check failed: '{key}' not found in actionInputs")
        continue
    value = inputs[key]
    if expected_type == 'string':
        continue
    if expected_type == 'booleanString' and value.lower() not in ['true', 'false']:
        errors.append(f"[ERROR] Invalid booleanString for '{key}': '{value}' (expected 'true' or 'false')")
    if expected_type == 'numberString' and not is_number_string(value):
        errors.append(f"[ERROR] Invalid numberString for '{key}': '{value}' (expected any numeric string)")
    if expected_type not in ['string', 'booleanString', 'numberString']:
        errors.append(f"[ERROR] Unknown type '{expected_type}' for key '{key}'")

# Validate value of each input against its allowed range
for key, allowed_values in range_validation.items():
    if key not in inputs:
        errors.append(f"[ERROR] Range validation failed: '{key}' not found in actionInputs")
        continue
    if inputs[key] not in allowed_values:
        errors.append(f"[ERROR] Invalid value for '{key}': '{inputs[key]}'. Allowed values: {allowed_values}")

# Final validation result
if errors:
    print("\n[FAIL] Validation failed with the following issues:")
    for err in errors:
        print(f"  - {err}")
    print("\n*** [END] Validation Ended with Errors ***\n")
    sys.exit(1)
else:
    print("[OK] All validations passed.")
    print("\n*** [END] Validation Ended Successfully ***\n")
