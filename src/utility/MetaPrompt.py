from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt
from src.utility.util import validate_schema
from json import loads
load_dotenv()


META_SCHEMA = {
    "name": "metaschema",
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "The name of the schema"},
            "type": {
                "type": "string",
                "enum": ["object", "array", "string", "number", "boolean", "null"],
            },
            "properties": {
                "type": "object",
                "additionalProperties": {"$ref": "#/$defs/schema_definition"},
            },
            "items": {
                "anyOf": [
                    {"$ref": "#/$defs/schema_definition"},
                    {"type": "array", "items": {"$ref": "#/$defs/schema_definition"}},
                ]
            },
            "required": {"type": "array", "items": {"type": "string"}},
            "additionalProperties": {"type": "boolean"},
        },
        "required": ["type"],
        "additionalProperties": False,
        "if": {"properties": {"type": {"const": "object"}}},
        "then": {"required": ["properties"]},
        "$defs": {
            "schema_definition": {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": [
                            "object",
                            "array",
                            "string",
                            "number",
                            "boolean",
                            "null",
                        ],
                    },
                    "properties": {
                        "type": "object",
                        "additionalProperties": {"$ref": "#/$defs/schema_definition"},
                    },
                    "items": {
                        "anyOf": [
                            {"$ref": "#/$defs/schema_definition"},
                            {
                                "type": "array",
                                "items": {"$ref": "#/$defs/schema_definition"},
                            },
                        ]
                    },
                    "required": {"type": "array", "items": {"type": "string"}},
                    "additionalProperties": {"type": "boolean"},
                },
                "required": ["type"],
                "additionalProperties": False,
                "if": {"properties": {"type": {"const": "object"}}},
                "then": {"required": ["properties"]},
            }
        },
    },
}

META_SCHEMA_202012 = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://json-schema.org/draft/2020-12/schema",
    "$vocabulary": {
        "https://json-schema.org/draft/2020-12/vocab/core": True,
        "https://json-schema.org/draft/2020-12/vocab/applicator": True,
        "https://json-schema.org/draft/2020-12/vocab/unevaluated": True,
        "https://json-schema.org/draft/2020-12/vocab/validation": True,
        "https://json-schema.org/draft/2020-12/vocab/meta-data": True,
        "https://json-schema.org/draft/2020-12/vocab/format-annotation": True,
        "https://json-schema.org/draft/2020-12/vocab/content": True
    },
    "$dynamicAnchor": "meta",

    "title": "Core and Validation specifications meta-schema",
    "allOf": [
        {"$ref": "meta/core"},
        {"$ref": "meta/applicator"},
        {"$ref": "meta/unevaluated"},
        {"$ref": "meta/validation"},
        {"$ref": "meta/meta-data"},
        {"$ref": "meta/format-annotation"},
        {"$ref": "meta/content"}
    ],
    "type": ["object", "boolean"],
    "$comment": "This meta-schema also defines keywords that have appeared in previous drafts in order to prevent incompatible extensions as they remain in common use.",
    "properties": {
        "definitions": {
            "$comment": "\"definitions\" has been replaced by \"$defs\".",
            "type": "object",
            "additionalProperties": { "$dynamicRef": "#meta" },
            "deprecated": True,
            "default": {}
        },
        "dependencies": {
            "$comment": "\"dependencies\" has been split and replaced by \"dependentSchemas\" and \"dependentRequired\" in order to serve their differing semantics.",
            "type": "object",
            "additionalProperties": {
                "anyOf": [
                    { "$dynamicRef": "#meta" },
                    { "$ref": "meta/validation#/$defs/stringArray" }
                ]
            },
            "deprecated": True,
            "default": {}
        },
        "$recursiveAnchor": {
            "$comment": "\"$recursiveAnchor\" has been replaced by \"$dynamicAnchor\".",
            "$ref": "meta/core#/$defs/anchorString",
            "deprecated": True
        },
        "$recursiveRef": {
            "$comment": "\"$recursiveRef\" has been replaced by \"$dynamicRef\".",
            "$ref": "meta/core#/$defs/uriReferenceString",
            "deprecated": True
        }
    }
}

