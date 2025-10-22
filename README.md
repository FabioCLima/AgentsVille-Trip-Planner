# 🏙️ AgentsVille Trip Planner

An advanced AI-powered travel planning system that demonstrates sophisticated LLM reasoning techniques including **Role-Based Prompting**, **Chain-of-Thought Reasoning**, **ReAct Prompting**, and **Feedback Loops**.

## 🎯 Overview

The AgentsVille Trip Planner is a modular and professional system that uses specialized AI agents to create personalized travel itineraries. The system simulates a fictional city called AgentsVille and provides activities, events, and weather information to plan the perfect trip.

### ✨ Key Features

- **🤖 Specialized Agents**: ItineraryAgent and ItineraryRevisionAgent
- **🔄 ReAct Cycle**: Reasoning + Acting for iterative itinerary revision
- **📊 Automatic Evaluations**: Robust quality validation system
- **🛠️ Integrated Tools**: Calculator, activities API, evaluations
- **🌤️ Weather Compatibility**: Automatic verification of activities vs. weather
- **💰 Budget Management**: Automatic cost control
- **📝 Trip Narration**: Narrative summary of the planned experience

## 🏗️ System Architecture

```
AgentsVille-Trip-Planner/
├── 📄 main.py              # Main system execution
├── 📄 models.py             # Pydantic models for data validation
├── 📄 agents.py             # AI agents (ItineraryAgent, ItineraryRevisionAgent)
├── 📄 tools.py              # Tools for agents
├── 📄 evaluations.py        # Quality evaluation functions
├── 📄 project_lib.py        # Utility library (provided)
├── 📄 requirements.txt      # Project dependencies
├── 📄 config.env            # Environment configurations
├── 📄 tests/                # Automated tests
└── 📄 README.md             # This file
```

## 🚀 Installation and Setup

### 1. Prerequisites

- Python 3.8 or higher
- OpenAI API key (or Vocareum endpoint)

### 2. Installation

```bash
# Clone or download the project
cd AgentsVille-Trip-Planner

# Create a virtual environment using uv (recommended)
uv venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies using uv
uv pip install -r requirements.txt
```

### 3. Configuration

Edit the `config.env` file with your settings:

```env
# OpenAI API Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://openai.vocareum.com/v1

# Project Configuration
DEFAULT_MODEL=gpt-4.1-mini
MAX_REACT_STEPS=15
```

## 🎮 How to Use

### Main Execution

```bash
python main.py
```

This command runs the complete system:
1. **Phase 1**: Generates an initial itinerary based on travelers' preferences
2. **Phase 2**: Revises the itinerary using the ReAct cycle to incorporate feedback
3. **Evaluation**: Verifies that the final plan meets all quality criteria
4. **Narration**: Generates a narrative summary of the planned trip

### Tests

To run the automated tests:

```bash
python -m pytest
```

## 🔧 How It Works

### 1. ItineraryAgent
- Collects weather and activity data for requested dates
- Assembles a system prompt that includes the TravelPlan schema
- Requests the LLM to return a valid JSON TravelPlan

### 2. ItineraryRevisionAgent
- Implements a ReAct cycle (Reasoning + Acting)
- Receives the initial TravelPlan and produces THOUGHT and ACTION outputs
- ACTIONs are structured tool calls (JSON) executed by Python
- Tool results are sent back as OBSERVATION messages
- The cycle continues until the agent calls `final_answer_tool`

### 3. Evaluation System
- Verifies dates, budget, costs, and interest coverage
- Evaluates weather compatibility and feedback incorporation
- Ensures the final plan meets all quality criteria

## 🛠️ Available Tools

- **calculator_tool**: Evaluates mathematical expressions for precise calculations
- **get_activities_by_date_tool**: Retrieves available activities for a specific date
- **run_evals_tool**: Executes all evaluation functions on the travel plan
- **final_answer_tool**: Returns the final travel plan

## 📊 Data Models

The system uses Pydantic models for rigorous validation:

- **VacationInfo**: Trip information (travelers, destination, dates, budget)
- **TravelPlan**: Complete travel plan with itinerary days
- **Activity**: Individual activities with complete details
- **Weather**: Weather conditions for each day

## 🎓 Educational Aspects

This project demonstrates advanced prompt engineering techniques:

- **Role-Based Prompting**: Agents assume specialized roles
- **Chain-of-Thought**: Step-by-step reasoning for planning
- **ReAct Prompting**: Thought-action-observation cycle
- **Feedback Loops**: Self-evaluation and iterative refinement

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request to suggest improvements.

---

**Developed as part of the Udacity AI Engineering course**