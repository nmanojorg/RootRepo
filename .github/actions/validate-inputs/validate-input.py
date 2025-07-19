import sys
import os
import pathlib

def parse_kv_string(s):
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            print(f"? Invalid key=value pair: {pair}")
            sys.exit(1)
        k, v = pair.strip().split('=', 1)
        result[k.strip()] = v.strip()
    return result

def parse_csv(s):
    return [i.strip() for i in s.split(',') if i.strip()]

def parse_type_validation_grouped(s):
    # Ex: "booleanString=debug test,string=env"
    result = {}
    if s.strip() == '':
        return result
    for pair in s.split(','):
        if '=' not in pair:
            print(f"? Invalid typeValidations format: {pair}")
            sys.exit(1)
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
            print(f"? Invalid rangeValidations format: {pair}")
            sys.exit(1)
        key, values = pair.strip().split('=', 1)
        result[key.strip()] = values.strip().split()
    return result

# Read inputs from environment
inputs = parse_kv_string(os.environ.get('INPUT_ACTIONINPUTS', ''))
required = parse_csv(os.environ.get('INPUT_REQUIREDINPUTS', ''))
optional = parse_csv(os.environ.get('INPUT_OPTIONALINPUTS', ''))
file_keys = parse_csv(os.environ.get('INPUT_FILESPATHINPUTS', ''))  # Now a list, not kv
type_validation = parse_type_validation_grouped(os.environ.get('INPUT_TYPEVALIDATIONS', ''))
range_validation = parse_range_validation(os.environ.get('INPUT_RANGEVALIDATIONS', ''))

# Validate required keys are present and non-empty
for key in required:
    if key not in inputs or inputs[key] == '':
        print(f"? Missing or empty required parameter: {key}")
        sys.exit(1)

# Validate file path existence
for key in file_keys:
    if key not in inputs:
        print(f"? File validation failed: input '{key}' not found in actionInputs")
        sys.exit(1)
    file_path = inputs[key]
    if not pathlib.Path(file_path).exists():
        print(f"? File does not exist for key '{key}': {file_path}")
        sys.exit(1)

# Type validation
for key, expected_type in type_validation.items():
    if key not in inputs:
        print(f"? Type check failed: key '{key}' not in inputs")
        sys.exit(1)
    value = inputs[key]
    if expected_type == 'string':
        continue
    elif expected_type == 'booleanString':
        if value.lower() not in ['true', 'false']:
            print(f"? Invalid booleanString for {key}: {value}")
            sys.exit(1)
    elif expected_type == 'booleanNumber':
        if value not in ['0', '1']:
            print(f"? Invalid booleanNumber for {key}: {value}")
            sys.exit(1)
    else:
        print(f"? Unknown type for {key}: {expected_type}")
        sys.exit(1)

# Range validation
for key, allowed_values in range_validation.items():
    if key not in inputs:
        print(f"? Range validation failed: key '{key}' not in inputs")
        sys.exit(1)
    if inputs[key] not in allowed_values:
        print(f"? Invalid value for {key}: '{inputs[key]}'. Allowed: {allowed_values}")
        sys.exit(1)

print("? All validations passed")