META_PROMPT_SCHEMA = """
# Instructions
Return a valid schema for the described JSON.

You must also make sure:
- all fields in an object are set as required
- I REPEAT, ALL FIELDS MUST BE MARKED AS REQUIRED
- all objects must have additionalProperties set to false
    - because of this, some cases like "attributes" or "metadata" properties that would normally allow additional properties should instead have a fixed set of properties
- all objects must have properties defined
- field order matters. any form of "thinking" or "explanation" should come before the conclusion
- $defs must be defined under the schema param
- you need to follow the 2020-12 JSON schema standard
- I REPEAT, YOU NEED TO FOLLOW THE 2020-12 JSON SCHEMA STANDARD

Notable keywords NOT supported include:
- For strings: minLength, maxLength, pattern, format
- For numbers: minimum, maximum, multipleOf
- For objects: patternProperties, unevaluatedProperties, propertyNames, minProperties, maxProperties
- For arrays: unevaluatedItems, contains, minContains, maxContains, minItems, maxItems, uniqueItems

Other notes:
- definitions and recursion are supported
- only if necessary to include references e.g. "$defs", it must be inside the "schema" object

# Examples
Input: Generate a math reasoning schema with steps and a final answer.
Output: {
    "name": "math_reasoning",
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "description": "A sequence of steps involved in solving the math problem.",
            "items": {
                "type": "object",
                "properties": {
                    "explanation": {
                        "type": "string",
                        "description": "Description of the reasoning or method used in this step."
                    },
                    "output": {
                        "type": "string",
                        "description": "Result or outcome of this specific step."
                    }
                },
                "required": [
                    "explanation",
                    "output"
                ],
                "additionalProperties": false
            }
        },
        "final_answer": {
            "type": "string",
            "description": "The final solution or answer to the math problem."
        }
    },
    "required": [
        "steps",
        "final_answer"
    ],
    "additionalProperties": false
}

Input: Give me a linked list
Output: {
    "name": "linked_list",
    "type": "object",
    "properties": {
        "linked_list": {
            "$ref": "#/$defs/linked_list_node",
            "description": "The head node of the linked list."
        }
    },
    "$defs": {
        "linked_list_node": {
            "type": "object",
            "description": "Defines a node in a singly linked list.",
            "properties": {
                "value": {
                    "type": "number",
                    "description": "The value stored in this node."
                },
                "next": {
                    "anyOf": [
                        {
                            "$ref": "#/$defs/linked_list_node"
                        },
                        {
                            "type": "null"
                        }
                    ],
                    "description": "Reference to the next node; null if it is the last node."
                }
            },
            "required": [
                "value",
                "next"
            ],
            "additionalProperties": false
        }
    },
    "required": [
        "linked_list"
    ],
    "additionalProperties": false
}

Input: Dynamically generated UI
Output: {
    "name": "ui",
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "description": "The type of the UI component",
            "enum": [
                "div",
                "button",
                "header",
                "section",
                "field",
                "form"
            ]
        },
        "label": {
            "type": "string",
            "description": "The label of the UI component, used for buttons or form fields"
        },
        "children": {
            "type": "array",
            "description": "Nested UI components",
            "items": {
                "$ref": "#"
            }
        },
        "attributes": {
            "type": "array",
            "description": "Arbitrary attributes for the UI component, suitable for any element",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the attribute, for example onClick or className"
                    },
                    "value": {
                        "type": "string",
                        "description": "The value of the attribute"
                    }
                },
                "required": [
                    "name",
                    "value"
                ],
                "additionalProperties": false
            }
        }
    },
    "required": [
        "type",
        "label",
        "children",
        "attributes"
    ],
    "additionalProperties": false
}
""".strip()

