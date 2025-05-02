# import streamlit as st
# from PIL import Image
# from config import DISEASE_INDICATOR_CLASS_NAMES, CELL_TYPE_CLASS_NAMES
# from models.tf_models import load_tf_model
# from utils.hospital_search import search_hospitals, get_disease_description
# from utils.image_processing import preprocess_and_predict

# # Initialize AgentPro (handled globally to avoid multiple imports)
# try:
#     from agentpro import AgentPro
#     from agentpro.tools import AresInternetTool
#     tools = [AresInternetTool()]
#     agent = AgentPro(tools=tools)
#     hospital_search_available = True
# except ImportError:
#     try:
#         import sys
#         import os
#         sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../AgentPro"))
#         from agentpro import AgentPro
#         from agentpro.tools import AresInternetTool
#         tools = [AresInternetTool()]
#         agent = AgentPro(tools=tools)
#         hospital_search_available = True
#     except ImportError:
#         class AgentProPlaceholder:
#             def __init__(self, *args, **kwargs):
#                 pass
#             def __call__(self, *args, **kwargs):
#                 return "AgentPro is not available. Please check your installation."
#         agent = None
#         hospital_search_available = False

# def render_classifier():
#     st.header("🔬 Blood Image Classifier")
    
#     # Load models
#     blood_disease_model = load_tf_model('blood_cells_model.h5')
#     cell_type_model = load_tf_model('image_classification_model.h5')
    
#     if blood_disease_model is None or cell_type_model is None:
#         st.error("One or more classification models failed to load. Cannot proceed.")
#         return
    
#     col1, col2 = st.columns([1, 2])
#     with col1:
#         option = st.selectbox(
#             "Choose classification mode:",
#             ("Blood Disease", "Blood Cell Type Classification"),
#             key="classification_type",
#             help="Blood Disease: Predicts disease indicators (e.g., NPM1). Cell Type: Predicts cell types (e.g., lymphocyte)."
#         )
        
#         if option == "Blood Disease":
#             location = st.selectbox(
#                 "Select location for hospital search:",
#                 ["Lahore", "Karachi", "Islamabad", "Multan", "Faisalabad", "Peshawar"],
#                 key="location_selector",
#                 help="Select your location to find nearby hospitals that specialize in the detected disease."
#             )
        
#         uploaded_file = st.file_uploader(
#             "Upload a blood cell image",
#             type=['png', 'jpg', 'jpeg', 'tiff'],
#             key="file_uploader"
#         )
    
#     with col2:
#         if uploaded_file is not None:
#             try:
#                 image = Image.open(uploaded_file)
#                 st.image(image, caption="Uploaded Image", use_column_width=True)
#                 predicted_class = None
#                 confidence = None
#                 with st.spinner("Analyzing image..."):
#                     if option == "Blood Disease":
#                         predicted_class, confidence = preprocess_and_predict(
#                             image, blood_disease_model, DISEASE_INDICATOR_CLASS_NAMES, target_size=(224, 224)
#                         )
#                     else:
#                         predicted_class, confidence = preprocess_and_predict(
#                             image, cell_type_model, CELL_TYPE_CLASS_NAMES, target_size=(64, 64)
#                         )
                
#                 if predicted_class is not None and confidence is not None:
#                     if option == "Blood Disease":
#                         st.success(f"Predicted Disease Indicator: **{predicted_class}**")
#                         disease_description = get_disease_description(predicted_class)
#                         st.info(f"**About this marker:** {disease_description}")
                        
#                         location = st.session_state.get("location_selector", "Lahore")
#                         with st.expander(f"Find hospitals for {predicted_class} in {location}", expanded=True):
#                             if st.button("Search for Specialized Hospitals"):
#                                 with st.spinner(f"Searching for hospitals that specialize in {predicted_class} in {location}..."):
#                                     if hospital_search_available and agent:
#                                         response = search_hospitals(agent, predicted_class, location)
#                                         st.markdown("### Hospital Recommendations")
#                                         st.markdown(response)
#                                     else:
#                                         st.warning("Hospital search is not available because AgentPro could not be initialized.")
#                     else:
#                         st.success(f"Predicted Cell Type: **{predicted_class}**")
                    
#                     st.metric(label="Confidence", value=f"{confidence:.2f}%")
#                 else:
#                     st.warning("Could not make a prediction.")
#             except Exception as e:
#                 st.error(f"Error handling uploaded image: {e}")
#         else:
#             st.info("Upload an image using the panel on the left.")

import streamlit as st
from PIL import Image
from config import DISEASE_INDICATOR_CLASS_NAMES, CELL_TYPE_CLASS_NAMES
from models.tf_models import load_tf_model
from utils.hospital_search import search_hospitals, get_disease_description
from utils.image_processing import preprocess_and_predict

# Initialize AgentPro with both tools
try:
    from agentpro.agentpro import AgentPro
    from agentpro.tools import AresInternetTool, BloodDonationFinderTool
    tools = [AresInternetTool(), BloodDonationFinderTool()]
    agent = AgentPro(tools=tools)
    hospital_search_available = True
    donor_search_available = True
