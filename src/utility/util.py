from jsonschema import validate, Draft202012Validator
import jsonschema
from glob import glob
import json

def validate_schema(schema: dict, instance: dict, schema_name: str, verbose: bool = True) -> str:
    Draft202012Validator.check_schema(schema)
    validate(instance=instance, schema=schema["schema"])
    if verbose:
        print(f"[Valid] Schema: {schema_name}")
    return None

def post_process_schema() -> dict:
    json_schemas = sorted(glob("schema/JSON_schema/*.json"))
    examples = sorted(glob("schema/example/*.json"))
    for json_schema, example in zip(json_schemas, examples):
        json_schema_file = json.loads(open(json_schema, "r").read())
        example_file = json.loads(open(example, "r").read())
        json_schema_file["properties"]["conditionType"]["properties"]["label"]["enum"] = [example_file["conditionType"]["label"]]
        json_schema_file["properties"]["conditionType"]["properties"]["value"]["enum"] = [example_file["conditionType"]["value"]]
        json_schema_file["properties"]["formula"]["properties"]["label"]["enum"] = [example_file["formula"]["label"]]
        json_schema_file["properties"]["formula"]["properties"]["value"]["enum"] = [example_file["formula"]["value"]]
        json_schema_file["properties"]["formula"]["properties"]["type"]["enum"] = [example_file["formula"]["type"]]
        name = json_schema_file["name"]
        json_schema_file.pop("name")
        json_schema_file = {
            "name": name,
            "schema": json_schema_file
        }
        with open(json_schema, "w") as f:
            json.dump(json_schema_file, f, indent=4)