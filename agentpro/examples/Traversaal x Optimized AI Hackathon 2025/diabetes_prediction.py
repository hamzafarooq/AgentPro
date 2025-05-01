# -*- coding: utf-8 -*-
"""Diabetes Prediction"""

# Importing libraries
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.metrics import accuracy_score
import joblib

# Load dataset
data_set = pd.read_csv('diabetes.csv')

# Features where 0 indicates missing data
columns_to_impute = ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']

# Calculate and impute means for these columns
impute_means = {}
for col in columns_to_impute:
    mean_val = data_set[col][data_set[col] != 0].mean()
    impute_means[col] = mean_val
    data_set[col] = data_set[col].replace(0, mean_val)

# Separate features and labels
X = data_set.drop(columns='Outcome', axis=1)

# Save feature names
feature_names = list(X.columns)
joblib.dump(feature_names, 'feature_names.pkl')

Y = data_set['Outcome']

# Standardize the data
scaler = StandardScaler()
scaler.fit(X)
X_scaled = scaler.transform(X)

# Update X with standardized data
X = X_scaled

# Split into train and test sets
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, stratify=Y, random_state=2)
print("Shapes:", X.shape, X_train.shape, X_test.shape)

# Train the model
classifier = svm.SVC(kernel='linear')
classifier.fit(X_train, Y_train)

# ... (rest of your code remains unchanged)