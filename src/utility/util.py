from jsonschema import validate, Draft202012Validator
import jsonschema

def validate_schema(schema: dict, schema_name: str):
    try:
        Draft202012Validator.check_schema(schema)
        return f"Schema: {schema_name} is valid"
    except jsonschema.exceptions.SchemaError as e:
        return f"Schema: {schema_name} is invalid: {e}"

