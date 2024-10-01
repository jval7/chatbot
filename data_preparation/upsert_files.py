import os

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import CharacterTextSplitter

load_dotenv()

pinecone_api_key = os.environ.get("PINECONE_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")
index_name = os.environ.get("INDEX_NAME")


def upsert_files() -> None:
    loader = PyPDFLoader("test3.pdf")
    pages = loader.load_and_split()
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
    docs = text_splitter.split_documents(pages)

    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    PineconeVectorStore.from_documents(docs, embeddings, index_name=index_name)


upsert_files()
