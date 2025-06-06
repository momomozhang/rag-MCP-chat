from typing import Set

import streamlit as st
from dotenv import load_dotenv

from backend.rag_openai import run_llm

load_dotenv()

st.header("MCP RAG Chatbot")

prompt = st.text_input(
    "Prompt",
    placeholder="Enter your prompt here...",
)

if "user_prompt_history" not in st.session_state:
    st.session_state["user_prompt_history"] = []

if "chat_answers_history" not in st.session_state:
    st.session_state["chat_answers_history"] = []

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []


def create_sources_string(source_urls: Set[str]) -> str:
    """Generates a formatted string listing source URLs.

    Args:
        source_urls: A set of source URL strings.

    Returns:
        A formatted string that lists the sources in sorted order, each prefixed with a number.
        Returns an empty string if no sources are provided.
    """
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i + 1}. {source}\n"
    return sources_string


if prompt:
    with st.spinner("Generating response..."):
        generated_response = run_llm(
            query=prompt,
            chat_history=st.session_state["chat_history"],
        )
        sources = set([doc.metadata["source"] for doc in generated_response["context"]])

        FORMATTED_RESPONSE = (
            f"{generated_response['answer']} \n\n {create_sources_string(sources)}"
        )

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(FORMATTED_RESPONSE)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["answer"]))

if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        reversed(st.session_state["user_prompt_history"]),
        reversed(st.session_state["chat_answers_history"]),
    ):
        st.chat_message("user").write(user_query)
        st.chat_message("assistant").write(generated_response)
