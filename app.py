from flask import Flask, request, jsonify, render_template
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from groq import Groq
import os
import re
import requests
import math
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
        "age": int(user_data["age"]),
        "time_horizon_years": int(user_data.get("time_horizon_years", 5)),  # optional input
        "risk_tolerance": user_data.get("risk_tolerance", "medium")  # optional input
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
    Analyze the user's financial situation:

    Income: ₹{profile['income']}/month
    Debt: ₹{profile['debt']}
    Age: {profile['age']}
    Risk Tolerance: {profile['risk_tolerance']}

    Provide:
    - Risk tolerance (low/medium/high)
    - Debt health
    - Spending sustainability
    - Financial behavior insights
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"risk_analysis": res.choices[0].message.content.strip()}

# === FD Rates API Fallback ===
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
        return ["HDFC: 7.1%", "SBI: 6.8%", "ICICI: 7.0%"]

# === Agent 3: Investment Planner (Dynamic & Smart) ===
def investment_planner_agent(state):
    profile = state["profile"]
    income = profile["income"]
    goal = profile["goal_amount"]
    age = profile["age"]
    debt = profile["debt"]
    years = profile.get("time_horizon_years", 5)
    months = years * 12
    rate = 0.10 / 12  # assume 10% annual return, monthly compounding

    try:
        monthly_saving = goal * rate / (math.pow(1 + rate, months) - 1)
        monthly_saving = round(monthly_saving, 2)
    except:
        monthly_saving = round(goal / months, 2)

    # Affordability Analysis
    if monthly_saving > income:
        affordability_note = f"⚠️ To reach ₹{goal} in {years} years, you'd need to save ₹{monthly_saving}/month — which exceeds your monthly income of ₹{income}."
        suggestion = "Consider extending your timeline or reducing your goal."
    else:
        affordability_note = f"✅ You need to save approximately ₹{monthly_saving}/month to reach ₹{goal} in {years} years."
        suggestion = "This is feasible with your current income."

    # Smart Allocation Prompt (Dynamic)
    prompt = f"""
    Given the following user profile, generate a personalized investment allocation:

    Age: {age}
    Monthly Income: ₹{income}
    Current Debt: ₹{debt}
    Financial Goal: ₹{goal} in {years} years
    Risk Tolerance: {profile['risk_tolerance']}
    Monthly Saving Target: ₹{monthly_saving}

    Recommend a dynamic allocation across:
    - Equity SIPs (mutual funds)
    - Fixed Deposits
    - Gold
    - Emergency Fund

    Format:
    - Bullet points with percentages
    - 1-2 line explanation per choice
    - Optional tax-saving ideas
    - No generic advice — make it tailored
    """

    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )

    fd_rates = fetch_fd_rates()

    return {
        "investment_plan": f"""
{affordability_note}
{suggestion}

{res.choices[0].message.content.strip()}

🪙 Latest FD Rates:
{' | '.join(fd_rates)}
"""
    }

# === Agent 4: Strategy Summary Generator ===
def strategy_summary_agent(state):
    plan = state["investment_plan"]
    risk = state["risk_analysis"]
    prompt = f"""
    Summarize the following strategy for a non-financial user in simple language.

    Risk Analysis:
    {risk}

    Investment Plan:
    {plan}

    Provide a motivating conclusion and main action items.
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return {"summary": res.choices[0].message.content.strip()}

# === LangGraph Workflow Setup ===
from typing import TypedDict

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

# === Flask Routes ===
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_data = request.json
        result = app_graph.invoke({"user": user_data})
        return jsonify(result)
    return render_template("index.html")

# === Run the App ===
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
