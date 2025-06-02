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


def convert_file_path_to_web_url(file_path):
    """Convert local file path to web URL"""
    # Remove the local directory prefix and .html extension
    relative_path = file_path.replace("mcp_docs/html/", "").replace(".html", "")

    # Convert to web URL - adjust base URL as needed
    base_url = "https://modelcontextprotocol.io/docs/concepts"
    web_url = f"{base_url}/{relative_path}"

    return web_url


def ingest_docs():
    loader = DirectoryLoader(
        "mcp_docs/html",
        glob="**/*.html",
        loader_cls=BSHTMLLoader,
    )

    raw_documents = loader.load()
    print(f"loaded {len(raw_documents)} documents")

    for doc in raw_documents:
        doc.metadata["source"] = convert_file_path_to_web_url(doc.metadata["source"])

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
