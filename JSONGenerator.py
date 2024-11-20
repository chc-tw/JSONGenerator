import json
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from json import load

INSTRUCTION = """
Generate a JSON object that satisfies the provided JSON schema based on the user's query and relevant context.

Understand the user's query and any relevant context to accurately generate a JSON object that adheres to the given schema requirements.

# Steps

1. **Understand the Schema**: Read and comprehend the structure and constraints of the provided JSON schema.
2. **Analyze the User Query**: Identify key information and context from the user's query that will influence the JSON object.
3. **Generate JSON Object**: Create a JSON object that satisfies the schema, using the contextual information from the user query.
4. **Validation**: Ensure the generated JSON object fully adheres to the schema requirements.

# Output Format

Provide the output as a JSON object without any wrapping text or code blocks. Ensure it strictly follows the specified schema.
"""

def retrieveChunk(user_query: str, key_word: str) -> str:
    doc = PyPDFLoader(f"../tech_doc.pdf").load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    puedo_chunks = text_splitter.split_documents(doc)
    return ''.join(puedo_chunks)

def generateJSON(user_query: str, key_word: str) -> str:
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", INSTRUCTION),
        ("user", "{example_query}"),
        ("ai", "{example_schema}"),
        ("user", "{user_query}"),
    ])
    llm = ChatOpenAI(model="gpt-4o")
    relevant_chunk = retrieveChunk(user_query, key_word)
    with open(f"schema/JSON_schema/{key_word}.json", "r") as f:
        schema = f.read()
    structured_llm = llm.with_structured_output(schema, method="json_schema")
    chain = prompt_template | structured_llm
    return chain.invoke({"example_query": user_query, "example_schema": schema, "user_query": user_query, "relevant_chunk": relevant_chunk})


if __name__ == "__main__":
    pseudo_query = ""
    pseudo_key_word = ""
    generateJSON(pseudo_query, pseudo_key_word)
