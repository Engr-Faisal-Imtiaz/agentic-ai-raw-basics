# Agentic AI: Raw Python Journey (Projects A - E)

This repository contains my step-by-step journey of learning Agentic AI from scratch using raw Python, without using heavy frameworks like LangChain. I built everything from basic API calls to a fully functional Agent Loop with a GUI.

## 🚀 Projects Overview

* **Project A (Basic API):** Connected to LLMs using raw HTTP and OpenAI SDK (`LLM_API_USE.py`).
* **Project B (Structured JSON):** Forced the LLM to output strict JSON formats (`Fetch_Required_Data.py`).
* **Project C (Pydantic Validation):** Used Pydantic to validate LLM responses and prevent crashes (`Fetch_pydantic_valid_data.py`).
* **Project D (Tool Calling):** Taught the AI how to call Python functions based on user input (`Tool_call.py`).
* **Project E (The Agent Loop & System Monitor):** Built a complete agent loop with a Tkinter GUI (`AppUI.py`, `Logic.py`, `Manager.py`).
  * *Features:* Text-to-Speech (Voice), Background Alarms, File Creation (PDF/Text), and Real-time Weather fetching.

## ⚙️ How to Setup & Run Locally

If you want to run this project on your machine:

1. Clone the repository:

   ```bash
   git clone <your-repo-url>
   cd personal-assistant
   ```
2. Create and activate a virtual environment:
   **bash**

   ```
   python -m venv .venv
   .venv\Scripts\activate  # For Windows
   ```
3. Create a `.env` file in the root directory and add your API keys:
   **env**

   ```
   GROQ_API_KEY=your_groq_api_key_here
   WEATHER_API_KEY=your_openweathermap_api_key_here
   ```
4. Run the main application (Project E GUI):
   **bash**

   ```
   python "Project E/AppUI.py"
   ```


   ## 🛠️ Tech Stack

   Python, OpenAI SDK (Groq API), Pydantic, Tkinter (GUI), Pyttsx3 (Voice), OpenWeatherMap API.
