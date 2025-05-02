# 🧠 Diabetes Prediction Agentic AI (Powered by AgentPro)

Welcome to the **Diabetes Prediction Agentic AI** — a modern, modular, and agentic AI system that combines machine learning with natural language interaction to predict diabetes based on medical features. This project uses **[AgentPro](https://github.com/traversaal-ai/AgentPro)**, a powerful tool framework that brings LLM-based tool use, decision-making, and structured I/O under one roof.

> **🌟 Talk to the AI in natural language**, and it will intelligently invoke the diabetes prediction tool with structured arguments — all thanks to the underlying agentic pipeline.

---

## 🚀 Features

* 🔮 **LLM-powered Agent** that understands user queries and maps them to prediction tasks.
* 🩺 **Diabetes Prediction Tool** powered by trained machine learning models.
* 🛠️ **Tool-based architecture** via AgentPro for modularity and extensibility.
* 🌐 **Streamlit Frontend** for smooth, interactive user experience.
* 📈 Handles raw or imputed medical data (e.g., 0s replaced with statistical means).
* 💬 Accepts both **structured input fields** and **natural-language commands**.

---

## 🧩 Project Structure

```
Traversaal_Ai/
│
├── agentpro/                         # AgentPro framework (submodule or internal copy)
│   └── agentpro/
│       └── tools/
│           ├── base_tool.py
│           ├── ares_tool.py
│           └── duckduckgo_tool.py
│
├── diabetes_tool.py                 # Custom ML tool for diabetes prediction
├── impute_means.pkl                # Saved imputation means for missing values
├── scaler.pkl                      # StandardScaler instance
├── model.pkl                       # Trained ML model
├── feature_names.pkl               # List of model features
│
├── system.py                       # Main Streamlit app + Agent integration
├── requirements.txt                # Required dependencies
└── README.md                       # You are here 🚀
```

---

## 🧠 How It Works

### 🛠️ Agentic Pipeline (Simplified)

```
User Query (e.g. "Is this person diabetic: 6,148,72,35,0,33.6,0.627,50")
   ⬇
Streamlit UI collects the input
   ⬇
AgentPro Agent receives the query
   ⬇
Agent decides to call DiabetesPredictionTool with structured arguments
   ⬇
Tool processes inputs (with imputation, scaling, model inference)
   ⬇
Prediction returned → UI displays result
```

---

## 📦 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Traversaal_Ai.git
cd Traversaal_Ai
```

### 2. Install Python Dependencies

Ensure you have **Python 3.12**. Then install requirements:

```bash
pip install -r requirements.txt
```

> If `requirements.txt` doesn't exist yet, you can create one using:

```bash
pip freeze > requirements.txt
```

Make sure it includes:

```txt
streamlit
pandas
numpy
scikit-learn
joblib
pydantic
openai  # If AgentPro uses OpenAI API
```

### 3. Run the Streamlit App

```bash
streamlit run system.py
```

Visit the displayed URL (typically `http://localhost:8501/`) in your browser.

---

## 🎯 How to Use

### Option 1: Direct Entry

Use the **structured number inputs** to enter:

```
Pregnancies, Glucose, Blood Pressure, Skin Thickness, Insulin, BMI, DPF, Age
```

Click **Run Agent** → you'll get a prediction: *"The person is diabetic"* or *"The person is not diabetic"*.

### Option 2: Natural Language Command

Type something like:

```
"Predict diabetes for 5,116,74,0,0,25.6,0.201,30"
```

The LLM + Agent will understand, extract values, and make the prediction using the tool.

---

## 🧠 Model & Tool Details

* Trained using Pima Indians Diabetes Dataset
* Preprocessing includes:

  * Replacing 0s in some features with precomputed means (`impute_means.pkl`)
  * Feature scaling with `scaler.pkl`
* Logistic Regression or SVM (`model.pkl`) trained for binary classification

---

## 🧰 Powered by AgentPro

[AgentPro](https://github.com/traversaal-ai/AgentPro) is the agentic core of this project:

* Provides `Tool` base class and agent logic
* Automates tool selection and argument formatting
* Enables LLM to use tools like functions with typed inputs and validations

Your tool (DiabetesPredictionTool) inherits from AgentPro's `Tool` base class and implements `run(input_data)` with all logic.

---

## 🤝 Contributing

Want to contribute? Here’s how you can help:

* ✅ Improve model accuracy with better preprocessing or advanced ML techniques
* 📦 Package the app as a web or mobile service
* 🤖 Add new tools to the agent (e.g., heart disease, liver function, etc.)
* 🔐 Integrate security/auth for production environments



## 🙌 Acknowledgements

* Agentic framework: [AgentPro](https://github.com/traversaal-ai/AgentPro)
* Dataset: [Pima Indians Diabetes Dataset (UCI)](https://www.kaggle.com/datasets/uciml/pima-indians-diabetes-database)
* Frameworks used: `Streamlit`, `Scikit-learn`, `Pandas`, `Pydantic`, `Joblib`

