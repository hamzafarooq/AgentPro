# 🧠 TROJAN\_AI – Diabetes Prediction Agentic AI (Powered by AgentPro)

Welcome to **TROJAN\_AI**, our Diabetes Prediction Agentic AI system built on **AgentPro**.
This example demonstrates how to wrap a Streamlit-based ML tool into an LLM-driven agent pipeline.

---

## 🚀 Features

* 🔮 **LLM-powered Agent** routes user queries to your diabetes predictor.
* 🩺 **Diabetes Prediction Tool** uses a trained ML model (Logistic Regression).
* 🛠️ **AgentPro modular architecture** for easy extension.
* 🌐 **Streamlit frontend** for both form-based and natural-language interaction.
* 📊 Handles raw data and imputes missing zeros with statistical means.

---

## 📂 Directory Structure

```
agentpro/examples/Traversaal x Optimized AI Hackathon 2025/TROJAN_AI/
├── app.py                   # Streamlit app + AgentPro integration
├── diabetes_tool.py         # Custom Tool implementing diabetes prediction
├── system.py                # (alias) main entrypoint for Streamlit
├── Diabetes_Prediction.ipynb# Notebook demo
├── requirements.txt         # Python dependencies
├── impute_means.pkl         # Pickled means for imputation
├── scaler.pkl               # Pickled scaler
├── model.pkl                # Pickled trained model
├── feature_names.pkl        # Feature list
├── diabetes.csv             # Sample dataset
└── user_data.csv            # Sample user inputs
```

---

## 🛠️ Installation & Setup

1. **Clone the AgentPro repository**

   ```bash
   git clone https://github.com/traversaal-ai/AgentPro.git
   cd AgentPro
   ```

2. **Install AgentPro**

   ```bash
   pip install .
   ```

   or, if you prefer editable mode:

   ```bash
   pip install -e .
   ```

3. **Go to the TROJAN\_AI example**

   ```bash
   cd agentpro/examples/"Traversaal x Optimized AI Hackathon 2025"/TROJAN_AI
   ```

4. **Install example-specific dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

   Then open the URL (usually `http://localhost:8501/`) in your browser.

> **Note:** If your local folder is named `AgentPro` (capital letters), rename it to lowercase so Python imports resolve:
>
> ```bash
> mv AgentPro agentpro
> ```

---

## 🚀 Running the Example

Inside the `TROJAN_AI` folder:

```bash
streamlit run app.py
```

* **Form mode:** enter values in each field and click “Run Agent.”
* **Natural-language mode:** type e.g.

  ```
  Predict diabetes for 5,116,74,0,0,25.6,0.201,30
  ```

  The agent will parse and invoke the tool automatically.

---

## 🧠 How It Works

1. **Streamlit UI** gathers user input.
2. **AgentPro Agent** receives the prompt and chooses `DiabetesPredictionTool`.
3. **Tool logic** imputes missing data, scales features, and runs the model.
4. **Result** is returned and displayed in the UI.

---

## 🤝 Contributing & Extending

Feel free to adapt or extend this example:

* Swap in a different ML model or dataset.
* Package as a web service or CLI.
* Add new tools (e.g., heart-disease predictor) by subclassing AgentPro’s `Tool`.

---

## 🙏 Acknowledgements

* **AgentPro**: [https://github.com/traversaal-ai/AgentPro](https://github.com/traversaal-ai/AgentPro)
* **Dataset**: Pima Indians Diabetes (UCI / Kaggle)
* **Frameworks**: Streamlit, Scikit-learn, Pandas, Joblib

---

Happy hacking! 🎉

