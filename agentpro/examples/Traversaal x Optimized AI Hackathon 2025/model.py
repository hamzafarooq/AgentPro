import numpy as np
import joblib

# Load saved objects
impute_means = joblib.load('impute_means.pkl')
scaler = joblib.load('scaler.pkl')
load_model = joblib.load('model.pkl')

# Define feature names and columns to impute
feature_names = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
columns_to_impute = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

# Input data
input_data = (5, 166, 72, 19, 175, 25.8, 0.587, 51)

# Impute zeros if present
input_data = list(input_data)
for i, col in enumerate(feature_names):
    if col in columns_to_impute and input_data[i] == 0:
        input_data[i] = impute_means[col]

# Convert to numpy array and standardize
input_array = np.asarray(input_data).reshape(1, -1)
std_data = scaler.transform(input_array)

# Make prediction
prediction_answer = load_model.predict(std_data)
print('The prediction is:', prediction_answer[0])

if prediction_answer[0] == 0:
    print("The person is not diabetic")
else:
    print("The person is diabetic patient")