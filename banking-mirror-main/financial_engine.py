def simulate_spending(amount, customer_data):

    balance = customer_data["balance"]
    emi = customer_data["emi"]
    bills = customer_data["upcoming_bills"]

    projected_balance = balance - amount - emi - bills

    return {
        "current_balance": balance,
        "spending": amount,
        "emi": emi,
        "bills": bills,
        "projected_balance": projected_balance
    }


def financial_status(balance):

    if balance >= 20000:
        return "SAFE"

    elif balance >= 10000:
        return "CAUTION"

    else:
        return "RISK"


def analyze_balance(customer_data):

    transactions = customer_data["transactions"]

    total_spending = sum(
        t["amount"] for t in transactions
    )

    category_totals = {}

    for t in transactions:

        category = t["category"]

        if category not in category_totals:
            category_totals[category] = 0

        category_totals[category] += t["amount"]

    largest_category = max(
        category_totals,
        key=category_totals.get
    )

    largest_transaction = max(
        transactions,
        key=lambda x: x["amount"]
    )

    return {
        "current_balance": customer_data["balance"],
        "total_spending": total_spending,
        "category_totals": category_totals,
        "largest_category": largest_category,
        "largest_transaction": largest_transaction
    }


def compare_spending(amounts, customer_data):

    results = []

    for amount in amounts:

        result = simulate_spending(
            amount,
            customer_data
        )

        results.append({
            "spending": amount,
            "projected_balance":
                result["projected_balance"],

            "status":
                financial_status(
                    result["projected_balance"]
                )
        })

    return results


def simulate_salary_delay(days, customer_data):

    monthly_salary = customer_data["salary"]

    daily_salary = monthly_salary / 30

    delayed_amount = daily_salary * days

    projected_balance = (
        customer_data["balance"]
        - delayed_amount
    )

    status = financial_status(
        projected_balance
    )

    return {
        "salary": monthly_salary,
        "delay_days": days,
        "estimated_delayed_amount":
            round(delayed_amount),

        "projected_balance":
            round(projected_balance),

        "status": status
    }