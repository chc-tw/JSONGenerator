from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec
import os
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.readers.web import SimpleWebPageReader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.schema import TextNode
from llama_index.core import SimpleDirectoryReader
from llama_index.core.extractors import (
    SummaryExtractor,
    QuestionsAnsweredExtractor,
    TitleExtractor,
    KeywordExtractor,
)
from llama_index.core.ingestion import IngestionPipeline
import asyncio


load_dotenv()
pinecone_api_key = os.getenv('PINECONE_API_KEY')
pinecone = Pinecone(api_key=pinecone_api_key)

os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
llm = OpenAI(model="gpt-4o")

index_name = 'quickstart'
# delete index if needed
# pinecone.delete_index(index_name)

# create pinecone index
pinecone.create_index(
    name = 'quickstart',
    dimension=1536, # by default using OpenAI text-embedding-ada-002 for embedding model
    metric='cosine',
    spec=ServerlessSpec(
        cloud='aws',
        region='us-east-1'
    )
)

# load documents from web
web_documents = SimpleWebPageReader(html_to_text=True).load_data(
    [
        "https://capital.com/relative-strength-index",
        "https://capital.com/macd",
        "https://capital.com/moving-average",
        "https://capital.com/bollinger-bands",
        "https://capital.com/candlestick-patterns"
    ]
)

# Load the PDF document
pdf_path = "./documents"
new_documents = SimpleDirectoryReader(
    input_files=[
        "./documents/RSI.txt",
        "./documents/MA.txt",
        "./documents/MACD.txt",
        "./documents/Bollinger Bands.txt",
    ]
    ).load_data()

text_parser = SentenceSplitter(
    chunk_size=1024,
    chunk_overlap=200
)

# Perform Chunking
web_text_chunks = []
web_doc_idxs = []
for doc_idx, page in enumerate(web_documents):
    page_text = page.get_text()
    cur_text_chunks = text_parser.split_text(page_text)
    web_text_chunks.extend(cur_text_chunks)
    web_doc_idxs.extend([doc_idx] * len(cur_text_chunks))

pdf_text_chunks = []
pdf_doc_idxs = []
for doc_idx, page in enumerate(new_documents):
    page_text = page.get_text()
    cur_text_chunks = text_parser.split_text(page_text)
    pdf_text_chunks.extend(cur_text_chunks)
    pdf_doc_idxs.extend([doc_idx] * len(cur_text_chunks))

# Construct Nodes
web_nodes = []
for idx, text_chunk in enumerate(web_text_chunks):
    src_doc_idx = web_doc_idxs[idx]
    src_page = web_documents[src_doc_idx]
    node = TextNode(
        text=text_chunk,
        metadata={
            'source_url': src_page.get_doc_id()
        }
    )
    web_nodes.append(node)

pdf_nodes = []
for idx, text_chunk in enumerate(pdf_text_chunks):
    src_doc_idx = pdf_doc_idxs[idx]
    src_page = new_documents[src_doc_idx]
    node = TextNode(
        text=text_chunk,
        metadata={
            'source_file': src_page.metadata['file_name']
        }
    )
    pdf_nodes.append(node)

# Extract Metadata from Nodes
transformations = [
    TitleExtractor(nodes=5, llm=llm),
    QuestionsAnsweredExtractor(questions=3, llm=llm),
    SummaryExtractor(summaries=["prev", "self"]),
    KeywordExtractor(keywords=10, llm=llm)
]

pipeline = IngestionPipeline(transformations=transformations)

web_nodes = asyncio.run(pipeline.arun(nodes=web_nodes, in_place=False))
pdf_nodes = asyncio.run(pipeline.arun(nodes=pdf_nodes, in_place=False))

# Generate Embeddings from Nodes
embed_model = OpenAIEmbedding()

for node in web_nodes:
    node_embedding = embed_model.get_text_embedding(
        # Retrieve the text content of the node
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

for node in pdf_nodes:
    node_embedding = embed_model.get_text_embedding(
        # Retrieve the text content of the node
        node.get_content(metadata_mode="all")
    )
    node.embedding = node_embedding

# Upload Nodes on Pinecone Vectorstore
pinecone_index = pinecone.Index(index_name)
vector_store = PineconeVectorStore(pinecone_index=pinecone_index)

vector_store.add(web_nodes)
vector_store.add(pdf_nodes)