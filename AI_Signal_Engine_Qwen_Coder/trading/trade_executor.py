"""
=========================================================
AI Signal Engine
Trade Executor
Version : 2.0
=========================================================
"""

from datetime import datetime
from typing import Optional


class TradeExecutor:

   def __init__(
       self,
       exchange,
       database,
       position_manager,
       risk_manager,
       reporter,
       logger,
       learning_engine=None,
       journal_manager=None,
       performance_analyzer=None,
       notification_manager=None
    ):

        self.exchange = exchange

        self.database = database

        self.position_manager = position_manager

        self.risk_manager = risk_manager

        self.reporter = reporter

        self.logger = logger

        self.learning_engine = learning_engine

        self.active_orders = {}

        self.pending_orders = {}

        self.failed_orders = {}

    # =====================================================
    # EXCHANGE
    # =====================================================

    def exchange_name(self):

        return self.exchange.name()

    # =====================================================
    # CONNECTED
    # =====================================================

    def connected(self):

        return self.exchange.is_connected()

    # =====================================================
    # ACCOUNT
    # =====================================================

    def account(self):

        return self.exchange.account_info()

    # =====================================================
    # BALANCE
    # =====================================================

    def balance(self):

        account = self.account()

        return account.get(

            "balance",

            0

        )

    # =====================================================
    # FREE BALANCE
    # =====================================================

    def free_balance(self):

        account = self.account()

        return account.get(

            "free_balance",

            0

        )

    # =====================================================
    # CONNECTION CHECK
    # =====================================================

    def check_connection(self):

        if not self.connected():

            self.logger.error(

                "Exchange Disconnected"

            )

            return False

        return True

    # =====================================================
    # RISK CHECK
    # =====================================================

    def risk_check(

        self,

        signal

    ):

        account = self.account()

        return self.risk_manager.request_trade(

            signal,

            account

        )

    # =====================================================
    # REGISTER ORDER
    # =====================================================

    def register_order(

        self,

        order_id,

        order

    ):

        self.active_orders[

            order_id

        ] = order

    # =====================================================
    # REMOVE ORDER
    # =====================================================

    def unregister_order(

        self,

        order_id

    ):

        if order_id in self.active_orders:

            del self.active_orders[

                order_id

            ]

    # =====================================================
    # PENDING
    # =====================================================

    def add_pending(

        self,

        order

    ):

        self.pending_orders[

            order.symbol

        ] = order

    # =====================================================
    # FAILED
    # =====================================================

    def add_failed(

        self,

        order

    ):

        self.failed_orders[

            order.symbol

        ] = {

            "time": datetime.utcnow(),

            "order": order

        }

    # =====================================================
    # HEARTBEAT
    # =====================================================

    def heartbeat(self):

        self.logger.info(

            f"Executor "

            f"Active:{len(self.active_orders)} "

            f"Pending:{len(self.pending_orders)} "

            f"Failed:{len(self.failed_orders)}"

        )
    # =====================================================
    # MARKET ORDER
    # =====================================================

    def execute_market_order(
        self,
        package
    ):

        try:

            result = self.exchange.market_order(

                symbol=package["symbol"],

                side=package["side"],

                quantity=package["quantity"]

            )

            return result

        except Exception as e:

            self.logger.exception(e)

            return None

    # =====================================================
    # LIMIT ORDER
    # =====================================================

    def execute_limit_order(
        self,
        package
    ):

        try:

            result = self.exchange.limit_order(

                symbol=package["symbol"],

                side=package["side"],

                quantity=package["quantity"],

                price=package["entry"]

            )

            return result

        except Exception as e:

            self.logger.exception(e)

            return None

    # =====================================================
    # STOP ORDER
    # =====================================================

    def execute_stop_order(
        self,
        package
    ):

        try:

            result = self.exchange.stop_order(

                symbol=package["symbol"],

                side=package["side"],

                quantity=package["quantity"],

                stop_price=package["stop_loss"]

            )

            return result

        except Exception as e:

            self.logger.exception(e)

            return None

    # =====================================================
    # RETRY ORDER
    # =====================================================

    def retry_order(
        self,
        package,
        retries=3
    ):

        for attempt in range(retries):

            result = self.execute_market_order(

                package

            )

            if result:

                return result

            self.logger.warning(

                f"Retry {attempt+1}/{retries}"

            )

        return None

    # =====================================================
    # EXECUTE ORDER
    # =====================================================

    def execute_order(
        self,
        package,
        order_type="market"
    ):

        if order_type == "market":

            return self.execute_market_order(

                package

            )

        if order_type == "limit":

            return self.execute_limit_order(

                package

            )

        if order_type == "stop":

            return self.execute_stop_order(

                package

            )

        raise ValueError(

            f"Unknown order type: {order_type}"

        )

    # =====================================================
    # SAFE EXECUTION
    # =====================================================

    def safe_execute(
        self,
        package,
        order_type="market"
    ):

        result = self.execute_order(

            package,

            order_type

        )

        if result is None:

            self.logger.warning(

                "Primary execution failed. Retrying..."

            )

            result = self.retry_order(

                package

            )

        return result

    # =====================================================
    # CANCEL ORDER
    # =====================================================

    def cancel_order(
        self,
        order_id
    ):

        try:

            return self.exchange.cancel_order(

                order_id

            )

        except Exception as e:

            self.logger.exception(e)

            return False
    # =====================================================
    # CREATE POSITION
    # =====================================================

    def create_position(
        self,
        package,
        order_result
    ):

        position = {

            "order_id": order_result["order_id"],

            "symbol": package["symbol"],

            "side": package["side"],

            "entry_price": order_result["filled_price"],

            "quantity": package["quantity"],

            "stop_loss": package["stop_loss"],

            "take_profit_1": package["take_profit_1"],

            "take_profit_2": package["take_profit_2"],

            "take_profit_3": package["take_profit_3"],

            "leverage": package.get("leverage", 1),

            "margin": package.get("required_margin", 0),

            "fee": package.get("estimated_fee", 0),

            "signal_score": package.get("signal_score", 0),

            "risk_score": package.get("risk_score", 0),

            "risk_reward": package.get("risk_reward", 0),

            "status": "OPEN",

            "open_time": datetime.utcnow()

        }

        return position

    # =====================================================
    # SAVE POSITION
    # =====================================================

    def save_position(
        self,
        position
    ):

        try:

            self.database.save_position(

                position

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # REGISTER POSITION
    # =====================================================

    def register_position(
        self,
        position
    ):

        self.position_manager.add_position(

            position

        )

    # =====================================================
    # SAVE ORDER
    # =====================================================

    def save_order(
        self,
        order_result
    ):

        try:

            self.database.save_order(

                order_result

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # PROCESS EXECUTION
    # =====================================================

    def process_execution(
        self,
        package,
        order_result
    ):

        position = self.create_position(

            package,

            order_result

        )

        self.save_order(

            order_result

        )

        self.save_position(

            position

        )

        self.register_position(

            position

        )

        self.register_order(

            order_result["order_id"],

            position

        )

        return position

    # =====================================================
    # COMPLETE EXECUTION
    # =====================================================

    def complete_execution(
        self,
        package,
        order_type="market"
    ):

        result = self.safe_execute(

            package,

            order_type

        )

        if result is None:

            return None

        position = self.process_execution(

            package,

            result

        )

        return position
    # =====================================================
    # SEND REPORT
    # =====================================================

    def send_report(
        self,
        position
    ):

        try:

            if self.reporter:

                self.reporter.send_position_update(

                    position

                )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # SAVE JOURNAL
    # =====================================================

    def save_journal(
        self,
        position
    ):

        if self.journal_manager is None:

            return

        try:

            self.journal_manager.save_trade(

                position

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # UPDATE LEARNING
    # =====================================================

    def update_learning(
        self,
        position
    ):

        if self.learning_engine is None:

            return

        try:

            self.learning_engine.after_open(

                position

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def update_performance(
        self,
        position
    ):

        if self.performance_analyzer is None:

            return

        try:

            self.performance_analyzer.new_trade(

                position

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # NOTIFICATION
    # =====================================================

    def notify(
        self,
        position
    ):

        if self.notification_manager is None:

            return

        try:

            self.notification_manager.trade_opened(

                position

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # AFTER EXECUTION
    # =====================================================

    def after_execution(
        self,
        position
    ):

        self.send_report(

            position

        )

        self.save_journal(

            position

        )

        self.update_learning(

            position

        )

        self.update_performance(

            position

        )

        self.notify(

            position

        )

    # =====================================================
    # EXECUTE SIGNAL
    # =====================================================

    def execute_signal(
        self,
        signal,
        order_type="market"
    ):

        if not self.check_connection():

            return None

        package = self.risk_check(

            signal

        )

        if not package["allow_trade"]:

            self.logger.info(

                package["reason"]

            )

            return None

        position = self.complete_execution(

            package,

            order_type

        )

        if position:

            self.after_execution(

                position

            )

        return position

    # =====================================================
    # RECOVER ORDERS
    # =====================================================

    def recover_orders(self):

        try:

            orders = self.database.load_open_orders()

            for order in orders:

                self.active_orders[

                    order["order_id"]

                ] = order

            self.logger.info(

                f"Recovered {len(orders)} open orders."

            )

        except Exception as e:

            self.logger.exception(e)

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(self):

        self.logger.info(

            "Trade Executor Shutdown"

        )

        self.active_orders.clear()

        self.pending_orders.clear()

        self.failed_orders.clear()