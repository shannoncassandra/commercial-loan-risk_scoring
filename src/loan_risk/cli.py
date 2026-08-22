"""Command line interface for scoring commercial loan applications."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from loan_risk.model import LoanApplication, score_application


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score commercial loan applications from a CSV file."
    )
    parser.add_argument("input_csv", type=Path, help="Path to input loan CSV")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("scored_loans.csv"),
        help="Path for scored CSV output",
    )
    args = parser.parse_args()

    results = score_csv(args.input_csv, args.output)
    print(f"Scored {len(results)} applications -> {args.output}")


def score_csv(input_csv: Path, output_csv: Path) -> list[dict[str, str]]:
    """Score each row in a loan CSV and write a result CSV."""

    with input_csv.open(newline="", encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))

    scored_rows = []
    for row in rows:
        application = _application_from_row(row)
        result = score_application(application)
        scored_rows.append(
            {
                **row,
                "risk_score": f"{result.risk_score:.1f}",
                "risk_rating": result.risk_rating,
                "decision": result.decision,
                "reason_codes": "; ".join(result.reason_codes),
            }
        )

    if not scored_rows:
        raise ValueError("input CSV contains no application rows")

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=list(scored_rows[0].keys()))
        writer.writeheader()
        writer.writerows(scored_rows)

    return scored_rows


def _application_from_row(row: dict[str, str]) -> LoanApplication:
    return LoanApplication(
        application_id=row["application_id"],
        dscr=float(row["dscr"]),
        ltv=float(row["ltv"]),
        business_credit_score=int(row["business_credit_score"]),
        years_in_business=float(row["years_in_business"]),
        liquidity_ratio=float(row["liquidity_ratio"]),
        net_profit_margin=float(row["net_profit_margin"]),
        delinquencies_24m=int(row["delinquencies_24m"]),
        industry_risk=row["industry_risk"],
    )


if __name__ == "__main__":
    main()
