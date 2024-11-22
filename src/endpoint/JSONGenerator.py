import json
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from json import load

INSTRUCTION = """
Generate a JSON object that satisfies the provided JSON schema based on the user's query and relevant context.

Understand the user's query and any relevant context to accurately generate a JSON object that adheres to the given schema requirements.

# Steps

1. **Understand the Schema**: Read and comprehend the structure and constraints of the provided JSON schema.
2. **Analyze the User Query**: Identify key information and context from the user's query that will influence the JSON object.
3. **Generate JSON Object**: Create a JSON object that satisfies the schema, using the contextual information from the user query and relevant chunk.
4. **Validation**: Ensure the generated JSON object fully adheres to the schema requirements.

# Output Format

Provide the output as a JSON object without any wrapping text or code blocks. Ensure it strictly follows the specified schema.
"""
example_query = """
Create a trading strategy using the MACD indicator to identify upward momentum.
Specifically, I want the strategy to check if the current MACD value is greater than the MACD value from 5 minutes ago.
Use the standard MACD settings with a fast period of 12, a slow period of 26, and a signal period of 9.
The time frame should be 1 minute for each period.
"""

example_chunk = """
        Simple Moving Averages and Popular Alternatives In Chapter 1
        we examined two indicator-driven triggers that are also complete mechani-
        cal trading systems: the single moving average and the two moving average
        crossover. The variations on moving average indicators are so numerous
        that a book could be devoted exclusively to their various flavors; however,
        in the interest of completeness, I address what I believe are some of the
        most significant alternatives to the simple moving average.
        As discussed in Chapter 1, simple moving averages are the most widely
        used and the easiest to calculate because they give equal weighting to each
        data point within the data set. This issue of equal weighting to each data
        point leads technicians to seek alternatives to the simple moving average.
        The problem with using a moving average that gives equal weight to
        each data point is that with longer-term moving averages—such as the 200-
        day moving average—the lagging aspect of indicator means it will be slower
        to respond to changes in trend. Obviously slower response times to trend
        changes could mean less reward and greater risk. One solution to the prob-
        lem of the lagging nature of the simple moving average is to give greater
        weight to the most recent price action. Linearly weighted and exponentially
        smoothed moving averages both attempt to address the equal weighting
        issue by giving a larger weighting factor to more recent data.2
        An alternative to the moving average weighting paradigm is found
        through the use of a volume-adjusted moving average. The volume-adjusted
        moving average suggests that directional movement accompanied by strong
        or weak volume is often a better measure of trend strength than any of the
        time-driven weighting models.
        Another problem with moving averages is choosing between shorter
        and longer time parameters. The smaller the data set, such as a 7-day mov-
        ing average, the quicker the indicator’s ability to generate signals and the
        greater its reduction of lag time. But smaller data sets also result in more
        false trend-following signals during sideways, consolidation environments.
        As discussed, larger data sets, such as a 200-day moving average, will gen-
        erate fewer, higher-quality entry signals, but those remaining signals will en-
        tail less reward and greater risk. Perry Kaufman, author of many books on Simple Moving Averages and Popular Alternatives In Chapter 1
        we examined two indicator-driven triggers that are also complete mechani-
        cal trading systems: the single moving average and the two moving average
        crossover. The variations on moving average indicators are so numerous
        that a book could be devoted exclusively to their various flavors; however,
        in the interest of completeness, I address what I believe are some of the
        most significant alternatives to the simple moving average.
        As discussed in Chapter 1, simple moving averages are the most widely
        used and the easiest to calculate because they give equal weighting to each
        data point within the data set. This issue of equal weighting to each data
        point leads technicians to seek alternatives to the simple moving average.
        The problem with using a moving average that gives equal weight to
        each data point is that with longer-term moving averages—such as the 200-
        day moving average—the lagging aspect of indicator means it will be slower
        to respond to changes in trend. Obviously slower response times to trend
        changes could mean less reward and greater risk. One solution to the prob-
        lem of the lagging nature of the simple moving average is to give greater
        weight to the most recent price action. Linearly weighted and exponentially
        smoothed moving averages both attempt to address the equal weighting
        issue by giving a larger weighting factor to more recent data.2
        An alternative to the moving average weighting paradigm is found
        through the use of a volume-adjusted moving average. The volume-adjusted
        moving average suggests that directional movement accompanied by strong
        or weak volume is often a better measure of trend strength than any of the
        time-driven weighting models.
        Another problem with moving averages is choosing between shorter
        and longer time parameters. The smaller the data set, such as a 7-day mov-
        ing average, the quicker the indicator’s ability to generate signals and the
        greater its reduction of lag time. But smaller data sets also result in more
        false trend-following signals during sideways, consolidation environments.
        As discussed, larger data sets, such as a 200-day moving average, will gen-
        erate fewer, higher-quality entry signals, but those remaining signals will en-
        tail less reward and greater risk. Perry Kaufman, author of many books on
        """

with open("schema/JSON_schema/MACD.json", "r") as f:
    example_schema = f.read()

def retrieveChunk(user_query: str, key_word: str) -> str:
    return example_chunk
    

def parse_key_word(user_query: str) -> str:
    return user_query.split(":")[0]

async def generateJSON(user_query: str, key: str) -> str:
    key_word = parse_key_word(user_query)
    input_prompt = """
    <relevant_chunk>
    {relevant_chunk}
    </relevant_chunk>

    <user_query>
    {user_query}
    </user_query>
    """
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", INSTRUCTION),
        ("user", "{example_query}"),
        ("ai", "{example_schema}"),
        ("user", input_prompt),
    ])
    llm = ChatOpenAI(model="gpt-4o", api_key=key)
    relevant_chunk = retrieveChunk(user_query, key_word)
    # with open(f"schema/JSON_schema/{key_word}.json", "r") as f:
    #     schema = f.read()
    schema = json.loads(open(f"./schema/JSON_schema/SMA.json", "r").read())
    structured_llm = llm.with_structured_output(schema, method="json_schema")
    chain = prompt_template | structured_llm
    return chain.invoke({"example_query": example_query, "example_schema": example_schema, "user_query": user_query, "relevant_chunk": relevant_chunk})


if __name__ == "__main__":
    pseudo_query = ""
    pseudo_key_word = ""
    generateJSON(pseudo_query, pseudo_key_word)