except ImportError:
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../agentpro"))
        from agentpro import AgentPro
        from agentpro.tools import AresInternetTool, BloodDonationFinderTool
        tools = [AresInternetTool(), BloodDonationFinderTool()]
        agent = AgentPro(tools=tools)
        hospital_search_available = True
        donor_search_available = True
    except ImportError:
        class AgentProPlaceholder:
            def __init__(self, *args, **kwargs):
                pass
            def __call__(self, *args, **kwargs):
                return "AgentPro is not available. Please check your installation."
        agent = None
        hospital_search_available = False
        donor_search_available = False

def search_donors(agent, cell_type: str, location: str) -> str:
    """
    Search for blood donors or donation centers for a specific cell type in a given location.
    
    Args:
        agent: The AgentPro instance to use for search
        cell_type: The predicted cell type (e.g., 'lymphocyte')
        location: The city/location to search in (e.g., 'Lahore')
        
    Returns:
        str: A formatted response with donor information
    """
    try:
        query = (
            f"Find blood donors or blood donation centers in {location}, Pakistan "
            f"that can assist with needs related to {cell_type} cell types. "
            f"List the top 3 with their name, contact details, address, and services offered. "
            f"Format the response with markdown headings and bullet points."
        )
        
        st.write(f"Searching for blood donors for {cell_type} in {location}...")
        response = agent(query)
        
        if not response or len(response.strip()) < 10:
            return f"No blood donors or donation centers found for {cell_type} in {location}."
        
        return f"""
## Blood Donors/Donation Centers for {cell_type} in {location}

{response}

---

**Disclaimer:** This information is provided for reference only. Please verify details directly with the donors or centers 
before making any decisions. Always consult with a qualified healthcare provider for medical advice.
"""
    except Exception as e:
        error_msg = f"Error searching for blood donors: {str(e)}"
        return f"⚠️ {error_msg}\n\nPlease try again later or contact support."

def render_classifier():
    st.header("🔬 Blood Image Classifier")
    
    # Load models
    blood_disease_model = load_tf_model('blood_cells_model.h5')
    cell_type_model = load_tf_model('image_classification_model.h5')
    
    if blood_disease_model is None or cell_type_model is None:
        st.error("One or more classification models failed to load. Cannot proceed.")
        return
    
    col1, col2 = st.columns([1, 2])
    with col1:
        option = st.selectbox(
            "Choose classification mode:",
            ("Blood Disease", "Blood Cell Type Classification"),
            key="classification_type",
            help="Blood Disease: Predicts disease indicators (e.g., NPM1). Cell Type: Predicts cell types (e.g., lymphocyte)."
        )
        
        # Location selector for both hospital and donor searches
        location = st.selectbox(
            "Select location for searches:",
            ["Lahore", "Karachi", "Islamabad", "Multan", "Faisalabad", "Peshawar"],
            key="location_selector",
            help="Select your location for hospital or blood donor searches."
        )
        
        uploaded_file = st.file_uploader(
            "Upload a blood cell image",
            type=['png', 'jpg', 'jpeg', 'tiff'],
            key="file_uploader"
        )
    
    with col2:
        if uploaded_file is not None:
            try:
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Image", use_column_width=True)
                predicted_class = None
                confidence = None
                with st.spinner("Analyzing image..."):
                    if option == "Blood Disease":
                        predicted_class, confidence = preprocess_and_predict(
                            image, blood_disease_model, DISEASE_INDICATOR_CLASS_NAMES, target_size=(224, 224)
                        )
                    else:
                        predicted_class, confidence = preprocess_and_predict(
                            image, cell_type_model, CELL_TYPE_CLASS_NAMES, target_size=(64, 64)
                        )
                
                if predicted_class is not None and confidence is not None:
                    if option == "Blood Disease":
                        st.success(f"Predicted Disease Indicator: **{predicted_class}**")
                        disease_description = get_disease_description(predicted_class)
                        st.info(f"**About this marker:** {disease_description}")
                        
                        with st.expander(f"Find hospitals for {predicted_class} in {location}", expanded=True):
                            if st.button("Search for Specialized Hospitals"):
                                with st.spinner(f"Searching for hospitals that specialize in {predicted_class} in {location}..."):
                                    if hospital_search_available and agent:
                                        response = search_hospitals(agent, predicted_class, location)
                                        st.markdown("### Hospital Recommendations")
                                        st.markdown(response)
                                    else:
                                        st.warning("Hospital search is not available because AgentPro could not be initialized.")
                    else:
                        st.success(f"Predicted Cell Type: **{predicted_class}**")
                        
                        # Add donor search for Blood Cell Type Classification
                        with st.expander(f"Find blood donors for {predicted_class} in {location}", expanded=True):
                            if st.button("Search for Blood Donors"):
                                with st.spinner(f"Searching for blood donors related to {predicted_class} in {location}..."):
                                    if donor_search_available and agent:
                                        response = search_donors(agent, predicted_class, location)
                                        st.markdown("### Blood Donor Recommendations")
                                        st.markdown(response)
                                    else:
                                        st.warning("Blood donor search is not available because AgentPro could not be initialized.")
                    
                    st.metric(label="Confidence", value=f"{confidence:.2f}%")
                else:
                    st.warning("Could not make a prediction.")
            except Exception as e:
                st.error(f"Error handling uploaded image: {e}")
        else:
            st.info("Upload an image using the panel on the left.")