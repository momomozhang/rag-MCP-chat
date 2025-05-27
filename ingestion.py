import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DirectoryLoader, BSHTMLLoader
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

def ingest_docs():
    loader = DirectoryLoader(
        "mcp_docs/html",
        glob="**/*.html",
        loader_cls=BSHTMLLoader,
    )
    
    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1200,
        chunk_overlap=200,
    )
    
    docs_chunked = text_splitter.split_documents(raw_documents)
    
    print(f"Going to add {len(docs_chunked)} to Pinecone")
    
    PineconeVectorStore.from_documents(
        documents=docs_chunked,
        embedding=embeddings,
        index_name=pinecone_index_name,
    )
    
    print("Loading to vectortore done!")

if __name__ == "__main__":
    ingest_docs()