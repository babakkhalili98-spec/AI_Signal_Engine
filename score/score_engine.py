"""
====================================================
AI Signal Engine
Score Engine
Version : 1.0
====================================================
"""

from typing import Dict, List

from config.settings import (
    MIN_SIGNAL_SCORE,
    MAX_SCORE,
)


class ScoreEngine:
    """
    موتور اصلی امتیازدهی

    تمام ماژول‌ها فقط Evidence ارسال می‌کنند.
    این موتور امتیاز نهایی را محاسبه می‌کند.
    """

    def __init__(self):

        self.reset()

    # -------------------------------------------------

    def reset(self):

        self.categories: Dict[str, float] = {}

        self.reasons: List[dict] = []

        self.raw_score = 0.0

        self.adjusted_score = 0.0

        self.confidence = 0.0

    # -------------------------------------------------

    def add_score(
        self,
        module: str,
        rule_id: str,
        score: float,
        confidence: float,
        title: str,
        description: str
    ):

        self.raw_score += score

        self.categories[module] = (
            self.categories.get(module, 0) + score
        )

        self.reasons.append({

            "module": module,

            "rule_id": rule_id,

            "title": title,

            "description": description,

            "score": score,

            "confidence": confidence

        })

    # -------------------------------------------------

    def calculate_confidence(self):

        if len(self.reasons) == 0:

            self.confidence = 0

            return

        total = sum(
            item["confidence"]
            for item in self.reasons
        )

        self.confidence = round(
            total / len(self.reasons),
            2
        )

    # -------------------------------------------------

    def finalize(self):

        self.calculate_confidence()

        self.adjusted_score = self.raw_score

        if self.adjusted_score > MAX_SCORE:

            self.adjusted_score = MAX_SCORE

        if self.adjusted_score < 0:

            self.adjusted_score = 0

        return {

            "raw_score": round(self.raw_score, 2),

            "score": round(self.adjusted_score, 2),

            "confidence": round(self.confidence, 2),

            "signal": self.adjusted_score >= MIN_SIGNAL_SCORE,

            "reasons": self.reasons,

            "modules": self.categories

        }

    # -------------------------------------------------

    def print_summary(self):

        print()

        print("========== SCORE ==========")

        print("Raw Score :", self.raw_score)

        print("Confidence :", self.confidence)

        print("Final Score :", self.adjusted_score)

        print()

        for reason in self.reasons:

            print(

                f"[{reason['module']}] "

                f"{reason['title']} "

                f"{reason['score']}"

            )

        print("===========================")

