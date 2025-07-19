# personal_finance_advisor_app.py (Flask Version)

from flask import Flask, request, jsonify, render_template
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from groq import Groq
import os
import re
import requests
from dotenv import load_dotenv

# === Load environment variables ===
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=groq_api_key)

# === Flask App ===
app = Flask(__name__)

# === Utility: Parse Financial Inputs ===
def parse_financial_input(user_data):
    def extract_int(value):
        return int(re.sub(r"[^\d]", "", value)) if isinstance(value, str) else int(value)

    return {
        "goal": user_data["goal"],
        "goal_amount": extract_int(user_data["goal"]),
        "income": extract_int(user_data["income"]),
        "debt": extract_int(user_data.get("debt", 0)),
        "age": int(user_data["age"])
    }

# === Agent 1: Financial Profile Extractor ===
def financial_profile_agent(state):
    user = state["user"]
    parsed = parse_financial_input(user)
    return {"profile": parsed}

# === Agent 2: Risk & Spending Analyzer ===
def risk_analyzer_agent(state):
    profile = state["profile"]
    prompt = f"""
    Analyze the financial risk and spending behavior:

    Income: ₹{profile['income']}/month
    Debt: ₹{profile['debt']}
    Age: {profile['age']}

    Provide a short analysis including risk level (low/medium/high), whether spending is sustainable, and financial health.
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"risk_analysis": res.choices[0].message.content.strip()}

# === Fetch Real-Time FD Rates ===
def fetch_fd_rates():
    try:
        url = "https://api.bankbazaar.com/fixed-deposit/v1/fdrates"
        res = requests.get(url)
        data = res.json()
        return [
            f"{bank['bankName']}: {bank['interestRate']}%"
            for bank in data.get("bankRateList", [])[:5]
        ]
    except:
        return ["HDFC Bank: 7.1%", "SBI: 6.8%", "ICICI: 7.0%"]  # fallback

# === Agent 3: Investment Planner ===
def investment_planner_agent(state):
    profile = state["profile"]
    fd_rates = fetch_fd_rates()
    prompt = f"""
    User Profile:
    Age: {profile['age']}
    Income: ₹{profile['income']}/month
    Goal: Save ₹{profile['goal_amount']} in 5 years

    Plan an investment strategy using FDs, SIPs, stocks, and gold. Show approximate monthly saving required and asset allocation.
    Also include latest FD interest rates:
    {' | '.join(fd_rates)}
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"investment_plan": res.choices[0].message.content.strip()}

# === Agent 4: Strategy Summary ===
def strategy_summary_agent(state):
    plan = state["investment_plan"]
    risk = state["risk_analysis"]
    prompt = f"""
    Summarize the personal finance strategy below in plain English:

    Risk Analysis:
    {risk}

    Investment Plan:
    {plan}
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"summary": res.choices[0].message.content.strip()}

# === LangGraph: Multi-Agent Pipeline ===
from typing import TypedDict, Any

class FinanceState(TypedDict):
    user: dict
    profile: dict
    risk_analysis: str
    investment_plan: str
    summary: str

workflow = StateGraph(FinanceState)

workflow.add_node("profile", RunnableLambda(financial_profile_agent))
workflow.add_node("risk", RunnableLambda(risk_analyzer_agent))
workflow.add_node("invest", RunnableLambda(investment_planner_agent))
workflow.add_node("summary", RunnableLambda(strategy_summary_agent))

workflow.set_entry_point("profile")
workflow.add_edge("profile", "risk")
workflow.add_edge("risk", "invest")
workflow.add_edge("invest", "summary")
workflow.add_edge("summary", END)

app_graph = workflow.compile()

# === Web Routes ===
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_data = request.json
        result = app_graph.invoke({"user": user_data})
        return jsonify(result)
    return render_template("index.html")

# === Run Server ===
if __name__ == "__main__":
    app.run(debug=True)

