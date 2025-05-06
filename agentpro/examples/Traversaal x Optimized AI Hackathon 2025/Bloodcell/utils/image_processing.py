from PIL import Image
import numpy as np
import streamlit as st

def preprocess_and_predict(image: Image.Image, model, class_names: list, target_size: tuple = (64, 64)) -> tuple:
    try:
        img_resized = image.resize(target_size)
        if img_resized.mode != 'RGB':
            img_resized = img_resized.convert('RGB')
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        predictions = model.predict(img_array)
        pred_index = np.argmax(predictions, axis=1)[0]
        if pred_index < len(class_names):
            predicted_class = class_names[pred_index]
        else:
            st.error(f"Prediction index {pred_index} out of bounds (len {len(class_names)}).")
            return None, None
        confidence = np.max(predictions) * 100
        return predicted_class, confidence
    except Exception as e:
        st.error(f"Image processing/prediction error: {e}")
        return None, None