import streamlit as st
import re

from financial_engine import (
    simulate_spending,
    financial_status,
    analyze_balance,
    compare_spending,
    simulate_salary_delay
)

from ai_engine import ask_ai
from bank_data import customers


# -----------------------------
# PAGE SETTINGS
# -----------------------------

st.set_page_config(
    page_title="Banking Mirror",
    page_icon="🪞",
    layout="wide"
)


# -----------------------------
# DEMO LOGIN DETAILS
# -----------------------------

# Simple demo PINs for the prototype.
# In a real banking system these would NOT be stored like this.

customer_pins = {}

for i, name in enumerate(customers.keys()):
    customer_pins[name] = str(1234 + i)


# -----------------------------
# LOGIN
# -----------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "logged_customer" not in st.session_state:
    st.session_state.logged_customer = None


if not st.session_state.logged_in:

    st.title("🪞 BANKING MIRROR")
    st.caption("See the impact before you decide.")

    st.divider()

    st.subheader("🔐 Customer Login")

    selected_customer = st.selectbox(
        "Select Customer",
        list(customers.keys())
    )

    pin = st.text_input(
        "Enter 4-digit PIN",
        type="password",
        max_chars=4
    )

    if st.button("Login", type="primary"):

        if pin == customer_pins[selected_customer]:

            st.session_state.logged_in = True
            st.session_state.logged_customer = selected_customer

            st.rerun()

        else:

            st.error("Incorrect PIN. Please try again.")

    st.info(
        "Demo prototype: Each customer has a separate demo PIN."
    )

    # Show the PIN for the currently selected customer
    # only for hackathon demonstration.
    st.caption(
        f"Demo PIN for {selected_customer}: "
        f"{customer_pins[selected_customer]}"
    )

    st.stop()


# -----------------------------
# LOAD ONLY LOGGED-IN CUSTOMER
# -----------------------------

selected_name = st.session_state.logged_customer

customer_data = customers[selected_name]


# -----------------------------
# HEADER
# -----------------------------

st.title("🪞 BANKING MIRROR")
st.caption("See the impact before you decide.")

st.success(
    f"🔐 Logged in as {customer_data['name']}"
)

if st.button("Logout"):

    st.session_state.logged_in = False
    st.session_state.logged_customer = None

    st.rerun()


st.divider()


# -----------------------------
# CUSTOMER ACCOUNT
# -----------------------------

st.subheader("🏦 Customer Account")

c1, c2, c3 = st.columns(3)

c1.write(
    f"**Name:** {customer_data['name']}"
)

c2.write(
    f"**Bank:** {customer_data['bank']}"
)

c3.write(
    f"**Account:** {customer_data['account_number']}"
)


st.divider()


# -----------------------------
# FINANCIAL SNAPSHOT
# -----------------------------

st.subheader("📊 Financial Snapshot")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Current Balance",
    f"₹{customer_data['balance']:,}"
)

c2.metric(
    "Monthly Salary",
    f"₹{customer_data['salary']:,}"
)

c3.metric(
    "Upcoming EMI",
    f"₹{customer_data['emi']:,}"
)

c4.metric(
    "Upcoming Bills",
    f"₹{customer_data['upcoming_bills']:,}"
)


st.divider()


# -----------------------------
# TRANSACTIONS
# -----------------------------

with st.expander("📋 View Recent Transactions"):

    for transaction in customer_data["transactions"]:

        st.write(
            f"**{transaction['name']}** — "
            f"₹{transaction['amount']:,} "
            f"({transaction['category']})"
        )


st.divider()


# -----------------------------
# CHATBOT
# -----------------------------

st.header("💬 Ask Banking Mirror")

question = st.chat_input(
    f"Ask anything about {customer_data['name']}'s finances..."
)


if question:

    st.chat_message("user").write(question)

    q = question.lower()

    # Only the logged-in customer's data is sent
    # to the financial engine and AI.
    banking_context = {

        "customer": customer_data,

        "transactions":
            customer_data["transactions"]
    }


    # -----------------------------
    # EXTRACT NUMBERS
    # -----------------------------

    numbers = [
        int(x.replace(",", ""))
        for x in re.findall(
            r"\d[\d,]*",
            question
        )
    ]


    # -----------------------------
    # SPENDING / AFFORDABILITY
    # -----------------------------

    if numbers and any(
        word in q
        for word in [
            "spend",
            "buy",
            "purchase",
            "afford",
            "pay",
            "cost"
        ]
    ):

        amount = numbers[0]

        result = simulate_spending(
            amount,
            customer_data
        )

        banking_context["simulation"] = result

        banking_context["status"] = financial_status(
            result["projected_balance"]
        )


        # Decision card
        st.subheader("🪞 Financial Decision")

        d1, d2, d3, d4 = st.columns(4)

        d1.metric(
            "Current Balance",
            f"₹{customer_data['balance']:,}"
        )

        d2.metric(
            "Planned Spending",
            f"₹{amount:,}"
        )

        d3.metric(
            "EMI + Bills",
            f"₹{customer_data['emi'] + customer_data['upcoming_bills']:,}"
        )

        d4.metric(
            "Projected Balance",
            f"₹{result['projected_balance']:,}"
        )

        status = financial_status(
            result["projected_balance"]
        )

        if status == "SAFE":
            st.success("🟢 SAFE — The projected balance is above ₹20,000.")

        elif status == "CAUTION":
            st.warning("🟡 CAUTION — The projected balance is getting low.")

        else:
            st.error("🔴 RISK — The projected balance is very low.")


    # -----------------------------
    # COMPARISON
    # -----------------------------

    elif (
        len(numbers) >= 2
        and (
            "compare" in q
            or "versus" in q
            or "vs" in q
            or "options" in q
            or "which" in q
        )
    ):

        banking_context["comparison"] = compare_spending(
            numbers,
            customer_data
        )


    # -----------------------------
    # SALARY DELAY
    # -----------------------------

    elif (
        "salary" in q
        and (
            "delay" in q
            or "late" in q
            or "delayed" in q
        )
        and numbers
    ):

        banking_context["salary_delay"] = simulate_salary_delay(
            numbers[0],
            customer_data
        )


    # -----------------------------
    # BALANCE / SPENDING ANALYSIS
    # -----------------------------

    elif (
        "why" in q
        or "where did my money go" in q
        or "where is my money" in q
        or "spending" in q
        or "expenses" in q
        or "expense" in q
    ):

        banking_context["balance_analysis"] = analyze_balance(
            customer_data
        )


    # -----------------------------
    # AI RESPONSE
    # -----------------------------

    with st.spinner(
        "🪞 Banking Mirror is analyzing..."
    ):

        answer = ask_ai(
            question,
            banking_context
        )

    st.chat_message(
        "assistant"
    ).markdown(answer)
