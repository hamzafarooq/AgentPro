from agentpro.agentpro.tools.base_tool import Tool
import joblib
import pandas as pd
import numpy as np
from typing import Optional, Any

class DiabetesPredictionTool(Tool):
    # Required by the base Tool model:
    name: str = "Diabetes Prediction"
    description: str = "Predicts diabetes risk based on medical data"
    action_type: str = "diabetes_prediction"
    input_format: str = (
        "list of 8 medical values: [pregnancies, glucose, blood_pressure, "
        "skin_thickness, insulin, bmi, dpf, age]"
    )

    # Internal attributes (optional defaults satisfy Pydantic)
    impute_means: Optional[dict] = None
    scaler: Optional[Any]       = None
    model: Optional[Any]        = None
    feature_names: Optional[list] = None
    columns_to_impute: Optional[list] = None

    def __init__(self):
        super().__init__()   # Now picks up name/description/action_type/input_format
        # Load your artifacts
        self.impute_means    = joblib.load('impute_means.pkl')
        self.scaler          = joblib.load('scaler.pkl')
        self.model           = joblib.load('model.pkl')
        self.feature_names   = joblib.load('feature_names.pkl')
        self.columns_to_impute = ['Glucose','BloodPressure','SkinThickness','Insulin','BMI']

    def run(self, input_data):
        if len(input_data) != 8:
            return "Error: Please provide exactly 8 values for prediction."
        data = list(input_data)
        for i, col in enumerate(self.feature_names):
            if col in self.columns_to_impute and data[i] == 0:
                data[i] = self.impute_means[col]
        df = pd.DataFrame([data], columns=self.feature_names)
        std = self.scaler.transform(df)
        pred = self.model.predict(std)
        return 'The person is not diabetic' if pred[0] == 0 else 'The person is diabetic'

