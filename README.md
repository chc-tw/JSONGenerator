# JSON Generator

This project have two aims:
1. JSON Schema Generator: It prove the tool for generating JSON schemas based on examples and descriptions. It uses LangChain and OpenAI to generate the schemas.
2. JSON Generator: It generate the JSON based on the generated schema, user query and relevant information.

## JSON Schema Generator
To generate the JSON schema, you need to provide the example and description of the schema, which can be found in the `schema/example` folder.
You can run the `SchemaGenerator.py` to generate the JSON schema.
```bash
python SchemaGenerator.py
```

### Prompt Generator using Meta Prompt
To optimize the prompt for the LLM, you can use the `PromptGenerator.py`, where we utilize Meta-prompt.
```bash
python PromptGenerator.py --prompt <path_to_prompt or prompt_content>
```

## JSON Generator
Working in progress.