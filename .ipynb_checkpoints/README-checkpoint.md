# AgentPro

AgentPro is a flexible framework for building AI agents with multiple specialized tools. This repository allows you to create powerful agents that can search the internet, generate code, analyze YouTube videos, create presentations, and more.

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License: MIT">
</p>

## Features

- 🧠 **Flexible Agent Architecture**: Built on the ReAct framework to combine reasoning and action
- 🔧 **Modular Tool System**: Easily extend with custom tools
- 🌐 **Internet Search**: Real-time web search using the Ares API
- 💻 **Code Generation & Execution**: Generate and run Python code on-the-fly
- 🎬 **YouTube Analysis**: Search, extract transcripts, and summarize YouTube videos
- 📊 **Presentation Generation**: Create PowerPoint presentations automatically

## Quick Start

### Installation

Clone the repository and install the required packages:

```bash
git clone https://github.com/yourusername/agentpro.git
cd agentpro
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory with your API keys:

```
OPENAI_API_KEY=your_openai_api_key
TRAVERSAAL_ARES_API_KEY=your_traversaal_ares_api_key
```

### Running the Agent

From the command line:

```bash
python main.py
```

This starts an interactive session with the agent where you can enter queries.

## Usage Examples

### Basic Usage

```python
from agentpro import AgentPro
from agentpro.tools import AresInternetTool, CodeEngine, YouTubeSearchTool, SlideGenerationTool

# Initialize tools
ares_tool = AresInternetTool()
code_tool = CodeEngine()
youtube_tool = YouTubeSearchTool()
slide_tool = SlideGenerationTool()

# Create agent with tools
agent = AgentPro(tools=[ares_tool, code_tool, youtube_tool, slide_tool])

# Run a query
response = agent("Generate a presentation on the latest AI advancements")
print(response)
```

### Example Queries

The agent can handle a variety of tasks:

- **Internet Research**: "What are the latest developments in quantum computing?"
- **Code Generation**: "Create a Python script to analyze stock prices and generate a chart"
- **YouTube Analysis**: "Find and summarize recent videos about machine learning"
- **Presentation Creation**: "Make a presentation about renewable energy sources"

## Tools Overview

### AresInternetTool

Searches the internet for real-time information using the Traversaal Ares API.

```python
ares_tool = AresInternetTool()
result = ares_tool.run("recent advances in AI")
```

### CodeEngine

Generates and executes Python code based on natural language descriptions.

```python
code_tool = CodeEngine()
result = code_tool.run("create a bar chart comparing FAANG stocks")
```

### YouTubeSearchTool

Searches for YouTube videos, extracts transcripts, and summarizes content.

```python
youtube_tool = YouTubeSearchTool()
result = youtube_tool.run("machine learning tutorials")
```

### SlideGenerationTool

Creates PowerPoint presentations from structured content.

```python
slide_tool = SlideGenerationTool()
slides = [
    {"slide_title": "Introduction", "content": "Overview of the topic"},
    {"slide_title": "Key Points", "content": "The main arguments and findings"}
]
result = slide_tool.run(slides)
```

### DataAnalysisTool

Analyzes data files and provides statistical insights, visualizations, and exploratory data analysis.

```python
data_tool = DataAnalysisTool()

# Basic usage with a file path
result = data_tool.run("path/to/data.csv")

# With specific analysis parameters
analysis_params = {
    "file_path": "path/to/data.csv",
    "analysis_type": "visualization",
    "viz_type": "correlation",
    "columns": ["age", "income", "education"]
}
result = data_tool.run(analysis_params)
```

## Creating Custom Tools

You can create your own tools by extending the `Tool` base class:

```python
from agentpro.tools.base import Tool

class MyCustomTool(Tool):
    name: str = "My Custom Tool"
    description: str = "Description of what your tool does"
    arg: str = "Information about the required input format"

    def run(self, prompt: str) -> str:
        # Your tool implementation here
        return "Result of the tool operation"
```

Then initialize your agent with the custom tool:

```python
custom_tool = MyCustomTool()
agent = AgentPro(tools=[custom_tool, ares_tool, code_tool])
```

## Project Structure

```
agentpro/
├── agentpro/
│   ├── __init__.py
│   ├── agent.py              # Main agent implementation
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── base.py           # Base tool classes
│   │   ├── ares_tool.py      # Internet search
│   │   ├── code_tool.py      # Code generation
│   │   ├── youtube_tool.py   # YouTube analysis
│   │   └── slide_tool.py     # Presentation generation
│   └── examples/
│       ├── __init__.py
│       └── example_usage.py  # Usage examples
├── main.py                   # CLI entry point
├── requirements.txt          # Dependencies
└── .env                      # API keys (create this file)
```

## Requirements

- Python 3.8+
- OpenAI API key
- Traversaal Ares API key (for internet search)

## License

This project is licensed under the MIT License - see the LICENSE file for details.