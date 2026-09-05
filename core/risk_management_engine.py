"""
=========================================================
AI Signal Engine
Risk Management Engine
Version : 3.0.0
=========================================================

وظایف

• مدیریت ریسک معاملات
• مدیریت سرمایه
• محاسبه حجم معامله
• بررسی RR
• مدیریت Drawdown
• مدیریت Portfolio Risk
• بررسی Margin
• بررسی Leverage
• بررسی Correlation
• تصمیم نهایی برای ورود

=========================================================
"""

from __future__ import annotations

import logging

from dataclasses import dataclass
from typing import List
from typing import Optional


# ==========================================================
# Result
# ==========================================================

@dataclass
class RiskManagementResult:

    approved: bool

    risk_reward: float

    position_size_percent: float

    leverage: int

    portfolio_risk: float

    account_risk: float

    daily_loss: float

    drawdown: float

    correlation_risk: str

    open_positions: int

    liquidation_distance: float

    margin_usage: float

    status: str

    warnings: List[str]

    suggestions: List[str]


# ==========================================================
# Risk Engine
# ==========================================================

class RiskManagementEngine:

    """
    مدیریت ریسک کل پروژه
    """

    def __init__(

        self,

        position_size=5,

        leverage=8,

        max_positions=5,

        min_rr=1.0,

        max_daily_loss=6,

        max_drawdown=20,

        max_portfolio_risk=25

    ):

        self.logger = logging.getLogger(

            "RiskManagement"

        )

        self.position_size = position_size

        self.leverage = leverage

        self.max_positions = max_positions

        self.min_rr = min_rr

        self.max_daily_loss = max_daily_loss

        self.max_drawdown = max_drawdown

        self.max_portfolio_risk = max_portfolio_risk

        self.logger.info(

            "Risk Management Ready"

        )

    # -------------------------------------------------

    def initialize(self):

        """
        آماده‌سازی Engine
        """

        self.logger.info(

            "Risk Engine Initialized"

        )
    # -------------------------------------------------
    # Risk / Reward
    # -------------------------------------------------

    def calculate_rr(

        self,

        entry,

        stop_loss,

        take_profit

    ):

        """
        محاسبه نسبت سود به ضرر
        """

        risk = abs(

            entry - stop_loss

        )

        reward = abs(

            take_profit - entry

        )

        if risk == 0:

            return 0.0

        return round(

            reward / risk,

            2

        )

    # -------------------------------------------------
    # Position Size
    # -------------------------------------------------

    def calculate_position_size(

        self,

        capital

    ):

        """
        حجم هر معامله
        """

        return round(

            capital *

            self.position_size /

            100,

            2

        )

    # -------------------------------------------------
    # Account Risk
    # -------------------------------------------------

    def calculate_account_risk(

        self,

        capital,

        entry,

        stop_loss

    ):

        """
        درصد ریسک سرمایه
        """

        position = self.calculate_position_size(

            capital

        )

        if entry == 0:

            return 0

        loss_percent = abs(

            entry - stop_loss

        ) / entry

        risk = (

            position *

            loss_percent

        ) / capital * 100

        return round(

            risk,

            2

        )

    # -------------------------------------------------
    # Margin Usage
    # -------------------------------------------------

    def calculate_margin_usage(

        self,

        capital

    ):

        """
        میزان استفاده از مارجین
        """

        position = self.calculate_position_size(

            capital

        )

        if self.leverage <= 0:

            return 0

        margin = (

            position /

            self.leverage

        )

        return round(

            margin,

            2

        )

    # -------------------------------------------------
    # Liquidation Distance
    # -------------------------------------------------

    def calculate_liquidation_distance(

        self,

        entry

    ):

        """
        فاصله تقریبی لیکویید
        """

        if self.leverage <= 0:

            return 0

        distance = (

            entry /

            self.leverage

        )

        return round(

            distance,

            2
        )

    # -------------------------------------------------
    # Portfolio Risk
    # -------------------------------------------------

    def calculate_portfolio_risk(

        self,

        risks

    ):

        """
        ریسک کل پرتفوی
        """

        if not risks:

            return 0

        return round(

            sum(risks),

            2

        )
    # -------------------------------------------------
    # Correlation Risk
    # -------------------------------------------------

    def check_correlation(

        self,

        correlation_risk

    ):

        """
        بررسی همبستگی معاملات
        """

        warnings = []

        approved = True

        if correlation_risk == "HIGH":

            approved = False

            warnings.append(

                "همبستگی معاملات بسیار زیاد است."

            )

        elif correlation_risk == "MEDIUM":

            warnings.append(

                "همبستگی معاملات متوسط است."

            )

        return approved, warnings

    # -------------------------------------------------
    # Position Limit
    # -------------------------------------------------

    def check_position_limit(

        self,

        open_positions

    ):

        """
        بررسی تعداد معاملات باز
        """

        warnings = []

        approved = True

        if open_positions >= self.max_positions:

            approved = False

            warnings.append(

                "حداکثر تعداد معاملات باز تکمیل شده است."

            )

        return approved, warnings

    # -------------------------------------------------
    # Drawdown
    # -------------------------------------------------

    def check_drawdown(

        self,

        drawdown

    ):

        """
        بررسی افت سرمایه
        """

        warnings = []

        approved = True

        if drawdown >= self.max_drawdown:

            approved = False

            warnings.append(

                "حداکثر Drawdown مجاز عبور کرده است."

            )

        return approved, warnings

    # -------------------------------------------------
    # Daily Loss
    # -------------------------------------------------

    def check_daily_loss(

        self,

        daily_loss

    ):

        """
        بررسی ضرر روزانه
        """

        warnings = []

        approved = True

        if daily_loss >= self.max_daily_loss:

            approved = False

            warnings.append(

                "حد ضرر روزانه پر شده است."

            )

        return approved, warnings

    # -------------------------------------------------
    # Portfolio Risk
    # -------------------------------------------------

    def check_portfolio_risk(

        self,

        portfolio_risk

    ):

        """
        بررسی ریسک کل سبد
        """

        warnings = []

        approved = True

        if portfolio_risk >= self.max_portfolio_risk:

            approved = False

            warnings.append(

                "ریسک کل پرتفوی بیش از حد مجاز است."

            )

        return approved, warnings

    # -------------------------------------------------
    # RR Check
    # -------------------------------------------------

    def check_rr(

        self,

        rr

    ):

        """
        بررسی حداقل نسبت سود به ضرر
        """

        warnings = []

        approved = True

        if rr < self.min_rr:

            approved = False

            warnings.append(

                "Risk / Reward کمتر از مقدار مجاز است."

            )

        return approved, warnings
    # -------------------------------------------------
    # Analyze
    # -------------------------------------------------

    def analyze(

        self,

        capital,

        entry,

        stop_loss,

        take_profit,

        open_positions=0,

        portfolio_risk=0,

        daily_loss=0,

        drawdown=0,

        correlation_risk="LOW"

    ):

        """
        تحلیل کامل ریسک معامله
        """

        warnings = []

        suggestions = []

        approved = True

        # -----------------------------------------
        # RR
        # -----------------------------------------

        rr = self.calculate_rr(

            entry,

            stop_loss,

            take_profit

        )

        ok, msg = self.check_rr(rr)

        approved &= ok

        warnings.extend(msg)

        # -----------------------------------------
        # Position Limit
        # -----------------------------------------

        ok, msg = self.check_position_limit(

            open_positions

        )

        approved &= ok

        warnings.extend(msg)

        # -----------------------------------------
        # Correlation
        # -----------------------------------------

        ok, msg = self.check_correlation(

            correlation_risk

        )

        approved &= ok

        warnings.extend(msg)

        # -----------------------------------------
        # Portfolio Risk
        # -----------------------------------------

        ok, msg = self.check_portfolio_risk(

            portfolio_risk

        )

        approved &= ok

        warnings.extend(msg)

        # -----------------------------------------
        # Daily Loss
        # -----------------------------------------

        ok, msg = self.check_daily_loss(

            daily_loss

        )

        approved &= ok

        warnings.extend(msg)

        # -----------------------------------------
        # Drawdown
        # -----------------------------------------

        ok, msg = self.check_drawdown(

            drawdown

        )

        approved &= ok

        warnings.extend(msg)

        # -----------------------------------------
        # Position Size
        # -----------------------------------------

        position_size = self.calculate_position_size(

            capital

        )

        account_risk = self.calculate_account_risk(

            capital,

            entry,

            stop_loss

        )

        liquidation = self.calculate_liquidation_distance(

            entry

        )

        margin = self.calculate_margin_usage(

            capital

        )

        # -----------------------------------------
        # Suggestions
        # -----------------------------------------

        if rr < 1.5:

            suggestions.append(

                "بهتر است TP افزایش یابد."

            )

        if correlation_risk == "MEDIUM":

            suggestions.append(

                "حجم معامله را کاهش بده."

            )

        if portfolio_risk > 15:

            suggestions.append(

                "ورود با احتیاط انجام شود."

            )

        # -----------------------------------------
        # Status
        # -----------------------------------------

        status = (

            "APPROVED"

            if approved

            else

            "REJECTED"

        )

        return RiskManagementResult(

            approved=approved,

            risk_reward=rr,

            position_size_percent=self.position_size,

            leverage=self.leverage,

            portfolio_risk=portfolio_risk,

            account_risk=account_risk,

            daily_loss=daily_loss,

            drawdown=drawdown,

            correlation_risk=correlation_risk,

            open_positions=open_positions,

            liquidation_distance=liquidation,

            margin_usage=margin,

            status=status,

            warnings=warnings,

            suggestions=suggestions

        )

    def calculate(self, symbol, signal, data):

        entry = signal["metadata"]["entry"]

        stop = signal["metadata"]["stop_loss"]

        tp = signal["metadata"]["take_profit"]

        capital = 100

        result = self.analyze(

            capital=capital,

            entry=entry,

            stop_loss=stop,

            take_profit=tp,

        )

        return {

            "approved": result.approved,

            "rr": result.risk_reward,

            "position_size": result.position_size_percent,

            "warnings": result.warnings,

            "status": result.status,

        }
    # -------------------------------------------------
    # Statistics
    # -------------------------------------------------

    def statistics(self):
        """
        آمار موتور مدیریت ریسک
        """

        return {

            "position_size_percent":
                self.position_size,

            "leverage":
                self.leverage,

            "max_positions":
                self.max_positions,

            "minimum_rr":
                self.min_rr,

            "max_daily_loss":
                self.max_daily_loss,

            "max_drawdown":
                self.max_drawdown,

            "max_portfolio_risk":
                self.max_portfolio_risk

        }

    # -------------------------------------------------
    # Health Check
    # -------------------------------------------------

    def health_check(self):
        """
        بررسی وضعیت موتور
        """

        return {

            "engine":

                "RiskManagementEngine",

            "status":

                "READY",

            "statistics":

                self.statistics()

        }

    # -------------------------------------------------
    # Reset
    # -------------------------------------------------

    def reset(self):
        """
        ریست موقت موتور
        """

        self.logger.info(

            "Risk Engine Reset"

        )

    # -------------------------------------------------
    # Shutdown
    # -------------------------------------------------

    def shutdown(self):
        """
        خاموش کردن موتور
        """

        self.logger.info("")

        self.logger.info("=" * 60)

        self.logger.info(

            "RISK MANAGEMENT SHUTDOWN"

        )

        self.logger.info("=" * 60)

        self.reset()

        self.logger.info(

            "Risk Engine Closed"

        )