"""
==========================================================
AI SIGNAL ENGINE
Risk Management Engine
Version : 8.0
==========================================================
"""

from __future__ import annotations

import logging
from typing import Dict
from typing import Optional


class RiskManagementEngine:

    # =====================================================
    # INIT
    # =====================================================

    def __init__(self):

        self.logger = logging.getLogger("RiskManagementEngine")

        # درصد سرمایه در هر معامله
        self.position_percent = 5

        # حداقل نسبت سود به ضرر
        self.minimum_rr = 1.0

        self.logger.info("RiskManagementEngine Loaded")

    # =====================================================
    # MAIN CALCULATE
    # =====================================================

    def calculate(
        self,
        symbol: str,
        signal: Dict,
        data=None,
    ) -> Optional[Dict]:

        if signal is None:
            return None

        entry = signal.get("entry")
        sl = signal.get("stop_loss")

        tp1 = signal.get("take_profit_1")
        tp2 = signal.get("take_profit_2")
        tp3 = signal.get("take_profit_3")

        if entry is None:
            return None

        if sl is None:
            return None

        risk_distance = abs(entry - sl)

        if risk_distance == 0:
            return None

        rr1 = round(abs(tp1 - entry) / risk_distance, 2) if tp1 else 0
        rr2 = round(abs(tp2 - entry) / risk_distance, 2) if tp2 else 0
        rr3 = round(abs(tp3 - entry) / risk_distance, 2) if tp3 else 0

        return {
            "entry": entry,
            "sl": sl,
            "tp1": tp1,
            "tp2": tp2,
            "tp3": tp3,
            "risk_distance": risk_distance,
            "rr": rr3,
            "rr1": rr1,
            "rr2": rr2,
            "rr3": rr3,
            "position_percent": self.position_percent,
        }
    # =====================================================
    # POSITION SIZE
    # =====================================================

    def calculate_position_size(
        self,
        capital: float,
        entry: float,
        stop_loss: float,
        leverage: float = 1.0,
    ) -> float:

        if capital <= 0:
            return 0

        if entry <= 0:
            return 0

        if stop_loss <= 0:
            return 0

        risk_capital = capital * (self.position_percent / 100)

        distance = abs(entry - stop_loss)

        if distance == 0:
            return 0

        position_value = risk_capital * leverage

        quantity = position_value / entry

        return round(quantity, 8)

    # =====================================================
    # RISK AMOUNT
    # =====================================================

    def calculate_risk_amount(
        self,
        capital: float,
    ) -> float:

        return round(

            capital * self.position_percent / 100,

            2

        )

    # =====================================================
    # VALIDATE RR
    # =====================================================

    def validate_rr(
        self,
        rr: float,
    ) -> bool:

        return rr >= self.minimum_rr

    # =====================================================
    # TRADE SUMMARY
    # =====================================================

    def build_trade_summary(
        self,
        capital: float,
        leverage: float,
        risk: Dict,
    ) -> Dict:

        quantity = self.calculate_position_size(

            capital=capital,

            entry=risk["entry"],

            stop_loss=risk["sl"],

            leverage=leverage,

        )

        risk_amount = self.calculate_risk_amount(

            capital

        )

        summary = {

            "capital": capital,

            "position_percent": self.position_percent,

            "risk_amount": risk_amount,

            "leverage": leverage,

            "quantity": quantity,

            "entry": risk["entry"],

            "sl": risk["sl"],

            "tp1": risk["tp1"],

            "tp2": risk["tp2"],

            "tp3": risk["tp3"],

            "rr": risk["rr"],

            "valid_rr": self.validate_rr(

                risk["rr"]

            ),

        }

        return summary
    # =====================================================
    # TAKE PROFIT
    # =====================================================

    def calculate_take_profits(
        self,
        entry: float,
        stop_loss: float,
        signal: str,
    ):

        risk = abs(entry - stop_loss)

        if signal.upper() == "BUY":

            tp1 = entry + risk * 1.0
            tp2 = entry + risk * 2.0
            tp3 = entry + risk * 3.0

        else:

            tp1 = entry - risk * 1.0
            tp2 = entry - risk * 2.0
            tp3 = entry - risk * 3.0

        return {

            "tp1": round(tp1, 8),
            "tp2": round(tp2, 8),
            "tp3": round(tp3, 8),

        }

    # =====================================================
    # BREAK EVEN
    # =====================================================

    def break_even_price(
        self,
        entry: float,
    ):

        return round(entry, 8)

    # =====================================================
    # TRAILING STOP
    # =====================================================

    def trailing_stop(
        self,
        current_price: float,
        current_stop: float,
        signal: str,
        distance: float,
    ):

        if signal.upper() == "BUY":

            new_stop = current_price - distance

            if new_stop > current_stop:

                return round(new_stop, 8)

            return current_stop

        else:

            new_stop = current_price + distance

            if new_stop < current_stop:

                return round(new_stop, 8)

            return current_stop

    # =====================================================
    # UPDATE RISK
    # =====================================================

    def update_trade(
        self,
        risk: dict,
        current_price: float,
        signal: str,
    ):

        distance = risk["risk_distance"]

        risk["sl"] = self.trailing_stop(

            current_price=current_price,

            current_stop=risk["sl"],

            signal=signal,

            distance=distance,

        )

        return risk

    # =====================================================
    # CHECK STOP LOSS
    # =====================================================

    def stop_hit(
        self,
        signal: str,
        current_price: float,
        stop_loss: float,
    ):

        if signal.upper() == "BUY":

            return current_price <= stop_loss

        return current_price >= stop_loss

    # =====================================================
    # CHECK TAKE PROFIT
    # =====================================================

    def target_hit(
        self,
        signal: str,
        current_price: float,
        target: float,
    ):

        if signal.upper() == "BUY":

            return current_price >= target

        return current_price <= target
    # =====================================================
    # PARTIAL CLOSE
    # =====================================================

    def partial_close_plan(self):

        return [

            {

                "target": "tp1",

                "close_percent": 25,

            },

            {

                "target": "tp2",

                "close_percent": 35,

            },

            {

                "target": "tp3",

                "close_percent": 40,

            },

        ]

    # =====================================================
    # NEXT TARGET
    # =====================================================

    def next_target(self, trade):

        if trade.get("tp1_done") is not True:

            return trade["tp1"]

        if trade.get("tp2_done") is not True:

            return trade["tp2"]

        if trade.get("tp3_done") is not True:

            return trade["tp3"]

        return None

    # =====================================================
    # MARK TARGET
    # =====================================================

    def mark_target(self, trade, target_name):

        trade[target_name + "_done"] = True

        return trade

    # =====================================================
    # CLOSE PERCENT
    # =====================================================

    def close_percent(self, target_name):

        table = {

            "tp1": 25,

            "tp2": 35,

            "tp3": 40,

        }

        return table.get(target_name, 0)

    # =====================================================
    # CHECK TARGET HIT
    # =====================================================

    def check_targets(

        self,

        trade,

        current_price,

        signal,

    ):

        closed = []

        plans = self.partial_close_plan()

        for plan in plans:

            target = plan["target"]

            if trade.get(target + "_done"):

                continue

            price = trade[target]

            if signal.upper() == "BUY":

                hit = current_price >= price

            else:

                hit = current_price <= price

            if hit:

                trade[target + "_done"] = True

                closed.append(

                    {

                        "target": target,

                        "percent": plan["close_percent"],

                        "price": price,

                    }

                )

        return closed

    # =====================================================
    # RESET TRADE
    # =====================================================

    def reset_trade_flags(

        self,

        trade,

    ):

        trade["tp1_done"] = False

        trade["tp2_done"] = False

        trade["tp3_done"] = False

        return trade

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        risk,

    ):

        return {

            "entry": risk["entry"],

            "sl": risk["sl"],

            "tp1": risk["tp1"],

            "tp2": risk["tp2"],

            "tp3": risk["tp3"],

            "rr": risk["rr"],

            "risk_distance": risk["risk_distance"],

        }