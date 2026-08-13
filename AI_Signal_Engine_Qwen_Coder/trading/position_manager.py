"""
=========================================================
AI Signal Engine
Position Manager
Version : 1.0
=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List


# ===========================================
# Position Model
# ===========================================

@dataclass
class Position:

    symbol: str

    side: str

    entry_price: float

    quantity: float

    leverage: int

    open_time: datetime

    strategy: str = "AI"

    signal_score: float = 0.0

    stop_loss: float = 0.0

    take_profit_1: float = 0.0

    take_profit_2: float = 0.0

    take_profit_3: float = 0.0

    tp1_hit: bool = False

    tp2_hit: bool = False

    tp3_hit: bool = False

    break_even: bool = False

    trailing_active: bool = False

    trailing_price: float = 0.0

    highest_price: float = 0.0

    lowest_price: float = 999999999

    unrealized_profit: float = 0.0

    unrealized_percent: float = 0.0

    health_score: float = 100.0

    emergency_exit: bool = False

    close_reason: str = ""

    news_warning: bool = False

    market_structure: str = ""

    last_update: datetime = field(default_factory=datetime.utcnow)


# ===========================================
# Position Manager
# ===========================================

class PositionManager:

    def __init__(

        self,

        database,

        reporter,

        risk_manager,

        logger

    ):

        self.database = database

        self.reporter = reporter

        self.risk_manager = risk_manager

        self.logger = logger

        self.positions: Dict[str, Position] = {}

    # ---------------------------------------

    def add_position(

        self,

        position: Position

    ):

        self.positions[position.symbol] = position

        self.logger.info(

            f"Position Opened : {position.symbol}"

        )

        self.database.save_position(position)

    # ---------------------------------------

    def remove_position(

        self,

        symbol: str

    ):

        if symbol not in self.positions:

            return

        del self.positions[symbol]

    # ---------------------------------------

    def get_position(

        self,

        symbol: str

    ) -> Optional[Position]:

        return self.positions.get(symbol)

    # ---------------------------------------

    def has_position(

        self,

        symbol: str

    ) -> bool:

        return symbol in self.positions

    # ---------------------------------------

    def get_open_positions(

        self

    ) -> List[Position]:

        return list(

            self.positions.values()

        )

    # ---------------------------------------

    def total_positions(

        self

    ) -> int:

        return len(

            self.positions

        )

    # ---------------------------------------

    def update_market_price(

        self,

        symbol: str,

        current_price: float

    ):

        if symbol not in self.positions:

            return

        p = self.positions[symbol]

        p.last_update = datetime.utcnow()

        if p.side == "BUY":

            profit = current_price - p.entry_price

        else:

            profit = p.entry_price - current_price

        p.unrealized_profit = (

            profit

            * p.quantity

            * p.leverage

        )

        p.unrealized_percent = (

            profit

            / p.entry_price

        ) * 100

        if current_price > p.highest_price:

            p.highest_price = current_price

        if current_price < p.lowest_price:

            p.lowest_price = current_price

    # ---------------------------------------

    def save_all(self):

        for position in self.positions.values():

            self.database.update_position(

                position

            )

    # ---------------------------------------

    def load_positions(self):

        items = self.database.load_open_positions()

        for p in items:

            self.positions[p.symbol] = p

        self.logger.info(

            f"{len(items)} positions loaded."
        )

    # ---------------------------------------

    def close_position(

        self,

        symbol: str,

        reason: str

    ):

        if symbol not in self.positions:

            return

        position = self.positions[symbol]

        position.close_reason = reason

        self.database.close_position(

            position

        )

        self.reporter.position_closed(

            position

        )

        self.logger.info(

            f"{symbol} Closed ({reason})"

        )

        del self.positions[symbol]
# ==========================================================
# SMART TAKE PROFIT
# ==========================================================

def calculate_take_profit(
    self,
    position,
    analysis
):
    """
    تعیین TP بر اساس تحلیل بازار
    """

    current = analysis["price"]

    atr = analysis.get("atr", 0)

    resistance = analysis.get("resistance", [])

    support = analysis.get("support", [])

    side = position.side.upper()

    # -----------------------------
    # BUY
    # -----------------------------
    if side == "BUY":

        targets = []

        for r in resistance:
            if r > current:
                targets.append(r)

        targets = sorted(targets)

        if len(targets) >= 1:
            position.take_profit_1 = targets[0]
        else:
            position.take_profit_1 = current + atr

        if len(targets) >= 2:
            position.take_profit_2 = targets[1]
        else:
            position.take_profit_2 = position.take_profit_1 + atr

        if len(targets) >= 3:
            position.take_profit_3 = targets[2]
        else:
            position.take_profit_3 = position.take_profit_2 + atr

    # -----------------------------
    # SELL
    # -----------------------------
    else:

        targets = []

        for s in support:
            if s < current:
                targets.append(s)

        targets = sorted(targets, reverse=True)

        if len(targets) >= 1:
            position.take_profit_1 = targets[0]
        else:
            position.take_profit_1 = current - atr

        if len(targets) >= 2:
            position.take_profit_2 = targets[1]
        else:
            position.take_profit_2 = position.take_profit_1 - atr

        if len(targets) >= 3:
            position.take_profit_3 = targets[2]
        else:
            position.take_profit_3 = position.take_profit_2 - atr


# ==========================================================
# SMART STOP LOSS
# ==========================================================

def calculate_stop_loss(
    self,
    position,
    analysis
):

    atr = analysis.get("atr", 0)

    swing_high = analysis.get("swing_high")

    swing_low = analysis.get("swing_low")

    side = position.side.upper()

    if side == "BUY":

        if swing_low:

            position.stop_loss = swing_low - atr * 0.30

        else:

            position.stop_loss = (
                position.entry_price
                - atr
            )

    else:

        if swing_high:

            position.stop_loss = swing_high + atr * 0.30

        else:

            position.stop_loss = (
                position.entry_price
                + atr
            )


# ==========================================================
# UPDATE TP STATUS
# ==========================================================

def update_take_profit(
    self,
    position,
    price
):

    if position.side == "BUY":

        if (
            not position.tp1_hit
            and
            price >= position.take_profit_1
        ):

            position.tp1_hit = True

        if (
            not position.tp2_hit
            and
            price >= position.take_profit_2
        ):

            position.tp2_hit = True

        if (
            not position.tp3_hit
            and
            price >= position.take_profit_3
        ):

            position.tp3_hit = True

    else:

        if (
            not position.tp1_hit
            and
            price <= position.take_profit_1
        ):

            position.tp1_hit = True

        if (
            not position.tp2_hit
            and
            price <= position.take_profit_2
        ):

            position.tp2_hit = True

        if (
            not position.tp3_hit
            and
            price <= position.take_profit_3
        ):

            position.tp3_hit = True


# ==========================================================
# STOP LOSS HIT
# ==========================================================

def stop_loss_hit(
    self,
    position,
    price
):

    if position.side == "BUY":

        return price <= position.stop_loss

    return price >= position.stop_loss


# ==========================================================
# RISK REWARD
# ==========================================================

def risk_reward(
    self,
    position
):

    risk = fabs(

        position.entry_price
        -
        position.stop_loss

    )

    reward = fabs(

        position.take_profit_1
        -
        position.entry_price

    )

    if risk == 0:

        return 0

    return round(

        reward / risk,

        2

    )
    # =====================================================
    # BREAK EVEN
    # =====================================================

    def update_break_even(self, position, current_price):

        if position.break_even:
            return

        rr = self.risk_reward(position)

        if rr < 1:
            return

        risk = abs(position.entry_price - position.stop_loss)

        if position.side == "BUY":

            if current_price >= position.entry_price + risk:

                position.stop_loss = position.entry_price
                position.break_even = True

                self.logger.info(
                    f"{position.symbol} -> Break Even Activated"
                )

        else:

            if current_price <= position.entry_price - risk:

                position.stop_loss = position.entry_price
                position.break_even = True

                self.logger.info(
                    f"{position.symbol} -> Break Even Activated"
                )

    # =====================================================
    # SMART TRAILING STOP
    # =====================================================

    def update_trailing_stop(
        self,
        position,
        analysis,
        current_price
    ):

        atr = analysis.get("atr", 0)

        swing_high = analysis.get("swing_high")

        swing_low = analysis.get("swing_low")

        if position.side == "BUY":

            if swing_low:

                new_sl = swing_low - atr * 0.20

                if new_sl > position.stop_loss:

                    position.stop_loss = new_sl
                    position.trailing_active = True

        else:

            if swing_high:

                new_sl = swing_high + atr * 0.20

                if new_sl < position.stop_loss:

                    position.stop_loss = new_sl
                    position.trailing_active = True

    # =====================================================
    # UPDATE HIGH LOW
    # =====================================================

    def update_extremes(
        self,
        position,
        current_price
    ):

        if current_price > position.highest_price:

            position.highest_price = current_price

        if current_price < position.lowest_price:

            position.lowest_price = current_price

    # =====================================================
    # CHECK POSITION
    # =====================================================

    def monitor_position(
        self,
        position,
        analysis,
        current_price
    ):

        self.update_take_profit(
            position,
            current_price
        )

        self.update_break_even(
            position,
            current_price
        )

        self.update_trailing_stop(
            position,
            analysis,
            current_price
        )

        self.update_extremes(
            position,
            current_price
        )

        if self.stop_loss_hit(
            position,
            current_price
        ):

            self.close_position(
                position.symbol,
                "STOP LOSS"
            )

    # =====================================================
    # UPDATE ALL POSITIONS
    # =====================================================

    def update_all_positions(
        self,
        market_analysis
    ):

        for symbol in list(self.positions.keys()):

            if symbol not in market_analysis:
                continue

            analysis = market_analysis[symbol]

            current_price = analysis["price"]

            position = self.positions[symbol]

            self.monitor_position(

                position,

                analysis,

                current_price

            )
    # =====================================================
    # HEALTH SCORE
    # =====================================================

    def calculate_health_score(
        self,
        position,
        analysis
    ):

        score = 100

        trend = analysis.get("trend", "NEUTRAL")
        rsi = analysis.get("rsi", 50)
        volume_score = analysis.get("volume_score", 50)
        signal_score = analysis.get("signal_score", 70)
        news_warning = analysis.get("news_warning", False)
        market_structure = analysis.get(
            "market_structure",
            "UNKNOWN"
        )

        # Trend
        if position.side == "BUY":

            if trend == "BEARISH":
                score -= 30

        else:

            if trend == "BULLISH":
                score -= 30

        # RSI

        if position.side == "BUY":

            if rsi > 80:
                score -= 10

            if rsi < 30:
                score -= 20

        else:

            if rsi < 20:
                score -= 10

            if rsi > 70:
                score -= 20

        # Volume

        if volume_score < 40:
            score -= 10

        # Signal Score

        if signal_score < 70:
            score -= 10

        # News

        if news_warning:
            score -= 10

        # Structure

        if market_structure == "WEAK":
            score -= 15

        score = max(0, min(100, score))

        position.health_score = score

        return score

    # =====================================================
    # EMERGENCY EXIT
    # =====================================================

    def check_emergency_exit(
        self,
        position,
        analysis
    ):

        reason = None

        trend = analysis.get("trend")

        reversal = analysis.get(
            "reversal_pattern",
            False
        )

        divergence = analysis.get(
            "rsi_divergence",
            False
        )

        news_warning = analysis.get(
            "news_warning",
            False
        )

        health = self.calculate_health_score(
            position,
            analysis
        )

        if health <= 40:
            reason = "LOW HEALTH SCORE"

        elif reversal:
            reason = "REVERSAL PATTERN"

        elif divergence:
            reason = "RSI DIVERGENCE"

        elif news_warning:
            reason = "HIGH IMPACT NEWS"

        elif position.side == "BUY" and trend == "BEARISH":
            reason = "TREND REVERSAL"

        elif position.side == "SELL" and trend == "BULLISH":
            reason = "TREND REVERSAL"

        if reason:

            position.emergency_exit = True

            self.logger.warning(

                f"{position.symbol} Emergency Exit -> {reason}"

            )

            self.close_position(

                position.symbol,

                reason

            )

    # =====================================================
    # POSITION STATUS
    # =====================================================

    def get_position_status(
        self,
        position
    ):

        return {

            "symbol": position.symbol,

            "side": position.side,

            "health": position.health_score,

            "profit": round(
                position.unrealized_profit,
                2
            ),

            "profit_percent": round(
                position.unrealized_percent,
                2
            ),

            "tp1": position.tp1_hit,

            "tp2": position.tp2_hit,

            "tp3": position.tp3_hit,

            "break_even": position.break_even,

            "trailing": position.trailing_active,

            "news": position.news_warning,

            "emergency": position.emergency_exit

        }

    # =====================================================
    # UPDATE HEALTH
    # =====================================================

    def update_position_health(
        self,
        analysis
    ):

        for symbol in self.positions:

            if symbol not in analysis:
                continue

            self.calculate_health_score(

                self.positions[symbol],

                analysis[symbol]

            )

    # =====================================================
    # CHECK EMERGENCY
    # =====================================================

    def emergency_scan(
        self,
        analysis
    ):

        for symbol in list(self.positions.keys()):

            if symbol not in analysis:
                continue

            self.check_emergency_exit(

                self.positions[symbol],

                analysis[symbol]

            )
    # =====================================================
    # SAVE POSITION
    # =====================================================

    def save_position(self, position):

        position.last_update = datetime.utcnow()

        self.database.update_position(position)

    # =====================================================
    # SAVE ALL
    # =====================================================

    def save_positions(self):

        for position in self.positions.values():

            self.save_position(position)

    # =====================================================
    # PARTIAL CLOSE
    # =====================================================

    def partial_close(
        self,
        symbol,
        percent,
        reason
    ):

        if symbol not in self.positions:
            return

        position = self.positions[symbol]

        qty = position.quantity * (percent / 100)

        if qty <= 0:
            return

        position.quantity -= qty

        self.database.save_partial_close(

            symbol=symbol,

            quantity=qty,

            reason=reason,

            price=position.highest_price,

            time=datetime.utcnow()

        )

        self.logger.info(

            f"{symbol} Partial Close {percent}%"

        )

    # =====================================================
    # REPORT POSITION
    # =====================================================

    def report_position(
        self,
        symbol
    ):

        if symbol not in self.positions:
            return

        position = self.positions[symbol]

        report = self.get_position_status(

            position

        )

        self.reporter.position_update(

            report

        )

    # =====================================================
    # REPORT ALL
    # =====================================================

    def report_all_positions(self):

        for symbol in self.positions:

            self.report_position(

                symbol

            )

    # =====================================================
    # POSITION STATISTICS
    # =====================================================

    def statistics(self):

        total = len(self.positions)

        buy = 0

        sell = 0

        profit = 0

        health = 0

        for p in self.positions.values():

            if p.side == "BUY":

                buy += 1

            else:

                sell += 1

            profit += p.unrealized_profit

            health += p.health_score

        avg_health = 0

        if total:

            avg_health = round(

                health / total,

                2

            )

        return {

            "positions": total,

            "buy": buy,

            "sell": sell,

            "profit": round(

                profit,

                2

            ),

            "average_health": avg_health

        }

    # =====================================================
    # CHECK MAX POSITIONS
    # =====================================================

    def can_open_new_position(self):

        maximum = self.risk_manager.max_positions()

        return len(self.positions) < maximum

    # =====================================================
    # POSITION EXISTS
    # =====================================================

    def same_direction_exists(
        self,
        symbol,
        side
    ):

        if symbol not in self.positions:

            return False

        return self.positions[symbol].side == side

    # =====================================================
    # CLOSE ALL
    # =====================================================

    def close_all(
        self,
        reason
    ):

        symbols = list(

            self.positions.keys()

        )

        for symbol in symbols:

            self.close_position(

                symbol,

                reason

            )

    # =====================================================
    # HEARTBEAT
    # =====================================================

    def heartbeat(self):

        self.save_positions()

        self.report_all_positions()

        stats = self.statistics()

        self.logger.info(

            f"Open:{stats['positions']}  Profit:{stats['profit']}"

        )
    # =====================================================
    # TP1
    # =====================================================

    def process_tp1(
        self,
        position,
        current_price
    ):

        if position.tp1_hit:
            return

        if position.side == "BUY":

            if current_price < position.take_profit_1:
                return

        else:

            if current_price > position.take_profit_1:
                return

        position.tp1_hit = True

        self.partial_close(

            position.symbol,

            30,

            "TP1"

        )

        if position.stop_loss < position.entry_price:

            position.stop_loss = position.entry_price

        self.logger.info(

            f"{position.symbol} TP1 Hit"

        )

    # =====================================================
    # TP2
    # =====================================================

    def process_tp2(
        self,
        position,
        current_price
    ):

        if position.tp2_hit:
            return

        if not position.tp1_hit:
            return

        if position.side == "BUY":

            if current_price < position.take_profit_2:
                return

        else:

            if current_price > position.take_profit_2:
                return

        position.tp2_hit = True

        self.partial_close(

            position.symbol,

            30,

            "TP2"

        )

        if position.side == "BUY":

            position.stop_loss = position.take_profit_1

        else:

            position.stop_loss = position.take_profit_1

        self.logger.info(

            f"{position.symbol} TP2 Hit"

        )

    # =====================================================
    # TP3
    # =====================================================

    def process_tp3(
        self,
        position,
        current_price
    ):

        if position.tp3_hit:
            return

        if not position.tp2_hit:
            return

        if position.side == "BUY":

            if current_price < position.take_profit_3:
                return

        else:

            if current_price > position.take_profit_3:
                return

        position.tp3_hit = True

        self.close_position(

            position.symbol,

            "FINAL TP"

        )

        self.logger.info(

            f"{position.symbol} TP3 Hit"

        )

    # =====================================================
    # CHECK ALL TPS
    # =====================================================

    def process_take_profits(

        self,

        position,

        current_price

    ):

        self.process_tp1(

            position,

            current_price

        )

        self.process_tp2(

            position,

            current_price

        )

        self.process_tp3(

            position,

            current_price

        )

    # =====================================================
    # REMAINING POSITION
    # =====================================================

    def remaining_percent(

        self,

        position

    ):

        if position.tp3_hit:

            return 0

        if position.tp2_hit:

            return 40

        if position.tp1_hit:

            return 70

        return 100

    # =====================================================
    # IS FINISHED
    # =====================================================

    def trade_finished(

        self,

        position

    ):

        return (

            position.tp3_hit

            or

            position.quantity <= 0

        )
    # =====================================================
    # MOVE STOP LOSS
    # =====================================================

    def move_stop_loss(
        self,
        position,
        new_stop
    ):

        if position.side == "BUY":

            if new_stop > position.stop_loss:

                position.stop_loss = new_stop

        else:

            if new_stop < position.stop_loss:

                position.stop_loss = new_stop

    # =====================================================
    # AFTER TP1
    # =====================================================

    def update_after_tp1(
        self,
        position,
        analysis
    ):

        if not position.tp1_hit:
            return

        if position.side == "BUY":

            self.move_stop_loss(

                position,

                position.entry_price

            )

        else:

            self.move_stop_loss(

                position,

                position.entry_price

            )

    # =====================================================
    # AFTER TP2
    # =====================================================

    def update_after_tp2(
        self,
        position,
        analysis
    ):

        if not position.tp2_hit:
            return

        atr = analysis.get("atr", 0)

        swing_low = analysis.get("swing_low")

        swing_high = analysis.get("swing_high")

        if position.side == "BUY":

            if swing_low:

                self.move_stop_loss(

                    position,

                    swing_low - atr * 0.20

                )

        else:

            if swing_high:

                self.move_stop_loss(

                    position,

                    swing_high + atr * 0.20

                )

    # =====================================================
    # ICHIMOKU STOP
    # =====================================================

    def ichimoku_stop(
        self,
        position,
        analysis
    ):

        cloud_top = analysis.get("cloud_top")

        cloud_bottom = analysis.get("cloud_bottom")

        if cloud_top is None:
            return

        if cloud_bottom is None:
            return

        if position.side == "BUY":

            self.move_stop_loss(

                position,

                cloud_bottom

            )

        else:

            self.move_stop_loss(

                position,

                cloud_top

            )

    # =====================================================
    # PIVOT STOP
    # =====================================================

    def pivot_stop(
        self,
        position,
        analysis
    ):

        pivot = analysis.get("pivot")

        if pivot is None:
            return

        if position.side == "BUY":

            if pivot > position.stop_loss:

                self.move_stop_loss(

                    position,

                    pivot

                )

        else:

            if pivot < position.stop_loss:

                self.move_stop_loss(

                    position,

                    pivot

                )

    # =====================================================
    # TRAILING MANAGER
    # =====================================================

    def update_dynamic_stop(
        self,
        position,
        analysis
    ):

        self.update_after_tp1(

            position,

            analysis

        )

        self.update_after_tp2(

            position,

            analysis

        )

        self.ichimoku_stop(

            position,

            analysis

        )

        self.pivot_stop(

            position,

            analysis

        )

    # =====================================================
    # PROTECT PROFIT
    # =====================================================

    def protect_profit(
        self,
        position,
        current_price
    ):

        if position.side == "BUY":

            if current_price > position.highest_price:

                position.highest_price = current_price

        else:

            if current_price < position.lowest_price:

                position.lowest_price = current_price
    # =====================================================
    # STOP LOSS DECISION ENGINE
    # =====================================================

    def calculate_best_stop(
        self,
        position,
        analysis
    ):

        candidates = []

        atr = analysis.get("atr", 0)

        swing_low = analysis.get("swing_low")
        swing_high = analysis.get("swing_high")

        pivot = analysis.get("pivot")

        cloud_top = analysis.get("cloud_top")
        cloud_bottom = analysis.get("cloud_bottom")

        support = analysis.get("support", [])
        resistance = analysis.get("resistance", [])

        # -----------------------------
        # BUY
        # -----------------------------

        if position.side == "BUY":

            if swing_low:
                candidates.append(
                    (
                        swing_low - atr * 0.20,
                        95,
                        "Swing Low"
                    )
                )

            if cloud_bottom:
                candidates.append(
                    (
                        cloud_bottom,
                        90,
                        "Ichimoku"
                    )
                )

            if pivot:
                candidates.append(
                    (
                        pivot,
                        80,
                        "Pivot"
                    )
                )

            for s in support:

                candidates.append(
                    (
                        s,
                        70,
                        "Support"
                    )
                )

        # -----------------------------
        # SELL
        # -----------------------------

        else:

            if swing_high:

                candidates.append(
                    (
                        swing_high + atr * 0.20,
                        95,
                        "Swing High"
                    )
                )

            if cloud_top:

                candidates.append(
                    (
                        cloud_top,
                        90,
                        "Ichimoku"
                    )
                )

            if pivot:

                candidates.append(
                    (
                        pivot,
                        80,
                        "Pivot"
                    )
                )

            for r in resistance:

                candidates.append(
                    (
                        r,
                        70,
                        "Resistance"
                    )
                )

        if len(candidates) == 0:

            return None

        candidates = sorted(

            candidates,

            key=lambda x: x[1],

            reverse=True

        )

        best = candidates[0]

        return {

            "price": best[0],

            "score": best[1],

            "reason": best[2]

        }

    # =====================================================
    # APPLY BEST STOP
    # =====================================================

    def apply_best_stop(

        self,

        position,

        analysis

    ):

        result = self.calculate_best_stop(

            position,

            analysis

        )

        if result is None:

            return

        self.move_stop_loss(

            position,

            result["price"]

        )

        self.logger.info(

            f"{position.symbol} "

            f"SL -> {result['reason']}"

        )

    # =====================================================
    # STOP VALIDATION
    # =====================================================

    def validate_stop(

        self,

        position

    ):

        risk = abs(

            position.entry_price

            -

            position.stop_loss

        )

        if risk <= 0:

            return False

        rr = self.risk_reward(

            position

        )

        if rr < 1.5:

            return False

        return True

    # =====================================================
    # AUTO IMPROVE STOP
    # =====================================================

    def improve_stop(

        self,

        position,

        analysis

    ):

        self.apply_best_stop(

            position,

            analysis

        )

        if not self.validate_stop(

            position

        ):

            self.logger.warning(

                f"{position.symbol} "

                f"Risk Reward Too Low"

            )
    # =====================================================
    # UPDATE POSITION AGE
    # =====================================================

    def update_position_age(self, position):

        now = datetime.utcnow()

        position.age_minutes = int(

            (now - position.open_time).total_seconds() / 60

        )

        position.age_hours = round(

            position.age_minutes / 60,

            2

        )

    # =====================================================
    # STAGNANT TRADE
    # =====================================================

    def stagnant_trade(self, position):

        if position.age_hours < 12:
            return False

        if abs(position.unrealized_percent) < 0.30:

            return True

        return False

    # =====================================================
    # LIQUIDATION CHECK
    # =====================================================

    def liquidation_warning(

        self,

        position,

        current_price

    ):

        if position.side == "BUY":

            distance = (

                current_price

                -

                position.stop_loss

            )

        else:

            distance = (

                position.stop_loss

                -

                current_price

            )

        if distance <= 0:

            return True

        risk_percent = (

            distance

            /

            current_price

        ) * 100

        if risk_percent < 0.50:

            return True

        return False

    # =====================================================
    # MARGIN CHECK
    # =====================================================

    def margin_check(

        self,

        position,

        account

    ):

        margin_level = account.get(

            "margin_level",

            999

        )

        if margin_level < 120:

            self.logger.warning(

                f"{position.symbol} Margin Warning"

            )

            return False

        return True

    # =====================================================
    # STALE POSITION CHECK
    # =====================================================

    def stale_position_check(

        self,

        position

    ):

        if self.stagnant_trade(position):

            self.logger.info(

                f"{position.symbol} Stagnant Trade"

            )

            return True

        return False

    # =====================================================
    # POSITION PROTECTION
    # =====================================================

    def protect_position(

        self,

        position,

        current_price,

        account

    ):

        self.update_position_age(position)

        if self.liquidation_warning(

            position,

            current_price

        ):

            self.logger.warning(

                f"{position.symbol} Liquidation Risk"

            )

        self.margin_check(

            position,

            account

        )

        self.stale_position_check(

            position

        )
    # =====================================================
    # TRADE JOURNAL
    # =====================================================

    def write_trade_journal(
        self,
        position,
        result
    ):

        journal = {

            "symbol": position.symbol,

            "side": position.side,

            "entry": position.entry_price,

            "stop_loss": position.stop_loss,

            "tp1": position.take_profit_1,

            "tp2": position.take_profit_2,

            "tp3": position.take_profit_3,

            "profit": position.unrealized_profit,

            "profit_percent": position.unrealized_percent,

            "health": position.health_score,

            "reason": position.close_reason,

            "strategy": position.strategy,

            "signal_score": position.signal_score,

            "market_structure": position.market_structure,

            "open_time": position.open_time,

            "close_time": datetime.utcnow(),

            "result": result

        }

        self.database.save_trade_journal(

            journal

        )

    # =====================================================
    # LEARNING ENGINE
    # =====================================================

    def send_to_learning(

        self,

        position,

        result

    ):

        if self.learning_engine is None:

            return

        self.learning_engine.learn(

            position,

            result

        )

    # =====================================================
    # NEWS MEMORY
    # =====================================================

    def save_news_effect(

        self,

        position,

        analysis

    ):

        if "news_id" not in analysis:

            return

        self.database.save_news_effect(

            news_id=analysis["news_id"],

            symbol=position.symbol,

            profit=position.unrealized_profit,

            health=position.health_score

        )

    # =====================================================
    # SIGNAL REPORT
    # =====================================================

    def build_signal_report(

        self,

        position

    ):

        report = {

            "symbol": position.symbol,

            "side": position.side,

            "entry": position.entry_price,

            "profit": position.unrealized_profit,

            "health": position.health_score,

            "tp1": position.tp1_hit,

            "tp2": position.tp2_hit,

            "tp3": position.tp3_hit,

            "break_even": position.break_even,

            "trailing": position.trailing_active

        }

        return report

    # =====================================================
    # BALE REPORT
    # =====================================================

    def send_bale_update(

        self,

        position

    ):

        report = self.build_signal_report(

            position

        )

        self.reporter.send_position_update(

            report

        )

    # =====================================================
    # AFTER CLOSE
    # =====================================================

    def after_close(

        self,

        position,

        result,

        analysis=None

    ):

        self.write_trade_journal(

            position,

            result

        )

        self.send_to_learning(

            position,

            result

        )

        if analysis:

            self.save_news_effect(

                position,

                analysis

            )

        self.send_bale_update(

            position

        )
    # =====================================================
    # SYNC DATABASE
    # =====================================================

    def sync_database(
        self,
        position
    ):

        try:

            self.database.update_position(

                position

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # SYNC LEARNING ENGINE
    # =====================================================

    def sync_learning_engine(

        self,

        position,

        analysis

    ):

        if self.learning_engine is None:

            return

        try:

            self.learning_engine.update_trade(

                position,

                analysis

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # SYNC BALE
    # =====================================================

    def sync_bale(

        self,

        position

    ):

        try:

            report = self.build_signal_report(

                position

            )

            self.reporter.send_position_update(

                report

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # SYNC JOURNAL
    # =====================================================

    def sync_journal(

        self,

        position

    ):

        try:

            self.database.update_trade_journal(

                symbol=position.symbol,

                profit=position.unrealized_profit,

                health=position.health_score,

                last_update=datetime.utcnow()

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # COMPLETE SYNC
    # =====================================================

    def synchronize_position(

        self,

        position,

        analysis

    ):

        self.sync_database(

            position

        )

        self.sync_learning_engine(

            position,

            analysis

        )

        self.sync_journal(

            position

        )

        self.sync_bale(

            position
        )

    # =====================================================
    # SYNC ALL
    # =====================================================

    def synchronize_all(

        self,

        analysis_map

    ):

        for symbol in self.positions:

            if symbol not in analysis_map:

                continue

            self.synchronize_position(

                self.positions[symbol],

                analysis_map[symbol]

            )
    # =====================================================
    # SAFE DATABASE SAVE
    # =====================================================

    def safe_save(self, position):

        try:

            self.database.update_position(position)

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # SAFE REPORT
    # =====================================================

    def safe_report(self, report):

        try:

            self.reporter.send_position_update(report)

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # AUTO RECOVERY
    # =====================================================

    def recover_positions(self):

        try:

            positions = self.database.load_open_positions()

            self.positions.clear()

            for p in positions:

                self.positions[p.symbol] = p

            self.logger.info(

                f"Recovered {len(self.positions)} positions"

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # POSITION VALIDATOR
    # =====================================================

    def validate_position(self, position):

        if position.entry_price <= 0:

            return False

        if position.quantity <= 0:

            return False

        if position.side not in [

            "BUY",

            "SELL"

        ]:

            return False

        return True

    # =====================================================
    # CLEAN INVALID POSITIONS
    # =====================================================

    def cleanup_positions(self):

        invalid = []

        for symbol, position in self.positions.items():

            if not self.validate_position(position):

                invalid.append(symbol)

        for symbol in invalid:

            self.logger.warning(

                f"Invalid Position Removed : {symbol}"

            )

            del self.positions[symbol]

    # =====================================================
    # HEARTBEAT
    # =====================================================

    def heartbeat(self):

        self.cleanup_positions()

        for position in self.positions.values():

            self.safe_save(position)

        self.logger.info(

            f"Heartbeat | Open Positions : {len(self.positions)}"

        )

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.logger.info(

            "Saving positions before shutdown..."

        )

        for position in self.positions.values():

            self.safe_save(position)

        self.logger.info(

            "Position Manager Stopped."

        )