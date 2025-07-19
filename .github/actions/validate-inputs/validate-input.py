import sys
import os
import pathlib

# Error collector
errors = []

def parse_kv_string(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            errors.append(f"? Invalid key=value pair: '{pair}'")
            continue
        k, v = pair.strip().split('=', 1)
        result[k.strip()] = v.strip()
    return result

def parse_csv(s):
    return [i.strip() for i in s.split(',') if i.strip()]

def parse_type_validation_grouped(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            errors.append(f"? Invalid typeValidations format: '{pair}'")
            continue
        type_name, keys = pair.strip().split('=', 1)
        for key in keys.strip().replace("'", "").replace('"', '').split():
            result[key.strip()] = type_name.strip()
    return result

def parse_range_validation(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            errors.append(f"? Invalid rangeValidations format: '{pair}'")
            continue
        key, values = pair.strip().split('=', 1)
        result[key.strip()] = values.strip().split()
    return result

# === Start ===
print("\n*** ?? Validation Started ***")

# Read inputs from environment
inputs = parse_kv_string(os.environ.get('INPUT_ACTIONINPUTS', ''))
required = parse_csv(os.environ.get('INPUT_REQUIREDINPUTS', ''))
optional = parse_csv(os.environ.get('INPUT_OPTIONALINPUTS', ''))
file_keys = parse_csv(os.environ.get('INPUT_FILESPATHINPUTS', ''))
type_validation = parse_type_validation_grouped(os.environ.get('INPUT_TYPEVALIDATIONS', ''))
range_validation = parse_range_validation(os.environ.get('INPUT_RANGEVALIDATIONS', ''))

# Validate required keys
for key in required:
    if key not in inputs or inputs[key] == '':
        errors.append(f"? Missing or empty required input: '{key}'")

# Validate file path existence
for key in file_keys:
    if key not in inputs:
        errors.append(f"? File validation failed: '{key}' not found in actionInputs")
    else:
        file_path = inputs[key]
        if not pathlib.Path(file_path).exists():
            errors.append(f"? File not found for key '{key}': {file_path}")

# Type validation
for key, expected_type in type_validation.items():
    if key not in inputs:
        errors.append(f"? Type check failed: '{key}' not found in actionInputs")
        continue
    value = inputs[key]
    if expected_type == 'string':
        pass
    elif expected_type == 'booleanString':
        if value.lower() not in ['true', 'false']:
            errors.append(f"? Invalid booleanString for '{key}': '{value}' (expected 'true' or 'false')")
    elif expected_type == 'booleanNumber':
        if value not in ['0', '1']:
            errors.append(f"? Invalid booleanNumber for '{key}': '{value}' (expected '0' or '1')")
    else:
        errors.append(f"? Unknown expected type '{expected_type}' for key '{key}'")

# Range validation
for key, allowed_values in range_validation.items():
    if key not in inputs:
        errors.append(f"? Range validation failed: key '{key}' not found in actionInputs")
        continue
    if inputs[key] not in allowed_values:
        errors.append(f"? Invalid value for '{key}': '{inputs[key]}'. Allowed values: {allowed_values}")

# Final result
if errors:
    print("\n?? Validation failed with the following issues:")
    for err in errors:
        print(f"  - {err}")
    print("\n*** ? Validation Ended with Errors ***\n")
    sys.exit(1)
else:
    print("? All validations passed.")
    print("\n*** ? Validation Ended Successfully ***\n")
