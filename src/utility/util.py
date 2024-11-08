from jsonschema import validate, Draft202012Validator
import jsonschema

def validate_schema(schema: dict, instance: dict, schema_name: str, verbose: bool = True) -> str:
    Draft202012Validator.check_schema(schema)
    validate(instance=instance, schema=schema)
    if verbose:
        print(f"[Valid] Schema: {schema_name}")
    return None
