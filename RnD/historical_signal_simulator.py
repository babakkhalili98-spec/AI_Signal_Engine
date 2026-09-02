"""
Historical Signal Simulator - Simulates signal generation on historical data.

This module walks through historical market data and simulates what signals
the Signal Engine would have generated at each point in time, without
look-ahead bias.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class HistoricalSignal:
    """
    A signal generated during historical simulation.
    
    Attributes:
        symbol: Trading symbol
        market: Market name
        asset_class: Asset class
        timeframe: Timeframe
        timestamp: When the signal was generated
        direction: LONG/SHORT/NEUTRAL
        entry_price: Entry price at signal time
        indicators: Indicators that contributed to signal
        patterns: Patterns detected
        score: Signal score
        reasons: Reasons for signal
        market_context: Market conditions at signal time
        dominance_context: Dominance data (if available)
        smart_money_context: Smart money data (if available)
        news_context: News warnings (if any)
    """
    symbol: str
    market: str
    asset_class: str
    timeframe: str
    timestamp: datetime
    direction: str
    entry_price: float
    indicators: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)
    market_context: Dict[str, Any] = field(default_factory=dict)
    dominance_context: Optional[Dict[str, Any]] = None
    smart_money_context: Optional[Dict[str, Any]] = None
    news_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "market": self.market,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp.isoformat(),
            "direction": self.direction,
            "entry_price": self.entry_price,
            "indicators": self.indicators,
            "patterns": self.patterns,
            "score": self.score,
            "reasons": self.reasons,
            "market_context": self.market_context,
            "dominance_context": self.dominance_context,
            "smart_money_context": self.smart_money_context,
            "news_context": self.news_context,
        }


class HistoricalSignalSimulator:
    """
    Simulates signal generation on historical data.
    
    IMPORTANT: This simulator strictly avoids look-ahead bias.
    At timestamp T, only data available at or before T is used.
    """
    
    def __init__(self, signal_engine_callable: Optional[Callable] = None):
        """
        Initialize the simulator.
        
        Args:
            signal_engine_callable: Optional callable that generates signals.
                                    If None, signals must be generated manually.
        """
        self.signal_engine_callable = signal_engine_callable
        self.signals_generated: List[HistoricalSignal] = []
        self.candles_processed = 0
        self.lookahead_bias_checks = 0
        self.lookahead_bias_violations = 0
    
    def simulate(
        self,
        candles: List[Dict[str, Any]],
        symbol: str,
        market: str,
        asset_class: str,
        timeframe: str,
        signal_generator: Optional[Callable] = None,
    ) -> List[HistoricalSignal]:
        """
        Run historical simulation on candle data.
        
        Args:
            candles: List of candle data dictionaries (sorted by timestamp)
            symbol: Trading symbol
            market: Market name
            asset_class: Asset class
            timeframe: Timeframe
            signal_generator: Function to generate signals. 
                             Takes (candles_up_to_t, current_candle) and returns signal info.
        
        Returns:
            List of HistoricalSignal objects
        
        The signal_generator function signature:
            def generate_signal(historical_candles: List[Dict], current_candle: Dict) -> Optional[Dict]
            
            Where the returned dict contains:
                - direction: "buy", "sell", or "neutral"
                - entry_price: float
                - indicators: List[str]
                - patterns: List[str]
                - score: float
                - reasons: List[str]
        """
        if not candles:
            logger.warning("No candles provided for simulation")
            return []
        
        # Ensure candles are sorted by timestamp
        sorted_candles = sorted(candles, key=lambda x: x.get("timestamp", ""))
        
        self.signals_generated = []
        self.candles_processed = 0
        
        generator = signal_generator or self.signal_engine_callable
        
        if not generator:
            logger.error("No signal generator provided")
            return []
        
        # Walk through candles chronologically
        for i, current_candle in enumerate(sorted_candles):
            # Get all candles up to and including current (NO FUTURE DATA)
            historical_candles = sorted_candles[:i + 1]
            
            # Generate signal using only historical data
            try:
                signal_info = generator(historical_candles, current_candle)
                
                if signal_info and signal_info.get("direction", "neutral").lower() != "neutral":
                    # Create HistoricalSignal object
                    hist_signal = HistoricalSignal(
                        symbol=symbol,
                        market=market,
                        asset_class=asset_class,
                        timeframe=timeframe,
                        timestamp=self._parse_timestamp(current_candle.get("timestamp")),
                        direction=signal_info.get("direction", "neutral"),
                        entry_price=signal_info.get("entry_price", current_candle.get("close", 0)),
                        indicators=signal_info.get("indicators", []),
                        patterns=signal_info.get("patterns", []),
                        score=signal_info.get("score", 0.0),
                        reasons=signal_info.get("reasons", []),
                        market_context=signal_info.get("market_context", {}),
                        dominance_context=signal_info.get("dominance_context"),
                        smart_money_context=signal_info.get("smart_money_context"),
                        news_context=signal_info.get("news_context"),
                    )
                    
                    self.signals_generated.append(hist_signal)
                
                self.candles_processed += 1
                
            except Exception as e:
                logger.error(f"Error generating signal at candle {i}: {e}")
                continue
        
        logger.info(f"Simulation complete: {len(self.signals_generated)} signals from {self.candles_processed} candles")
        return self.signals_generated
    
    def _parse_timestamp(self, timestamp) -> datetime:
        """Parse timestamp from various formats"""
        if isinstance(timestamp, datetime):
            return timestamp
        
        if isinstance(timestamp, str):
            try:
                return datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                pass
            
            try:
                return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            except:
                pass
        
        if isinstance(timestamp, (int, float)):
            # Unix timestamp
            return datetime.fromtimestamp(timestamp)
        
        return datetime.utcnow()
    
    def check_lookahead_bias(
        self,
        signal_time: datetime,
        data_used_time: datetime,
        context: str = ""
    ):
        """
        Check for potential look-ahead bias.
        
        Args:
            signal_time: Time when signal was generated
            data_used_time: Time of data used in analysis
            context: Context description for logging
        """
        self.lookahead_bias_checks += 1
        
        if data_used_time > signal_time:
            self.lookahead_bias_violations += 1
            logger.error(
                f"LOOK-AHEAD BIAS DETECTED: {context} - "
                f"Signal at {signal_time} used data from {data_used_time}"
            )
            return False
        
        return True
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get simulation statistics"""
        buy_signals = sum(1 for s in self.signals_generated if s.direction.lower() in ["buy", "long"])
        sell_signals = sum(1 for s in self.signals_generated if s.direction.lower() in ["sell", "short"])
        
        return {
            "total_signals": len(self.signals_generated),
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "candles_processed": self.candles_processed,
            "signals_per_candle": len(self.signals_generated) / self.candles_processed if self.candles_processed > 0 else 0,
            "lookahead_bias_checks": self.lookahead_bias_checks,
            "lookahead_bias_violations": self.lookahead_bias_violations,
        }
