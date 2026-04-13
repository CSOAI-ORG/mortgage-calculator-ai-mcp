from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mortgage-calculator")

@mcp.tool()
def calculate_monthly_payment(principal: float, annual_rate: float, years: int) -> dict:
    """Calculate monthly mortgage payment."""
    monthly_rate = annual_rate / 100 / 12
    n = years * 12
    if monthly_rate == 0:
        payment = principal / n
    else:
        payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    total_cost = payment * n
    total_interest = total_cost - principal
    return {
        "monthly_payment": round(payment, 2),
        "total_payments": n,
        "total_interest": round(total_interest, 2),
        "total_cost": round(total_cost, 2),
    }

@mcp.tool()
def generate_amortization_schedule(principal: float, annual_rate: float, years: int) -> dict:
    """Generate amortization schedule."""
    monthly_rate = annual_rate / 100 / 12
    n = years * 12
    if monthly_rate == 0:
        payment = principal / n
    else:
        payment = principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)
    schedule = []
    balance = principal
    for year in range(1, years + 1):
        yearly_interest = 0.0
        yearly_principal = 0.0
        for _ in range(12):
            if balance <= 0:
                break
            interest = balance * monthly_rate
            p = payment - interest
            balance -= p
            yearly_interest += interest
            yearly_principal += p
        schedule.append({
            "year": year,
            "interest_paid": round(yearly_interest, 2),
            "principal_paid": round(yearly_principal, 2),
            "remaining_balance": round(max(balance, 0), 2),
        })
    return {"monthly_payment": round(payment, 2), "schedule": schedule}

@mcp.tool()
def compare_mortgages(a: dict, b: dict) -> dict:
    """Compare two mortgage options."""
    res_a = calculate_monthly_payment(a["principal"], a["annual_rate"], a["years"])
    res_b = calculate_monthly_payment(b["principal"], b["annual_rate"], b["years"])
    return {
        "mortgage_a": res_a,
        "mortgage_b": res_b,
        "monthly_savings": round(res_a["monthly_payment"] - res_b["monthly_payment"], 2),
        "interest_savings": round(res_a["total_interest"] - res_b["total_interest"], 2),
    }

def main():
    mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
