"""
=========================================================
AI Signal Engine
Telegram / Bale Formatter
Version : 2.0
=========================================================
"""


class TelegramFormatter:

    def __init__(

        self,

        config,

        logger

    ):

        self.config = config

        self.logger = logger

    # =====================================================
    # FORMAT
    # =====================================================

    def format(

        self,

        report

    ):

        message = []

        message.extend(

            self.build_header(report)

        )

        message.extend(

            self.build_trade(report)

        )

        message.extend(

            self.build_score(report)

        )

        message.extend(

            self.build_market(report)

        )

        message.extend(

            self.build_news(report)

        )

        message.extend(

            self.build_warning(report)

        )

        message.extend(

            self.build_footer(report)

        )

        return "\n".join(message)
    # =====================================================
    # TRADE
    # =====================================================

    def build_trade(

        self,

        report

    ):

        trade = report["trade"]

        lines = [

            "━━━━━━━━━━━━━━━━━━━━",

            "💰 TRADE",

            "",

            f"🎯 Entry : {trade['entry']}",

            f"🛑 Stop Loss : {trade['stop_loss']}",

            "",

            f"🥇 TP1 : {trade['take_profit_1']}",

            f"🥈 TP2 : {trade['take_profit_2']}",

            f"🥉 TP3 : {trade['take_profit_3']}",

            "",

            f"⚖️ Risk / Reward : {trade['risk_reward']}",

            ""

        ]

        return lines
    # =====================================================
    # SCORE
    # =====================================================

    def build_score(

        self,

        report

    ):

        score = report["score"]

        lines = [

            "━━━━━━━━━━━━━━━━━━━━",

            "📊 AI SCORE",

            "",

            f"⭐ Final Score : {score['confidence']}/100",

            f"🏆 Rank : {score['rank']}",

            f"📈 Signal Quality : {score['quality']}",

            f"⚖️ Risk / Reward : {report['trade']['risk_reward']}",

            ""

        ]

        return lines
    # =====================================================
    # MARKET
    # =====================================================

    def build_market(

        self,

        report

    ):

        market = report["market"]

        lines = [

            "━━━━━━━━━━━━━━━━━━━━",

            "🌍 MARKET STATUS",

            "",

            f"📈 Trend : {market['trend']}",

            f"🧬 Market DNA : {market['market_phase']}",

            f"📊 Volume : {market['volume']}",

            f"📉 Volatility : {market['volatility']}",

            f"📡 Spread : {market['spread']}",

            f"🌊 Noise : {market['noise_level']}",

            ""

        ]

        return lines
    # =====================================================
    # NEWS
    # =====================================================

    def build_news(

        self,

        report

    ):

        news = report.get(

            "news",

            {}

        )

        if not news:

            return []

        lines = [

            "━━━━━━━━━━━━━━━━━━━━",

            "📰 NEWS",

            ""

        ]

        if news.get("upcoming"):

            lines.extend([

                f"⏰ Next News : {news['name']}",

                f"🕒 Time : {news['time']}",

                f"⭐ Importance : {news['importance']}",

                f"⌛ Remaining : {news['remaining']}",

                ""

            ])

        if news.get("released"):

            lines.extend([

                f"📢 Result : {news['actual']}",

                f"📊 Forecast : {news['forecast']}",

                f"📈 Previous : {news['previous']}",

                f"🎯 Market Impact : {news['impact']}",

                f"⌛ Estimated Effect : {news['effect_duration']}",

                ""

            ])

        return lines
    # =====================================================
    # FOOTER
    # =====================================================

    def build_footer(

        self,

        report

    ):

        metadata = report.get(

            "metadata",

            {}

        )

        lines = [

            "━━━━━━━━━━━━━━━━━━━━",

            f"🆔 Report ID : {report['report_id']}",

            f"🤖 Engine : AI Signal Engine V{metadata.get('engine_version','1.0.0')}",

            f"📅 Generated : {metadata.get('generated_time','')}",

            f"📡 Market : {metadata.get('market','CRYPTO')}",

            "",

            "⚠ این گزارش توسط هوش مصنوعی تولید شده است.",

            "مدیریت سرمایه و مدیریت ریسک الزامی است.",

            ""

        ]

        return lines