META_PROMPT = """
Given a task description or existing prompt, produce a detailed system prompt to guide a language model in completing the task effectively.

# Guidelines

- Understand the Task: Grasp the main objective, goals, requirements, constraints, and expected output.
- Minimal Changes: If an existing prompt is provided, improve it only if it's simple. For complex prompts, enhance clarity and add missing elements without altering the original structure.
- Reasoning Before Conclusions**: Encourage reasoning steps before any conclusions are reached. ATTENTION! If the user provides examples where the reasoning happens afterward, REVERSE the order! NEVER START EXAMPLES WITH CONCLUSIONS!
    - Reasoning Order: Call out reasoning portions of the prompt and conclusion parts (specific fields by name). For each, determine the ORDER in which this is done, and whether it needs to be reversed.
    - Conclusion, classifications, or results should ALWAYS appear last.
- Examples: Include high-quality examples if helpful, using placeholders [in brackets] for complex elements.
   - What kinds of examples may need to be included, how many, and whether they are complex enough to benefit from placeholders.
- Clarity and Conciseness: Use clear, specific language. Avoid unnecessary instructions or bland statements.
- Formatting: Use markdown features for readability. DO NOT USE ``` CODE BLOCKS UNLESS SPECIFICALLY REQUESTED.
- Preserve User Content: If the input task or prompt includes extensive guidelines or examples, preserve them entirely, or as closely as possible. If they are vague, consider breaking down into sub-steps. Keep any details, guidelines, examples, variables, or placeholders provided by the user.
- Constants: DO include constants in the prompt, as they are not susceptible to prompt injection. Such as guides, rubrics, and examples.
- Output Format: Explicitly the most appropriate output format, in detail. This should include length and syntax (e.g. short sentence, paragraph, JSON, etc.)
    - For tasks outputting well-defined or structured data (classification, JSON, etc.) bias toward outputting a JSON.
    - JSON should never be wrapped in code blocks (```) unless explicitly requested.

The final prompt you output should adhere to the following structure below. Do not include any additional commentary, only output the completed system prompt. SPECIFICALLY, do not include any additional messages at the start or end of the prompt. (e.g. no "---")

[Concise instruction describing the task - this should be the first line in the prompt, no section header]

[Additional details as needed.]

[Optional sections with headings or bullet points for detailed steps.]

# Steps [optional]

[optional: a detailed breakdown of the steps necessary to accomplish the task]

# Output Format

[Specifically call out how the output should be formatted, be it response length, structure e.g. JSON, markdown, etc]

# Examples [optional]

[Optional: 1-3 well-defined examples with placeholders if necessary. Clearly mark where examples start and end, and what the input and output are. User placeholders as necessary.]
[If the examples are shorter than what a realistic example is expected to be, make a reference with () explaining how real examples should be longer / shorter / different. AND USE PLACEHOLDERS! ]

# Notes [optional]

[optional: edge cases, details, and an area to call or repeat out specific important considerations]
""".strip()

TAKE_TEMPLATE  = """
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
- The provided example is a valid JSON, so the schema should be able to validate it, so don't set the fields required to be true if they are not in the example.
"""
@retry(stop=stop_after_attempt(1))
def generate_schema(example: str, description: str, valid_option: str, file_name: str, validate: bool = True) -> dict:
    task_prompt_template = PromptTemplate(
        input_variables=["json_example", "json_description", "valid_option"], template=TAKE_TEMPLATE
    )
    input_task = task_prompt_template.format(
            json_example=example, json_description=description, valid_option = valid_option
        )
    message = [
        SystemMessage(content=META_PROMPT_SCHEMA),
        HumanMessage(content="Description:\n" + input_task),
    ]
    llm = ChatOpenAI(model="gpt-4o")
    llm = llm.with_structured_output(META_SCHEMA, method="json_schema")
    chain = llm
    
    res = chain.invoke(message)
    if validate:
        validate_schema(schema=res, instance=loads(example), schema_name=file_name, verbose=False)
    return res

def generate_prompt(task_or_prompt: str) -> str:
    messages = [
        SystemMessage(content=META_PROMPT),
        HumanMessage(content="Task, Goal, or Current Prompt:\n" + task_or_prompt),
    ]
    llm = ChatOpenAI(model="gpt-4o")
    chain = llm | StrOutputParser()
    return chain.invoke(messages)
