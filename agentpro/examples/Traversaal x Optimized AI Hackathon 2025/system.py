import os
import sys
import pandas as pd
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENROUTER_API_KEY")
os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"

import streamlit as st
import numpy as np
import joblib
from agentpro.agentpro import AgentPro
from agentpro.agentpro.tools.ares_tool import AresInternetTool
from agentpro.agentpro.tools.duckduckgo_tool import DuckDuckGoTool
from diabetes_tool import DiabetesPredictionTool

# Initialize tools and agent
try:
    diabetes_tool = DiabetesPredictionTool()
    internet_tool = AresInternetTool()
    search_tool = DuckDuckGoTool()
    agent = AgentPro(
        tools=[diabetes_tool, internet_tool, search_tool]
    )
except Exception as e:
    st.error(f"Failed to initialize agent: {str(e)}")
    st.stop()

# Custom CSS for styling
st.markdown("""
<style>
.main-header { color: #2c3e50; font-size: 36px; font-weight: bold; text-align: center; margin-bottom: 20px; }
.sub-header  { color: #34495e; font-size: 24px; font-weight: bold; margin-top: 20px; }
.info-box    { background-color: #e8f4f8; padding: 15px; border-radius: 10px; margin-bottom: 20px; font-size: 16px; color: #2c3e50; }
.prediction-success { background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; font-weight: bold; }
.prediction-error   { background-color: #f8d7da; color: #721c24; padding: 10px; border-radius: 5px; font-weight: bold; }
.stButton>button      { background-color: #3498db; color: white; border-radius: 5px; padding: 10px 20px; font-size: 16px; }
.stButton>button:hover{ background-color: #2980b9; }
.stNumberInput input { border-radius: 5px; padding: 5px; }
</style>
""", unsafe_allow_html=True)

# Functions for data storage and precautions
def store_user_data(data_list):
    headers = diabetes_tool.feature_names
    df = pd.DataFrame([data_list], columns=headers)
    file_path = "user_data.csv"
    if os.path.exists(file_path):
        df.to_csv(file_path, mode='a', header=False, index=False)
    else:
        df.to_csv(file_path, index=False)


def get_precautions(is_diabetic):
    if is_diabetic:
        return [
            "Monitor blood sugar levels regularly.",
            "Follow a balanced diet low in sugar and carbohydrates.",
            "Engage in regular physical activity (e.g., 30 minutes most days).",
            "Consult a healthcare professional for personalized advice."
        ]
    else:
        return [
            "Maintain a healthy diet rich in fruits, vegetables, and whole grains.",
            "Exercise regularly to keep a healthy weight.",
            "Get routine health check-ups to monitor your condition.",
            "Stay hydrated and manage stress levels."
        ]

# Streamlit app
def main():
    st.markdown('<div class="main-header">Diabetes AI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="info-box">Welcome! I’m an AI agent that can predict your diabetes risk, suggest precautions, and provide educational resources. Ask me anything!</div>', unsafe_allow_html=True)

    st.sidebar.title("About")
    st.sidebar.write("""
    This AI agent uses specialized tools to assist with diabetes-related queries:
    - **Prediction Agent**: Predicts diabetes risk using an SVM model trained on the PIMA Indians Diabetes Dataset.
    - **Internet Agent**: Answers general questions about diabetes using live web search.
    - **Resource Agent**: Provides links to tutorials, videos, and articles on diabetes management.
    """)

    # Input section
    st.markdown('<div class="sub-header">Enter Your Medical Data (optional for predictions)</div>', unsafe_allow_html=True)
    data_input_method = st.radio("Select Data Input Method", ["Separate Fields", "Comma Separated"])

    if data_input_method == "Separate Fields":
        st.markdown("Provide your details below. Zeros in certain fields will be imputed with average values.")
        col1, col2 = st.columns(2)
        with col1:
            pregnancies = st.number_input('Pregnancies', min_value=0, max_value=20, value=0, help="Number of times pregnant (0-20)")
            glucose = st.number_input('Glucose (mg/dL)', min_value=0, max_value=300, value=0, help="Blood sugar level (70-140 mg/dL)")
            blood_pressure = st.number_input('Blood Pressure (mm Hg)', min_value=0, max_value=150, value=0, help="Diastolic blood pressure (60-90 mm Hg)")
            skin_thickness = st.number_input('Skin Thickness (mm)', min_value=0, max_value=100, value=0, help="Triceps skin fold thickness (mm)")
        with col2:
            insulin = st.number_input('Insulin (mu U/ml)', min_value=0, max_value=1000, value=0, help="2-hour serum insulin (mu U/ml)")
            bmi = st.number_input('BMI', min_value=0.0, max_value=70.0, value=0.0, help="Body Mass Index (18.5-30)")
            dpf = st.number_input('Diabetes Pedigree Function', min_value=0.0, max_value=3.0, value=0.0, help="Genetic diabetes risk score (0.0-3.0)")
            age = st.number_input('Age', min_value=0, max_value=120, value=0, help="Age in years (0-120)")
        if st.button('Set My Data (Separate Fields)'):
            data = [pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, dpf, age]
            st.session_state['medical_data'] = data
            store_user_data(data)
            st.success("Your data has been set and stored!")
    else:
        comma_data = st.text_input("Enter 8 values separated by commas", placeholder="e.g., 6,148,72,35,0,33.6,0.627,50")
        if st.button("Set My Data (Comma Separated)"):
            try:
                values = [float(x.strip()) for x in comma_data.split(",")]
                if len(values) != 8:
                    st.error("Please enter exactly 8 comma separated values.")
                else:
                    st.session_state['medical_data'] = values
                    store_user_data(values)
                    st.success("Your data has been set and stored!")
            except Exception as e:
                st.error(f"Error processing comma separated data: {e}")

    # Query section
    st.markdown('<div class="sub-header">Ask Me Anything About Diabetes</div>', unsafe_allow_html=True)
    user_query = st.text_input("Your query:", placeholder="E.g., 'Predict my diabetes risk' or 'What are diabetes symptoms?'")

    if user_query:
        query_with_data = user_query
        if 'medical_data' in st.session_state:
            query_with_data += f" Use this data: {st.session_state['medical_data']}"

        with st.spinner('Processing your query...'):
            try:
                reasoning_response = agent.run(query_with_data)
                st.markdown("**Reasoning/Information Response:**")
                st.markdown(reasoning_response)

                if 'medical_data' in st.session_state:
                    prediction_response = diabetes_tool.run(st.session_state['medical_data'])
                    is_diabetic = "diabetic" in prediction_response.lower()
                    st.markdown(f"<div class='prediction-success'><strong>Prediction Result:</strong> {prediction_response}</div>", unsafe_allow_html=True)
                    st.markdown("<div class='sub-header'>Recommended Precautions</div>", unsafe_allow_html=True)
                    for p in get_precautions(is_diabetic): st.markdown(f"- {p}")

                # Use search tool for resources
                resource_query = user_query if 'medical_data' not in st.session_state else "Diabetes management tutorials and videos"
                resource_response = search_tool.run(resource_query)
                st.markdown("<div class='sub-header'>Recommended Resources</div>", unsafe_allow_html=True)
                st.markdown(resource_response, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error processing your query: {str(e)}")

    # Disclaimer
    st.markdown('<div class="info-box">*Disclaimer: This prediction is not a substitute for professional medical advice.*</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()

