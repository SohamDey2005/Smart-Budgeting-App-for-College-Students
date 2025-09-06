import streamlit as st
import matplotlib.pyplot as plt
import google.generativeai as genai
import os
import pandas as pd
import datetime

# -------------------------------
# Gemini Configuration
# -------------------------------
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-1.5-flash")
else:
    model = None

def get_ai_tips(expenses, budget, remaining, goal, mode):
    prompt = f"""
    You are a financial advisor for COLLEGE STUDENTS.

    Mode: {mode}
    Expenses breakdown: ₹{expenses}
    Budget: ₹{budget}
    Remaining: ₹{remaining}
    Savings Goal: ₹{goal}

    Provide 6 personalized student-focused budgeting tips.
    - If monthly: focus on food, outings, daily savings.
    - If semester: focus on tuition fees, hostel, trips, exams, and long-term planning.
    Keep them simple and actionable. Use proper fonts.
    """
    response = model.generate_content(prompt)
    return response.text

# -------------------------------
# Streamlit App
# -------------------------------
st.set_page_config(page_title="🎓 Student Budgeting App", layout="wide")

st.title("🎓 Smart Budgeting App for College Students")
st.caption("Plan monthly OR semester budgets, track expenses, visualize data, and get AI tips!")

# -------------------------------
# Selection of Mode
# -------------------------------
mode = st.radio("📅 Choose mode:", ["Monthly Budgeting", "Semester Budgeting"])

# -------------------------------
# Categories
# -------------------------------
if mode == "Monthly Budgeting":
    # Monthly Budgeting
    budget = st.number_input("💸 Monthly Budget (₹):", min_value=0, step=500)
    goal = st.number_input("🎯 Monthly Savings Goal (₹):", min_value=0, step=500)

    categories = {
        "🍔 Food": "Daily meals, snacks, canteen",
        "🚌 Transport": "Bus, train, Uber, bike fuel",
        "🏠 Rent/Hostel": "Hostel fee or PG rent",
        "✏️ Study Materials": "Books, stationery, software",
        "📱 Internet/Phone": "Mobile data, WiFi, recharge",
        "🎬 Entertainment & Outings": "Movies, hangouts, trips",
        "🏥 Health & Fitness": "Medicines, doctor visits, gym",
        "🎭 Clubs/Events": "Societies, fests, competitions",
        "📦 Others": "Miscellaneous expenses",
    }

else:  
    # Semester Budgeting
    budget = st.number_input("💸 Semester Budget (₹):", min_value=0, step=1000)
    goal = st.number_input("🎯 Semester Savings Goal (₹):", min_value=0, step=1000)

    categories = {
        "📚 Tuition Fees": "College or semester fees",
        "🏠 Hostel/PG Rent": "Semester-long rent or hostel fee",
        "✏️ Study Materials": "Books, notes, stationery, software",
        "🚌 Transport": "Travel home, trips, daily commute",
        "🎭 College Events/Fests": "Cultural fest, tech fest, competitions",
        "🎒 Trips & Excursions": "Industrial visit, college trip",
        "🏥 Health & Insurance": "Medicines, hospital, insurance",
        "📱 Internet & Utilities": "WiFi, mobile recharge, electricity",
        "🍔 Food & Daily Expenses": "Canteen, groceries, mess",
        "📦 Others": "Miscellaneous semester expenses",
    }

# -------------------------------
# Input Expenses 
# -------------------------------
st.subheader("📝 Add Your Expenses")
expenses = {}
for cat, desc in categories.items():
    with st.expander(f"{cat} - {desc}"):
        amount = st.number_input(f"Enter amount for {cat} (₹):", min_value=0, step=500, key=cat+mode)
        expenses[cat] = amount

total_expenses = sum(expenses.values())
remaining = budget - total_expenses

# -------------------------------
# Budget Summary
# -------------------------------
st.subheader("📊 Budget Summary")
col1, col2, col3 = st.columns(3)
col1.metric("💸 Budget", f"₹{budget}")
col2.metric("📉 Expenses", f"₹{total_expenses}")
col3.metric("✅ Remaining", f"₹{remaining}")

# -------------------------------
# Mode-Specific Insights
# -------------------------------
if mode == "Monthly Budgeting" and budget > 0:
    daily_budget = budget / 30
    st.info(f"📆 Your daily spending allowance: ₹{daily_budget:.2f}")
elif mode == "Semester Budgeting" and budget > 0:
    months = 6
    monthly_equiv = budget / months
    st.info(f"📆 Equivalent Monthly Budget: ₹{monthly_equiv:.2f}")

# -------------------------------
# Warnings
# -------------------------------
if remaining < 0:
    st.error("⚠️ You exceeded your budget!")
elif remaining < budget * 0.2:
    st.warning("⚠️ You are close to exceeding your budget.")
else:
    st.success("✅ You're on track!")

# -------------------------------
# Visualization
# -------------------------------
st.subheader("📈 Expense Distribution")
if total_expenses > 0:
    fig, ax = plt.subplots()
    ax.pie(expenses.values(), labels=expenses.keys(), autopct='%1.1f%%')
    st.pyplot(fig)

# -------------------------------
# Bar Chart
# -------------------------------
st.subheader("📊 Budget vs Expenses")
df = pd.DataFrame({
    "Category": list(expenses.keys()),
    "Expenses": list(expenses.values())
})
df.loc[len(df)] = ["Remaining", remaining]
st.bar_chart(df.set_index("Category"))

# -------------------------------
# Expense Tracker
# -------------------------------
st.subheader("🗂 Expense Log")
if "history" not in st.session_state:
    st.session_state["history"] = []

if st.button("💾 Save this budget data"):
    st.session_state["history"].append({
        "Date": datetime.date.today(),
        "Mode": mode,
        "Budget": budget,
        "Expenses": total_expenses,
        "Remaining": remaining,
        "Goal": goal
    })

if len(st.session_state["history"]) > 0:
    history_df = pd.DataFrame(st.session_state["history"])
    st.write(history_df[["Date", "Mode", "Budget", "Expenses", "Remaining", "Goal"]])

    # Download option
    csv = history_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Expense History (CSV)", csv, "expenses.csv", "text/csv")

# -------------------------------
# AI Tips
# -------------------------------
st.subheader("🤖 AI-Powered Smart Tips")
if st.button("✨ Get AI Tips"):
    try:
        tips = get_ai_tips(expenses, budget, remaining, goal, mode)
        st.success(tips)
    except Exception as e:
        st.warning("⚠️ Unable to fetch AI tips. Please check your Gemini API key.")
        st.error(str(e))
st.markdown("---")
st.caption("⚡ Powered by **Google Gemini AI** + **Streamlit**")
st.caption("👨‍💻 Developed by **Soham Dey**")