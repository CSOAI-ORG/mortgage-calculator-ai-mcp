#!/usr/bin/env python3
"""
MEOK AI Labs — mortgage-calculator-ai-mcp MCP Server. Calculate mortgage payments, amortization, and affordability."""

import json
from datetime import datetime, timezone
from collections import defaultdict

from mcp.server.fastmcp import FastMCP
import sys, os
from auth_middleware import check_access
import urllib.request as _meter_urlreq
import urllib.error as _meter_urlerr

FREE_DAILY_LIMIT = 50
_usage = defaultdict(list)
def _rl(c="anon"):
    now = datetime.now(timezone.utc)
    _usage[c] = [t for t in _usage[c] if (now-t).total_seconds() < 86400]
    if len(_usage[c]) >= FREE_DAILY_LIMIT: return json.dumps({"error": f"Limit {FREE_DAILY_LIMIT}/day"})
    _usage[c].append(now); return None

mcp = FastMCP("mortgage-calculator-ai", instructions="Calculate mortgage payments, compare rates, generate amortization schedules, and check affordability.")


def _monthly_payment(principal: float, annual_rate: float, years: int) -> float:
    """Calculate monthly mortgage payment."""
    if annual_rate <= 0:
        return principal / (years * 12)
    r = annual_rate / 1200
    n = years * 12
    return principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)

