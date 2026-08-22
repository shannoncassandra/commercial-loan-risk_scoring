import unittest

from loan_risk.model import LoanApplication, score_application


class RiskScoringTests(unittest.TestCase):
    def test_low_risk_application_is_approved(self) -> None:
        application = LoanApplication(
            application_id="CL-LOW",
            dscr=1.7,
            ltv=0.45,
            business_credit_score=90,
            years_in_business=15,
            liquidity_ratio=2.2,
            net_profit_margin=0.20,
            delinquencies_24m=0,
            industry_risk="low",
        )

        result = score_application(application)

        self.assertEqual(result.risk_rating, "A")
        self.assertEqual(result.decision, "approve")
        self.assertLess(result.risk_score, 20)

    def test_high_risk_application_is_declined_with_reason_codes(self) -> None:
        application = LoanApplication(
            application_id="CL-HIGH",
            dscr=0.9,
            ltv=0.98,
            business_credit_score=50,
            years_in_business=0.5,
            liquidity_ratio=0.6,
            net_profit_margin=-0.05,
            delinquencies_24m=4,
            industry_risk="high",
        )

        result = score_application(application)

        self.assertEqual(result.risk_rating, "E")
        self.assertEqual(result.decision, "decline")
        self.assertIn("weak debt service coverage", result.reason_codes)
        self.assertEqual(len(result.reason_codes), 3)

    def test_invalid_industry_risk_raises_error(self) -> None:
        application = LoanApplication(
            application_id="CL-BAD",
            dscr=1.2,
            ltv=0.7,
            business_credit_score=70,
            years_in_business=5,
            liquidity_ratio=1.3,
            net_profit_margin=0.08,
            delinquencies_24m=0,
            industry_risk="unknown",
        )

        with self.assertRaisesRegex(ValueError, "industry_risk"):
            score_application(application)


if __name__ == "__main__":
    unittest.main()
