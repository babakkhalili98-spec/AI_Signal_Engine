"""
Metrics - R&D specific metrics for research and analysis.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class RnDMetrics:
    """
    Metrics for R&D analysis.
    
    Focuses on market behavior analysis rather than trading performance.
    """
    
    # Signal statistics
    total_signals: int = 0
    buy_signals: int = 0
    sell_signals: int = 0
    neutral_signals: int = 0
    
    # Outcome statistics (based on price movement after signal)
    successful_signals: int = 0
    failed_signals: int = 0
    neutral_outcomes: int = 0
    
    # Price movement metrics
    average_favorable_excursion: float = 0.0  # % 
    average_adverse_excursion: float = 0.0  # %
    max_favorable_excursion: float = 0.0  # %
    max_adverse_excursion: float = 0.0  # %
    
    # Time-based metrics
    average_candles_to_max_favorable: float = 0.0
    average_candles_to_max_adverse: float = 0.0
    
    # Context-specific metrics
    indicator_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    pattern_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    support_resistance_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    market_condition_performance: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Sample tracking
    sample_size_by_timeframe: Dict[str, int] = field(default_factory=dict)
    sample_size_by_market: Dict[str, int] = field(default_factory=dict)
    sample_size_by_asset: Dict[str, int] = field(default_factory=dict)
    
    def add_signal_result(
        self,
        direction: str,
        final_outcome: str,
        favorable_excursion: Optional[float],
        adverse_excursion: Optional[float],
        candles_to_favorable: Optional[int],
        candles_to_adverse: Optional[int],
        timeframe: str,
        market: str,
        asset: str,
        indicators: List[str],
        patterns: List[str],
        market_condition: str,
    ):
        """Add a signal result to metrics"""
        self.total_signals += 1
        
        if direction.lower() == "buy" or direction.lower() == "long":
            self.buy_signals += 1
        elif direction.lower() == "sell" or direction.lower() == "short":
            self.sell_signals += 1
        else:
            self.neutral_signals += 1
        
        if final_outcome == "success":
            self.successful_signals += 1
        elif final_outcome == "failure":
            self.failed_signals += 1
        else:
            self.neutral_outcomes += 1
        
        if favorable_excursion is not None:
            self.average_favorable_excursion = (
                (self.average_favorable_excursion * (self.total_signals - 1) + favorable_excursion) / self.total_signals
            )
            if favorable_excursion > self.max_favorable_excursion:
                self.max_favorable_excursion = favorable_excursion
        
        if adverse_excursion is not None:
            self.average_adverse_excursion = (
                (self.average_adverse_excursion * (self.total_signals - 1) + abs(adverse_excursion)) / self.total_signals
            )
            if abs(adverse_excursion) > abs(self.max_adverse_excursion):
                self.max_adverse_excursion = adverse_excursion
        
        if candles_to_favorable is not None:
            self.average_candles_to_max_favorable = (
                (self.average_candles_to_max_favorable * (self.total_signals - 1) + candles_to_favorable) / self.total_signals
            )
        
        if candles_to_adverse is not None:
            self.average_candles_to_max_adverse = (
                (self.average_candles_to_max_adverse * (self.total_signals - 1) + candles_to_adverse) / self.total_signals
            )
        
        # Update timeframe samples
        self.sample_size_by_timeframe[timeframe] = self.sample_size_by_timeframe.get(timeframe, 0) + 1
        
        # Update market samples
        self.sample_size_by_market[market] = self.sample_size_by_market.get(market, 0) + 1
        
        # Update asset samples
        self.sample_size_by_asset[asset] = self.sample_size_by_asset.get(asset, 0) + 1
        
        # Update indicator performance
        for indicator in indicators:
            if indicator not in self.indicator_performance:
                self.indicator_performance[indicator] = {
                    "sample_size": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "neutral_count": 0,
                    "avg_favorable": 0.0,
                    "avg_adverse": 0.0,
                }
            
            perf = self.indicator_performance[indicator]
            perf["sample_size"] += 1
            
            if final_outcome == "success":
                perf["success_count"] += 1
            elif final_outcome == "failure":
                perf["failure_count"] += 1
            else:
                perf["neutral_count"] += 1
            
            if favorable_excursion is not None:
                perf["avg_favorable"] = (perf["avg_favorable"] * (perf["sample_size"] - 1) + favorable_excursion) / perf["sample_size"]
            
            if adverse_excursion is not None:
                perf["avg_adverse"] = (perf["avg_adverse"] * (perf["sample_size"] - 1) + abs(adverse_excursion)) / perf["sample_size"]
        
        # Update pattern performance
        for pattern in patterns:
            if pattern not in self.pattern_performance:
                self.pattern_performance[pattern] = {
                    "sample_size": 0,
                    "success_count": 0,
                    "failure_count": 0,
                    "neutral_count": 0,
                    "avg_favorable": 0.0,
                    "avg_adverse": 0.0,
                }
            
            perf = self.pattern_performance[pattern]
            perf["sample_size"] += 1
            
            if final_outcome == "success":
                perf["success_count"] += 1
            elif final_outcome == "failure":
                perf["failure_count"] += 1
            else:
                perf["neutral_count"] += 1
        
        # Update market condition performance
        if market_condition not in self.market_condition_performance:
            self.market_condition_performance[market_condition] = {
                "sample_size": 0,
                "success_count": 0,
                "failure_count": 0,
                "neutral_count": 0,
            }
        
        perf = self.market_condition_performance[market_condition]
        perf["sample_size"] += 1
        
        if final_outcome == "success":
            perf["success_count"] += 1
        elif final_outcome == "failure":
            perf["failure_count"] += 1
        else:
            perf["neutral_count"] += 1
    
    @property
    def success_rate(self) -> float:
        """Calculate overall success rate"""
        if self.total_signals == 0:
            return 0.0
        return self.successful_signals / self.total_signals
    
    @property
    def failure_rate(self) -> float:
        """Calculate overall failure rate"""
        if self.total_signals == 0:
            return 0.0
        return self.failed_signals / self.total_signals
    
    def get_indicator_stats(self, indicator_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific indicator"""
        return self.indicator_performance.get(indicator_name)
    
    def get_pattern_stats(self, pattern_name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific pattern"""
        return self.pattern_performance.get(pattern_name)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_signals": self.total_signals,
            "buy_signals": self.buy_signals,
            "sell_signals": self.sell_signals,
            "neutral_signals": self.neutral_signals,
            "successful_signals": self.successful_signals,
            "failed_signals": self.failed_signals,
            "neutral_outcomes": self.neutral_outcomes,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "average_favorable_excursion": self.average_favorable_excursion,
            "average_adverse_excursion": self.average_adverse_excursion,
            "max_favorable_excursion": self.max_favorable_excursion,
            "max_adverse_excursion": self.max_adverse_excursion,
            "average_candles_to_max_favorable": self.average_candles_to_max_favorable,
            "average_candles_to_max_adverse": self.average_candles_to_max_adverse,
            "indicator_performance": self.indicator_performance,
            "pattern_performance": self.pattern_performance,
            "support_resistance_performance": self.support_resistance_performance,
            "market_condition_performance": self.market_condition_performance,
            "sample_size_by_timeframe": self.sample_size_by_timeframe,
            "sample_size_by_market": self.sample_size_by_market,
            "sample_size_by_asset": self.sample_size_by_asset,
        }
