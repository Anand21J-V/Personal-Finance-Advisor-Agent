# 🧠💸 AI-Powered Personal Finance Advisor App

An intelligent, multi-agent **Flask** application built using **LangGraph** and **Groq's LLaMA 3** to help users plan their financial goals, analyze risk, and get personalized investment strategies — all in plain, simple language.

---

## 🚀 Features

- 🧾 **User Financial Profile Extraction**: Understands user income, debt, goals, age, etc.
- 📊 **Risk & Spending Analyzer**: Uses LLM to evaluate risk tolerance, debt health, and financial behavior.
- 📈 **Smart Investment Planner**: Recommends a goal-based monthly saving target and asset allocation.
- 🧠 **Strategy Summary Generator**: Converts the plan into easy-to-understand steps and motivation.
- 🔄 **Multi-Agent Workflow**: Powered by LangGraph, modeled as a directed flow of intelligent agents.
- 🏦 **Live FD Rate Integration**: Gets real fixed deposit rates (with fallback).

---

## 🏗️ Tech Stack

- **🧠 Groq LLM** (LLaMA 3.3 70B Versatile)
- **🔗 LangGraph** (Multi-agent orchestration)
- **🧪 Flask** (Web backend)
- **🌐 HTML (Jinja)** (Frontend templating)
- **📦 dotenv** (Environment config)
- **📉 Requests + Math** (Calculations & FD rates)

---

## 🖼️ Architecture

``
          ┌────────────────────────┐
          │    User Input (Form)   │
          └────────────┬───────────┘
                       ▼
     ┌────────────────────────────────────┐
     │        LangGraph Agent Flow        │
     │                                    │
     │ 1️⃣ Financial Profile Extractor    │
     │ 2️⃣ Risk & Spending Analyzer       │
     │ 3️⃣ Investment Planner             │
     │ 4️⃣ Strategy Summary Generator     │
     └────────────────┬──────────────────┘
                      ▼
           🔁 Final JSON Response

📥 How to Use
🔧 Prerequisites
Python 3.9+

Groq API Key (set as GROQ_API_KEY in .env)

#🛠️ Setup Instructions

## 1. Clone the Repo
git clone https://github.com/yourusername/ai-finance-advisor.git
cd ai-finance-advisor

## 2. Create Virtual Environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

## 3. Install Dependencies
pip install -r requirements.txt

## 4. Add your Groq API key
echo "GROQ_API_KEY=your_groq_api_key_here" > .env

# 5. Run the App
python app.py
The app will be available at: http://localhost:5000

## 🧠 LLM Prompt Engineering
Each agent in the flow is powered by contextual prompts designed to:

Mimic financial advisor reasoning.

Break down complex strategies.

Deliver understandable and actionable content.

## 🌐 Live FD Rate Integration
The app uses https://api.bankbazaar.com/fixed-deposit/v1/fdrates to fetch real-time FD rates and gracefully falls back if unavailable.

## 💡 Use Cases
🧑‍💼 First-time investors planning goals

🧮 Salary earners aiming to save smarter

📊 Financial coaches looking for AI-powered advice generators

🏦 EdTech & FinTech startup MVPs

## 🛡️ License
MIT License

## 🤝 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.

## 📬 Connect
Made with ❤️ by [Your Name]
DM for demo, collaboration, or feedback.
