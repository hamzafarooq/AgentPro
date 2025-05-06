import google.generativeai as genai
import numpy as np
import streamlit as st
from config import GEMINI_MODEL_NAME, EMBEDDING_MODEL_NAME

def configure_gemini():
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except KeyError:
        st.error("❌ Google API Key not found. Please ensure it's in `.streamlit/secrets.toml` as GOOGLE_API_KEY='YourKey'.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error configuring Google AI SDK: {e}")
        st.stop()

def generate_gemini_embedding(text: str, dimension: int = None) -> np.ndarray:
    try:
        embed_config = {}
        if dimension is not None and dimension > 0:
            embed_config["output_dimensionality"] = dimension
        result = genai.embed_content(
            model=EMBEDDING_MODEL_NAME,
            content=text,
            task_type="RETRIEVAL_QUERY",
            **embed_config
        )
        return np.array(result["embedding"], dtype=np.float32)
    except Exception as e:
        st.error(f"Error generating embedding: {e}")
        return None

def generate_chat_response(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(contents=[prompt])
        if response.parts:
            return response.text
        elif not response.candidates:
            st.warning(f"Feedback: {response.prompt_feedback}")
            return "Response may have been blocked due to safety settings or contains no content."
        else:
            st.warning(f"Unexpected response: {response}")
            return "Received an unexpected response structure."
    except Exception as e:
        st.error(f"❌ Error generating content: {e}")
        return f"Sorry, an error occurred: {e}"