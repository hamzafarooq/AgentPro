import streamlit as st
from config import BLOOD_DISEASE_MODEL_PATH, CELL_TYPE_MODEL_PATH
from models.tf_models import load_tf_model

def render_model_summary():
    st.header("⚙️ TensorFlow Model Details")
    
    selected_option = st.session_state.get("classification_type", "Blood Disease")
    with st.expander(f"Show TF Model Summary for '{selected_option}'"):
        model_to_show = None
        if selected_option == "Blood Disease":
            model_to_show = load_tf_model(BLOOD_DISEASE_MODEL_PATH)
        else:
            model_to_show = load_tf_model(CELL_TYPE_MODEL_PATH)
        
        if model_to_show:
            summary_lines = []
            model_to_show.summary(print_fn=lambda x: summary_lines.append(x))
            st.text('\n'.join(summary_lines))
        else:
            st.warning("Selected classification model could not be loaded/found.")