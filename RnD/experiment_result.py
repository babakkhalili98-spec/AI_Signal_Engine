"""
Experiment Result - Stores results of individual experiments.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid


class ExperimentStatus(Enum):
    """Status of an experiment"""
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    INVALIDATED = "invalidated"


class ConfidenceLevel(Enum):
    """Confidence levels for research findings"""
    INSUFFICIENT_SAMPLE = "insufficient_sample"
    LOW_CONFIDENCE = "low_confidence"
    MEDIUM_CONFIDENCE = "medium_confidence"
    HIGH_CONFIDENCE = "high_confidence"
    STATISTICALLY_RELEVANT = "statistically_relevant_sample"


@dataclass
class SignalOutcome:
    """Outcome of a single signal in backtest"""
    timestamp: datetime
    direction: str
    entry_price: float
    outcome_after_1candle: Optional[float] = None  # % change
    outcome_after_3candles: Optional[float] = None
    outcome_after_5candles: Optional[float] = None
    outcome_after_10candles: Optional[float] = None
    outcome_after_20candles: Optional[float] = None
    max_favorable_excursion: Optional[float] = None  # % 
    max_adverse_excursion: Optional[float] = None  # %
    candles_to_max_favorable: Optional[int] = None
    candles_to_max_adverse: Optional[int] = None
    final_outcome: str = "unknown"  # success, failure, neutral
    indicators_used: List[str] = field(default_factory=list)
    patterns_detected: List[str] = field(default_factory=list)
    market_context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExperimentResult:
    """
    Result of a single R&D experiment.
    
    Attributes:
        experiment_id: Unique identifier (e.g., EXP-000001)
        hypothesis: What was being tested
        date_created: When experiment was created
        market: Market name (e.g., CRYPTO, FOREX)
        symbol: Symbol tested (e.g., BTCUSDT)
        asset_class: Asset class
        timeframe: Timeframe tested
        indicator: Indicator being tested (if applicable)
        old_parameters: Previous parameters (if optimization)
        new_parameters: New parameters tested
        sample_size: Number of signals analyzed
        signal_outcomes: List of individual signal outcomes
        metrics: Calculated metrics
        conclusion: Summary conclusion
        confidence: Confidence level based on sample size
        status: Current status
        limitations: Known limitations
        updated_at: Last update timestamp
    """
    
    experiment_id: str = field(default_factory=lambda: f"EXP-{datetime.utcnow().strftime('%Y%m%d')}-000001")
    hypothesis: str = ""
    date_created: datetime = field(default_factory=datetime.utcnow)
    market: str = ""
    symbol: str = ""
    asset_class: str = ""
    timeframe: str = ""
    indicator: Optional[str] = None
    old_parameters: Optional[Dict[str, Any]] = None
    new_parameters: Optional[Dict[str, Any]] = None
    sample_size: int = 0
    signal_outcomes: List[SignalOutcome] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    conclusion: str = ""
    confidence: ConfidenceLevel = ConfidenceLevel.INSUFFICIENT_SAMPLE
    status: ExperimentStatus = ExperimentStatus.PLANNED
    limitations: List[str] = field(default_factory=list)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def add_signal_outcome(self, outcome: SignalOutcome):
        """Add a signal outcome to the experiment"""
        self.signal_outcomes.append(outcome)
        self.sample_size = len(self.signal_outcomes)
        self.updated_at = datetime.utcnow()
        self._update_confidence()
    
    def _update_confidence(self):
        """Update confidence level based on sample size"""
        if self.sample_size < 30:
            self.confidence = ConfidenceLevel.INSUFFICIENT_SAMPLE
        elif self.sample_size < 100:
            self.confidence = ConfidenceLevel.LOW_CONFIDENCE
        elif self.sample_size < 300:
            self.confidence = ConfidenceLevel.MEDIUM_CONFIDENCE
        elif self.sample_size < 1000:
            self.confidence = ConfidenceLevel.HIGH_CONFIDENCE
        else:
            self.confidence = ConfidenceLevel.STATISTICALLY_RELEVANT
    
    def calculate_metrics(self):
        """Calculate aggregate metrics from signal outcomes"""
        if not self.signal_outcomes:
            return
        
        successes = sum(1 for o in self.signal_outcomes if o.final_outcome == "success")
        failures = sum(1 for o in self.signal_outcomes if o.final_outcome == "failure")
        neutrals = sum(1 for o in self.signal_outcomes if o.final_outcome == "neutral")
        
        favorable_moves = [o.max_favorable_excursion for o in self.signal_outcomes if o.max_favorable_excursion is not None]
        adverse_moves = [o.max_adverse_excursion for o in self.signal_outcomes if o.max_adverse_excursion is not None]
        
        self.metrics = {
            "total_signals": self.sample_size,
            "success_count": successes,
            "failure_count": failures,
            "neutral_count": neutrals,
            "success_rate": successes / self.sample_size if self.sample_size > 0 else 0,
            "failure_rate": failures / self.sample_size if self.sample_size > 0 else 0,
            "average_favorable_move": sum(favorable_moves) / len(favorable_moves) if favorable_moves else 0,
            "average_adverse_move": sum(adverse_moves) / len(adverse_moves) if adverse_moves else 0,
            "avg_candles_to_max_favorable": sum(o.candles_to_max_favorable for o in self.signal_outcomes if o.candles_to_max_favorable) / len([o for o in self.signal_outcomes if o.candles_to_max_favorable]) if any(o.candles_to_max_favorable for o in self.signal_outcomes) else 0,
        }
        
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "experiment_id": self.experiment_id,
            "hypothesis": self.hypothesis,
            "date_created": self.date_created.isoformat(),
            "market": self.market,
            "symbol": self.symbol,
            "asset_class": self.asset_class,
            "timeframe": self.timeframe,
            "indicator": self.indicator,
            "old_parameters": self.old_parameters,
            "new_parameters": self.new_parameters,
            "sample_size": self.sample_size,
            "signal_outcomes": [
                {
                    "timestamp": o.timestamp.isoformat(),
                    "direction": o.direction,
                    "entry_price": o.entry_price,
                    "outcome_after_1candle": o.outcome_after_1candle,
                    "outcome_after_3candles": o.outcome_after_3candles,
                    "outcome_after_5candles": o.outcome_after_5candles,
                    "outcome_after_10candles": o.outcome_after_10candles,
                    "outcome_after_20candles": o.outcome_after_20candles,
                    "max_favorable_excursion": o.max_favorable_excursion,
                    "max_adverse_excursion": o.max_adverse_excursion,
                    "candles_to_max_favorable": o.candles_to_max_favorable,
                    "candles_to_max_adverse": o.candles_to_max_adverse,
                    "final_outcome": o.final_outcome,
                    "indicators_used": o.indicators_used,
                    "patterns_detected": o.patterns_detected,
                    "market_context": o.market_context,
                }
                for o in self.signal_outcomes
            ],
            "metrics": self.metrics,
            "conclusion": self.conclusion,
            "confidence": self.confidence.value,
            "status": self.status.value,
            "limitations": self.limitations,
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentResult":
        """Create from dictionary"""
        data["date_created"] = datetime.fromisoformat(data["date_created"])
        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        data["confidence"] = ConfidenceLevel(data["confidence"])
        data["status"] = ExperimentStatus(data["status"])
        data["signal_outcomes"] = [
            SignalOutcome(
                timestamp=datetime.fromisoformat(o["timestamp"]),
                direction=o["direction"],
                entry_price=o["entry_price"],
                outcome_after_1candle=o.get("outcome_after_1candle"),
                outcome_after_3candles=o.get("outcome_after_3candles"),
                outcome_after_5candles=o.get("outcome_after_5candles"),
                outcome_after_10candles=o.get("outcome_after_10candles"),
                outcome_after_20candles=o.get("outcome_after_20candles"),
                max_favorable_excursion=o.get("max_favorable_excursion"),
                max_adverse_excursion=o.get("max_adverse_excursion"),
                candles_to_max_favorable=o.get("candles_to_max_favorable"),
                candles_to_max_adverse=o.get("candles_to_max_adverse"),
                final_outcome=o["final_outcome"],
                indicators_used=o.get("indicators_used", []),
                patterns_detected=o.get("patterns_detected", []),
                market_context=o.get("market_context", {}),
            )
            for o in data.get("signal_outcomes", [])
        ]
        return cls(**data)
