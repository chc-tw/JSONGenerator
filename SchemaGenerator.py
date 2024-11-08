import glob
import os
from json import load

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from tqdm import tqdm
import json
from src.utility import generate_schema, validate_schema

load_dotenv()

task_template = """
Generate a JSON schema based on the provided JSON example, description, and valid options.

# Steps

1. **Analyze the JSON Example**: Understand the structure and data types of each field in the JSON example provided.
2. **Interpret the Description**: Extract key details from the description to understand the intended configuration and adjust the schema accordingly.
3. **Utilize Valid Options**: Incorporate the valid options provided to ensure all fields have correct and permissible values.
4. **Create JSON Schema**: Construct a JSON schema that reflects the structure, data types, constraints, and valid options for each field.

# Provided Reference
<json_example>
{json_example}
</json_example>
<json_description>
{json_description}
</json_description>
<valid_options>
{valid_option}
</valid_options>

# Output Format

The output should be a plain JSON schema representing the structure, types, and constraints of the strategy form configuration.

# Notes

- Ensure that each field in the schema corresponds to the appropriate type (e.g., string, number, object).
- Use the valid options to restrict fields to acceptable values.
- The schema should reflect the description by setting defaults or constraints as specified (e.g., specific formula, comparison, or parameters).
- Do not include any formatting or code block markers in the response.
- You need to follow the 2020-12 JSON schema standard.
"""


def main():
    with open("schema/example/Strategy Dialog Options.md", "r") as f:
        valid_option = f.read()
    json_examples = glob.glob("schema/example/*.json")
    json_descriptions = glob.glob("schema/example/*.text")
    
    task_prompt_template = PromptTemplate(
        input_variables=["json_example", "json_description", "valid_option"], template=task_template
    )
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

        input_task = task_prompt_template.format(
            json_example=json_example, json_description=json_description, valid_option = valid_option
        )
        result = generate_schema(input_task)
        results.append(validate_schema(result, file_name))
        with open(
            f"schema/JSON_schema/{file_name}.json", "w"
        ) as f:
            json.dump(result, f)
    for result in results:
        print(result)


if __name__ == "__main__":
    main()
