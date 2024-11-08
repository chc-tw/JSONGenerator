import glob
import os
from json import load

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from tqdm import tqdm
import json
from src.utility import generate_schema, validate_schema

load_dotenv()




def main():
    with open("schema/example/Strategy Dialog Options.md", "r") as f:
        valid_option = f.read()
    json_examples = sorted(glob.glob("schema/example/*.json"))
    json_descriptions = sorted(glob.glob("schema/example/*.txt"))
    assert len(json_examples) == len(json_descriptions), "Number of examples and descriptions do not match"

    os.makedirs("schema/JSON_schema", exist_ok=True)
    results = []
    for json_example, json_description in tqdm(
        zip(json_examples, json_descriptions),
        total=len(json_examples),
        desc="Processing files",
    ):
        file_name = json_example.split("/")[-1].split(".")[0]
        with open(json_example, "r") as example_file:
            json_example = example_file.read()
        with open(json_description, "r") as description_file:
            json_description = description_file.read()

        
        result = generate_schema(example=json_example, description=json_description, valid_option=valid_option, file_name=file_name)
        # results.append(validate_schema(result, file_name))
        with open(
            f"schema/JSON_schema/{file_name}.json", "w"
        ) as f:
            json.dump(result, f, indent=4)
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
