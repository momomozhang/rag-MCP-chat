import os
from dotenv import load_dotenv
from langchain.chains.retrieval import create_retrieval_chain
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain import hub


load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")

def run_llm(query:str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = PineconeVectorStore(
        index_name=pinecone_index_name,
        embedding=embeddings,
    )
    chat = ChatOpenAI(verbose=True, temperature=0)
    
    retrieval_qa_chat_prompt = hub.pull("langchain-ai/retrieval-qa-chat")
    
    stuff_documents_chain = create_stuff_documents_chain(
        llm=chat,
        prompt = retrieval_qa_chat_prompt,
        )
    
    rag_chain = create_retrieval_chain(
        retriever=docsearch.as_retriever(),
        combine_docs_chain=stuff_documents_chain,
    )
    
    rag_result = rag_chain.invoke(input={"input":query})
    return rag_result

if __name__ == "__main__":
    result = run_llm(query = "what are the most important facts to know about MCP during a tech interview?")
    print(result["answer"])