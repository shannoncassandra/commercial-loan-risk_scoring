"""Transparent baseline model for commercial loan risk scoring."""

from __future__ import annotations

from dataclasses import dataclass


INDUSTRY_RISK_MAP = {
    "low": 0.15,
    "medium": 0.50,
    "high": 0.85,
}

FEATURE_WEIGHTS = {
    "dscr": 0.24,
    "ltv": 0.18,
    "business_credit_score": 0.17,
    "years_in_business": 0.10,
    "liquidity_ratio": 0.10,
    "net_profit_margin": 0.08,
    "delinquencies_24m": 0.08,
    "industry_risk": 0.05,
}


@dataclass(frozen=True)
class LoanApplication:
    """Inputs used to score one commercial loan application."""

    application_id: str
    dscr: float
    ltv: float
    business_credit_score: int
    years_in_business: float
    liquidity_ratio: float
    net_profit_margin: float
    delinquencies_24m: int
    industry_risk: str


@dataclass(frozen=True)
class RiskResult:
    """Model output for a scored application."""

    application_id: str
    risk_score: float
    risk_rating: str
    decision: str
    reason_codes: tuple[str, ...]


def score_application(application: LoanApplication) -> RiskResult:
    """Score a commercial loan application on a 0-100 risk scale."""

    _validate(application)

    feature_risks = {
        "dscr": _risk_from_dscr(application.dscr),
        "ltv": _risk_from_ltv(application.ltv),
        "business_credit_score": _risk_from_credit_score(application.business_credit_score),
        "years_in_business": _risk_from_years_in_business(application.years_in_business),
        "liquidity_ratio": _risk_from_liquidity_ratio(application.liquidity_ratio),
        "net_profit_margin": _risk_from_profit_margin(application.net_profit_margin),
        "delinquencies_24m": _risk_from_delinquencies(application.delinquencies_24m),
        "industry_risk": INDUSTRY_RISK_MAP[application.industry_risk.lower()],
    }

    weighted_score = sum(
        feature_risks[name] * FEATURE_WEIGHTS[name] for name in FEATURE_WEIGHTS
    )
    risk_score = round(weighted_score * 100, 1)

    return RiskResult(
        application_id=application.application_id,
        risk_score=risk_score,
        risk_rating=_rating_from_score(risk_score),
        decision=_decision_from_score(risk_score),
        reason_codes=_reason_codes(application, feature_risks),
    )


def _validate(application: LoanApplication) -> None:
    if application.dscr < 0:
        raise ValueError("dscr must be non-negative")
    if not 0 <= application.ltv <= 2:
        raise ValueError("ltv must be between 0 and 2")
    if not 0 <= application.business_credit_score <= 100:
        raise ValueError("business_credit_score must be between 0 and 100")
    if application.years_in_business < 0:
        raise ValueError("years_in_business must be non-negative")
    if application.liquidity_ratio < 0:
        raise ValueError("liquidity_ratio must be non-negative")
    if application.delinquencies_24m < 0:
        raise ValueError("delinquencies_24m must be non-negative")
    if application.industry_risk.lower() not in INDUSTRY_RISK_MAP:
        raise ValueError("industry_risk must be low, medium, or high")


def _risk_from_dscr(dscr: float) -> float:
    if dscr >= 1.50:
        return 0.05
    if dscr >= 1.25:
        return 0.20
    if dscr >= 1.10:
        return 0.45
    if dscr >= 1.00:
        return 0.70
    return 0.95


def _risk_from_ltv(ltv: float) -> float:
    if ltv <= 0.50:
        return 0.10
    if ltv <= 0.65:
        return 0.25
    if ltv <= 0.80:
        return 0.50
    if ltv <= 0.90:
        return 0.75
    return 0.95


def _risk_from_credit_score(score: int) -> float:
    if score >= 85:
        return 0.05
    if score >= 75:
        return 0.25
    if score >= 65:
        return 0.50
    if score >= 55:
        return 0.75
    return 0.95


def _risk_from_years_in_business(years: float) -> float:
    if years >= 10:
        return 0.05
    if years >= 5:
        return 0.25
    if years >= 3:
        return 0.50
    if years >= 1:
        return 0.75
    return 0.95


def _risk_from_liquidity_ratio(ratio: float) -> float:
    if ratio >= 2.0:
        return 0.05
    if ratio >= 1.5:
        return 0.25
    if ratio >= 1.0:
        return 0.50
    if ratio >= 0.75:
        return 0.75
    return 0.95


def _risk_from_profit_margin(margin: float) -> float:
    if margin >= 0.15:
        return 0.05
    if margin >= 0.08:
        return 0.25
    if margin >= 0.03:
        return 0.50
    if margin >= 0:
        return 0.75
    return 0.95


def _risk_from_delinquencies(count: int) -> float:
    if count == 0:
        return 0.05
    if count == 1:
        return 0.35
    if count == 2:
        return 0.65
    return 0.95


def _rating_from_score(score: float) -> str:
    if score < 20:
        return "A"
    if score < 40:
        return "B"
    if score < 60:
        return "C"
    if score < 80:
        return "D"
    return "E"


def _decision_from_score(score: float) -> str:
    if score < 40:
        return "approve"
    if score < 70:
        return "review"
    return "decline"


def _reason_codes(
    application: LoanApplication, feature_risks: dict[str, float]
) -> tuple[str, ...]:
    labels = {
        "dscr": "<3weak debt service coverage",
        "ltv": "high loan-to-value",
        "business_credit_score": "lower business credit score",
        "years_in_business": "limited operating history",
        "liquidity_ratio": "thin liquidity position",
        "net_profit_margin": "low profitability",
        "delinquencies_24m": "recent payment delinquencies",
        "industry_risk": f"{application.industry_risk.lower()} industry risk",
    }
    ranked = sorted(
        feature_risks.items(),
        key=lambda item: item[1] * FEATURE_WEIGHTS[item[0]],
        reverse=True,
    )
    return tuple(labels[name] for name, risk in ranked[:3] if risk >= 0.45)
