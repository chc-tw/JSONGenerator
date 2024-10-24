import glob
import os
from json import load

from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from tqdm import tqdm

from src.utility import generate_schema

load_dotenv()

task_template = """
    given the following json example:
    {json_example}
    please generate a json schema based on the following description:
    {json_description}
    You only need to response the plain json schema without formatting (such as "```json" or "```")
    After this paragraph, please output the json schema:
"""


def main():
    json_examples = glob.glob("schema/example/*.json")
    json_descriptions = glob.glob("schema/example/*.text")
    task_prompt_template = PromptTemplate(
        input_variables=["json_example", "json_description"], template=task_template
    )
    os.makedirs("schema/JSON_schema", exist_ok=True)

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
            json_example=json_example, json_description=json_description
        )
        result = generate_schema(input_task)
        with open(
            f"schema/JSON_schema/{file_name}.json", "w"
        ) as f:
            f.write(result)


if __name__ == "__main__":
    main()
