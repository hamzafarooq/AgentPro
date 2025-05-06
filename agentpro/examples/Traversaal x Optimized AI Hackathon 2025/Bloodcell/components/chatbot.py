import streamlit as st
import numpy as np
from config import SYSTEM_PROMPT, EMBEDDING_DIMENSION
from models.gemini_client import generate_chat_response, generate_gemini_embedding
from utils.knowledge_base import load_knowledge_base, load_embeddings

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def render_chatbot():
    st.header("💬 AI Chat Assistant")
    st.caption("Ask questions about blood cells and related diseases (general information only).")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Get user input
    if prompt := st.chat_input("Your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Load knowledge base and embeddings
        data_details = load_knowledge_base()
        embeddings = load_embeddings()
        full_prompt = SYSTEM_PROMPT + f"\n\nSpecific details if relevant:\n---\n{data_details}\n---\n"

        # Search embeddings for relevant content
        if embeddings:
            try:
                query_embedding = generate_gemini_embedding(prompt, dimension=EMBEDDING_DIMENSION)
                if query_embedding is not None:
                    similarities = [
                        (e['text'], cosine_similarity(query_embedding, e['embedding']))
                        for e in embeddings
                    ]
                    # Get top 3 most similar chunks (threshold similarity > 0.7)
                    relevant_texts = [text for text, sim in sorted(similarities, key=lambda x: x[1], reverse=True)[:3] if sim > 0.7]
                    if relevant_texts:
                        context_from_embeddings = "\n\nRelevant information from knowledge base:\n" + "\n---\n".join(relevant_texts)
                        full_prompt += context_from_embeddings
            except Exception as e:
                st.warning(f"Error searching embeddings: {e}")

        full_prompt += "\n\nUser: " + prompt + "\n\nAssistant:"
        
        with st.spinner("Thinking..."):
            assistant_response = generate_chat_response(full_prompt)
        
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        st.rerun()