import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME")
pinecone_api_key = os.environ.get("PINECONE_API_KEY")

def format_docs(docs):
    """
    Formats a list of document objects into a single string, separating each document's content with two newlines.

    Args:
        docs (list): A list of document objects, each expected to have a 'page_content' attribute.

    Returns:
        str: A single string containing the concatenated 'page_content' of all documents, separated by two newlines.
    """
    return "\n\n".join(doc.page_content for doc in docs)

def run_llm(query:str):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    docsearch = PineconeVectorStore(
        index_name=pinecone_index_name,
        embedding=embeddings,
    ) 
        
    template = """Answer user questions based solely on the context given below.
    Always cite the original source from the context. Do not make up facts nor information.
    Make the answer relevant, complete and precise.
    
    {context}
    
    Question: {question}
    
    Helpful Answer: 
      
    """
    
    custom_rag_prompt = PromptTemplate.from_template(template)
    
    llm = ChatOpenAI(
    api_key=openai_api_key,
    model="gpt-4.1-nano",
    temperature=0.2,
    )
    
    rag_chain = (
        {"question": RunnablePassthrough(), "context": docsearch.as_retriever() | format_docs }
        | custom_rag_prompt
        | llm
    )
    
    rag_result = rag_chain.invoke(query)
    
    return rag_result

if __name__ == "__main__":
    result = run_llm(query = "what are the most important facts to know about MCP during a tech interview?")
    print(result.content)