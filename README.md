# Commercial Loan Risk Scoring

A small Python project that scores commercial loan applications using a transparent, rules-based model. It is designed as a portfolio project for GitHub: simple to run, easy to test, and clear about the financial assumptions behind the score.

> This is an educational baseline model, not production credit policy or financial advice.

## What It Does

The model returns a risk score from `0` to `100`, where higher scores mean higher estimated credit risk. It uses common commercial lending signals:

- Debt service coverage ratio (`dscr`)
- Loan-to-value ratio (`ltv`)
- Business credit score
- Years in business
- Liquidity ratio
- Net profit margin
- Payment delinquencies in the last 24 months
- Industry risk level

Each feature is converted into a normalized risk contribution, multiplied by a weight, and mapped to a simple rating band.

## Risk Bands

| Score | Rating | Meaning |
| --- | --- | --- |
| 0-19 | A | Low risk |
| 20-39 | B | Moderate-low risk |
| 40-59 | C | Moderate risk |
| 60-79 | D | Elevated risk |
| 80-100 | E | High risk |

## Project Structure

```text
commercial-loan-risk-scoring/
├── data/
│   └── sample_loans.csv
├── src/
│   └── loan_risk/
│       ├── __init__.py
│       ├── cli.py
│       └── model.py
├── tests/
│   └── test_model.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e .
python -m unittest discover -s tests
loan-risk-score data/sample_loans.csv
```

On macOS or Linux, activate the environment with:

```bash
source .venv/bin/activate
```

You can also run the CLI without installing the console script:

```bash
python -m loan_risk.cli data/sample_loans.csv --output scored_loans.csv
```

## Example Output

```text
application_id  risk_score  risk_rating  decision
CL-1001         14.8        A            approve
CL-1002         54.0        C            review
CL-1003         83.5        E            decline
```

## CSV Input Format

Required columns:

```text
application_id,dscr,ltv,business_credit_score,years_in_business,liquidity_ratio,net_profit_margin,delinquencies_24m,industry_risk
```

`industry_risk` must be one of:

- `low`
- `medium`
- `high`

## Model Assumptions

The scoring logic favors borrowers with stronger cash flow coverage, lower collateral leverage, longer operating history, stronger liquidity, positive margins, and clean payment history. The weights are intentionally visible in `src/loan_risk/model.py` so they can be adjusted or replaced with a trained model later.

## Possible Improvements

- Calibrate weights against historical default data
- Add explainability charts or reason codes
- Introduce borrower sector and geography features
- Compare the rules-based baseline with logistic regression or gradient boosting
- Add fairness and stability checks before any production use