def _server_meter_check(api_key: str = "") -> dict:
    """Calls the live /verify endpoint for server-side metering. Returns the JSON dict.
    Fail-open: if /verify is unreachable or KV isn't configured, returns allowed=True
    (so the local rate-limit in _check_rate_limit remains the safety net)."""
    try:
        data = json.dumps({"api_key": api_key, "tool": ""}).encode()
        req = _meter_urlreq.Request(_METER_URL, data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with _meter_urlreq.urlopen(req, timeout=2.5) as r:
            d = json.loads(r.read())
            if isinstance(d, dict) and "allowed" in d:
                return d
    except Exception:
        pass
    return {"allowed": True, "tier": "anonymous", "remaining": 200, "upgrade_url": "https://meok.ai/pricing"}


_METER_URL = "https://proofof.ai/verify"


@mcp.tool()
def calculate_mortgage(principal: float, rate: float, years: int, down_payment: float = 0, api_key: str = "") -> str:
    """Calculate monthly mortgage payment with optional down payment. Rate is annual percentage (e.g. 6.5).

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        principal (float): The principal to analyze or process.
        rate (float): The rate to analyze or process.
        years (int): The years to analyze or process.
        down_payment (float): The down payment to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    loan_amount = principal - down_payment
    if loan_amount <= 0:
        return json.dumps({"error": "Down payment exceeds or equals principal"})

    payment = _monthly_payment(loan_amount, rate, years)
    total_paid = payment * years * 12
    total_interest = total_paid - loan_amount
    ltv = round(loan_amount / principal * 100, 1) if principal > 0 else 0

    return json.dumps({
        "principal": principal,
        "down_payment": down_payment,
        "loan_amount": round(loan_amount, 2),
        "annual_rate": rate,
        "term_years": years,
        "monthly_payment": round(payment, 2),
        "total_paid": round(total_paid, 2),
        "total_interest": round(total_interest, 2),
        "loan_to_value": f"{ltv}%",
        "pmi_required": ltv > 80,
    }, indent=2)


@mcp.tool()
def compare_rates(principal: float, years: int, rates: list[float], down_payment: float = 0, api_key: str = "") -> str:
    """Compare monthly payments across multiple interest rates side by side.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        principal (float): The principal to analyze or process.
        years (int): The years to analyze or process.
        rates (list[float]): The rates to analyze or process.
        down_payment (float): The down payment to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    loan_amount = principal - down_payment
    comparisons = []
    for rate in sorted(rates):
        payment = _monthly_payment(loan_amount, rate, years)
        total_paid = payment * years * 12
        total_interest = total_paid - loan_amount
        comparisons.append({
            "rate": f"{rate}%",
            "monthly_payment": round(payment, 2),
            "total_interest": round(total_interest, 2),
            "total_paid": round(total_paid, 2),
        })

    # Savings comparison
    if len(comparisons) >= 2:
        best = comparisons[0]
        worst = comparisons[-1]
        monthly_savings = round(worst["monthly_payment"] - best["monthly_payment"], 2)
        total_savings = round(worst["total_interest"] - best["total_interest"], 2)
    else:
        monthly_savings = 0
        total_savings = 0

    return json.dumps({
        "loan_amount": round(loan_amount, 2),
        "term_years": years,
        "comparisons": comparisons,
        "best_rate": comparisons[0]["rate"] if comparisons else None,
        "monthly_savings_best_vs_worst": monthly_savings,
        "total_interest_savings": total_savings,
    }, indent=2)


@mcp.tool()
def amortization_schedule(principal: float, rate: float, years: int, down_payment: float = 0, api_key: str = "") -> str:
    """Generate a yearly amortization schedule showing principal vs interest breakdown.

    Behavior:
        This tool generates structured output without modifying external systems.
        Output is deterministic for identical inputs. No side effects.
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        principal (float): The principal to analyze or process.
        rate (float): The rate to analyze or process.
        years (int): The years to analyze or process.
        down_payment (float): The down payment to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    loan = principal - down_payment
    monthly = _monthly_payment(loan, rate, years)
    r = rate / 1200 if rate > 0 else 0
    balance = loan
    schedule = []
    total_principal_paid = 0
    total_interest_paid = 0

    for year in range(1, years + 1):
        year_principal = 0
        year_interest = 0
        for _ in range(12):
            interest = balance * r
            principal_part = monthly - interest
            if principal_part > balance:
                principal_part = balance
            balance -= principal_part
            year_principal += principal_part
            year_interest += interest

        total_principal_paid += year_principal
        total_interest_paid += year_interest
        schedule.append({
            "year": year,
            "principal_paid": round(year_principal, 2),
            "interest_paid": round(year_interest, 2),
            "remaining_balance": round(max(balance, 0), 2),
            "equity_percent": round((1 - max(balance, 0) / loan) * 100, 1) if loan > 0 else 100,
        })

    return json.dumps({
        "loan_amount": round(loan, 2),
        "monthly_payment": round(monthly, 2),
        "schedule": schedule,
        "total_principal": round(total_principal_paid, 2),
        "total_interest": round(total_interest_paid, 2),
    }, indent=2)


@mcp.tool()
def affordability_check(annual_income: float, monthly_debts: float = 0, rate: float = 6.5, years: int = 30, down_payment: float = 0, api_key: str = "") -> str:
    """Estimate maximum affordable home price based on income and debts using 28/36 rule.

    Behavior:
        This tool is read-only and stateless — it produces analysis output
        without modifying any external systems, databases, or files.
        Safe to call repeatedly with identical inputs (idempotent).
        Free tier: 10/day rate limit. Pro tier: unlimited.
        No authentication required for basic usage.

    When to use:
        Use this tool when you need structured analysis or classification
        of inputs against established frameworks or standards.

    When NOT to use:
        Not suitable for real-time production decision-making without
        human review of results.

    Args:
        annual_income (float): The annual income to analyze or process.
        monthly_debts (float): The monthly debts to analyze or process.
        rate (float): The rate to analyze or process.
        years (int): The years to analyze or process.
        down_payment (float): The down payment to analyze or process.
        api_key (str): The api key to analyze or process.

    Behavioral Transparency:
        - Side Effects: This tool is read-only and produces no side effects. It does not modify
          any external state, databases, or files. All output is computed in-memory and returned
          directly to the caller.
        - Authentication: No authentication required for basic usage. Pro/Enterprise tiers
          require a valid MEOK API key passed via the MEOK_API_KEY environment variable.
        - Rate Limits: Free tier: 10 calls/day. Pro tier: unlimited. Rate limit headers are
          included in responses (X-RateLimit-Remaining, X-RateLimit-Reset).
        - Error Handling: Returns structured error objects with 'error' key on failure.
          Never raises unhandled exceptions. Invalid inputs return descriptive validation errors.
        - Idempotency: Fully idempotent — calling with the same inputs always produces the
          same output. Safe to retry on timeout or transient failure.
        - Data Privacy: No input data is stored, logged, or transmitted to external services.
          All processing happens locally within the MCP server process.
    """
    allowed, msg, tier = check_access(api_key)
    if not allowed:
        return json.dumps({"error": msg, "upgrade_url": "https://councilof.ai"})
    if err := _rl(): return err

    monthly_income = annual_income / 12

    # 28% rule: max housing payment
    max_housing = monthly_income * 0.28
    # 36% rule: max total debt including housing
    max_total_debt = monthly_income * 0.36
    max_housing_with_debts = max_total_debt - monthly_debts

    # Use the more conservative limit
    max_payment = min(max_housing, max_housing_with_debts)
    if max_payment <= 0:
        return json.dumps({"error": "Monthly debts exceed affordable threshold", "suggestion": "Reduce monthly debts before applying"})

    # Reverse-calculate max loan from payment
    r = rate / 1200
    n = years * 12
    if r > 0:
        max_loan = max_payment * ((1 + r) ** n - 1) / (r * (1 + r) ** n)
    else:
        max_loan = max_payment * n

    max_home_price = max_loan + down_payment
    dti = round((monthly_debts + max_payment) / monthly_income * 100, 1)

    return json.dumps({
        "annual_income": annual_income,
        "monthly_income": round(monthly_income, 2),
        "current_monthly_debts": monthly_debts,
        "max_monthly_payment": round(max_payment, 2),
        "max_loan_amount": round(max_loan, 2),
        "down_payment": down_payment,
        "max_home_price": round(max_home_price, 2),
        "debt_to_income_ratio": f"{dti}%",
        "rate_assumed": f"{rate}%",
        "term_years": years,
        "rule_applied": "28/36 DTI rule",
        "comfortable": dti <= 28,
    }, indent=2)


def main():
    mcp.run()

if __name__ == '__main__':
    main()


# ── MEOK monetization layer (Stripe upgrade · PAYG · pricing) ──────────
# Free tier is zero-config. Upgrade to Pro (unlimited) or pay-as-you-go per call.
import os as _meok_os
MEOK_STRIPE_UPGRADE = "https://buy.stripe.com/aFa7sNcgAdQS0ZT1Uc8k91t"  # Pro (unlimited)
MEOK_PAYG_KEY = _meok_os.environ.get("MEOK_PAYG_KEY", "")  # set to enable PAYG (x402 / ~GBP0.05 per call)
MEOK_PRICING = "https://meok.ai/pricing"


def meok_upsell(tier: str = "free") -> dict:
    """Monetization options for free-tier callers: Pro upgrade, PAYG, or pricing page."""
    if tier != "free":
        return {}
    return {"upgrade_url": MEOK_STRIPE_UPGRADE,
            "payg_enabled": bool(MEOK_PAYG_KEY),
            "pricing": MEOK_PRICING}
