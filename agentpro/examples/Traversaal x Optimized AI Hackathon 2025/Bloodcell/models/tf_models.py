import tensorflow as tf
import streamlit as st
import os

@st.cache_resource
def load_tf_model(model_path: str):
    if not os.path.exists(model_path):
        st.error(f"Model file not found at path: {model_path}")
        return None
    try:
        return tf.keras.models.load_model(model_path)
    except Exception as e:
        st.error(f"Error loading TensorFlow model from {model_path}: {e}")
        return None