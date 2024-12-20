from dotenv import load_dotenv
from pinecone import Pinecone
import os
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.vector_stores import VectorStoreQuery

# Load environment variables
load_dotenv()
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone = Pinecone(api_key=pinecone_api_key)

# Initialize Pinecone index
index_name = 'quickstart'
pinecone_index = pinecone.Index(index_name)

def retrieveChunk(user_query: str, key_word: str) -> str:
    # Create an embedding for the user query
    embed_model = OpenAIEmbedding()
    query_embedding = embed_model.get_query_embedding(user_query)

    # Query the Pinecone vector store
    vector_store_query = VectorStoreQuery(
        query_embedding=query_embedding,
        similarity_top_k=4,
        mode='default'
    )

    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    query_result = vector_store.query(vector_store_query)

    outputString = ''
    i = 1
    for node in query_result.nodes:
        outputString += f'Chunk {i}:\n\n' + node.get_content(metadata_mode="all")
        i+=1

    return outputString

test = retrieveChunk('tell me about RSI', '')
print(test)