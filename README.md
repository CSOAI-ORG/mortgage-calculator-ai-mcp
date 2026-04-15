# Mortgage Calculator AI

> By [MEOK AI Labs](https://meok.ai) — Calculate mortgage payments, compare rates, generate amortization schedules, and check affordability

## Installation

```bash
pip install mortgage-calculator-ai-mcp
```

## Usage

```bash
python server.py
```

## Tools

### `calculate_mortgage`
Calculate monthly mortgage payment with optional down payment.

**Parameters:**
- `principal` (float): Home price
- `rate` (float): Annual interest rate percentage (e.g. 6.5)
- `years` (int): Loan term in years
- `down_payment` (float): Down payment amount (default: 0)

### `compare_rates`
Compare monthly payments across multiple interest rates side by side.

**Parameters:**
- `principal` (float): Home price
- `years` (int): Loan term
- `rates` (list[float]): Interest rates to compare
- `down_payment` (float): Down payment (default: 0)

### `amortization_schedule`
Generate a yearly amortization schedule showing principal vs interest breakdown and equity growth.

**Parameters:**
- `principal` (float): Home price
- `rate` (float): Annual rate
- `years` (int): Loan term
- `down_payment` (float): Down payment (default: 0)

### `affordability_check`
Estimate maximum affordable home price based on income and debts using the 28/36 DTI rule.

**Parameters:**
- `annual_income` (float): Annual gross income
- `monthly_debts` (float): Existing monthly debt payments (default: 0)
- `rate` (float): Assumed interest rate (default: 6.5)
- `years` (int): Loan term (default: 30)
- `down_payment` (float): Available down payment (default: 0)

## Authentication

Free tier: 15 calls/day. Upgrade at [meok.ai/pricing](https://meok.ai/pricing) for unlimited access.

## License

MIT — MEOK AI Labs
