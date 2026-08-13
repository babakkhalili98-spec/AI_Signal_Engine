"""
==========================================================
AI SIGNAL ENGINE
Score Engine
Version : 3.0
==========================================================
"""

import logging


class ScoreEngine:

    def __init__(self):

        self.logger = logging.getLogger("ScoreEngine")

    # =====================================================

    def calculate(self, signal):

        if signal is None:
            return 0

        score = 0

        # -----------------------------
        # Signal
        # -----------------------------

        signal_type = signal.get("signal", "NO TRADE")

        if signal_type == "BUY":
            score += 10

        elif signal_type == "SELL":
            score += 10

        # -----------------------------
        # Confluence
        # -----------------------------

        confluence = signal.get("confluence", 0)

        score += min(confluence * 5, 40)

        # -----------------------------
        # Risk
        # -----------------------------

        risk = signal.get("risk")

        if isinstance(risk, dict):

            rr = risk.get("rr", 0)

            if rr >= 3:
                score += 30

            elif rr >= 2:
                score += 20

            elif rr >= 1:
                score += 10

        else:

            self.logger.warning(
                "Risk is None. Score calculated without RR."
            )

        # -----------------------------
        # Confidence
        # -----------------------------

        confidence = signal.get("confidence", 0)

        score += confidence

        # -----------------------------
        # Limit
        # -----------------------------

        score = max(0, min(score, 100))

        return score