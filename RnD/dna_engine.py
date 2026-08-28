"""
DNA Engine - Creates and maintains behavioral profiles for markets/assets.

The DNA Engine builds a "behavioral fingerprint" for each unique combination of:
- Market (e.g., CRYPTO, FOREX)
- Asset/Symbol (e.g., BTCUSDT, EURUSD)
- Timeframe (e.g., 1H, 4H)

This profile captures how that specific asset/timeframe typically reacts to:
- Various indicators
- Patterns
- Support/Resistance levels
- Market conditions
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from .research_database import ResearchDatabase
from .experiment_result import ConfidenceLevel

logger = logging.getLogger(__name__)


@dataclass
class IndicatorReaction:
    """How an asset reacts to a specific indicator"""
    indicator_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    sample_size: int = 0
    success_count: int = 0
    failure_count: int = 0
    neutral_count: int = 0
    average_favorable_move: float = 0.0
    average_adverse_move: float = 0.0
    consistency_score: float = 0.0  # 0-1 scale
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def confidence(self) -> ConfidenceLevel:
        """Get confidence level based on sample size"""
        if self.sample_size < 30:
            return ConfidenceLevel.INSUFFICIENT_SAMPLE
        elif self.sample_size < 100:
            return ConfidenceLevel.LOW_CONFIDENCE
        elif self.sample_size < 300:
            return ConfidenceLevel.MEDIUM_CONFIDENCE
        elif self.sample_size < 1000:
            return ConfidenceLevel.HIGH_CONFIDENCE
        else:
            return ConfidenceLevel.STATISTICALLY_RELEVANT
    
    def update(self, outcome: str, favorable_move: float, adverse_move: float):
        """Update with new observation"""
        self.sample_size += 1
        
        if outcome == "success":
            self.success_count += 1
        elif outcome == "failure":
            self.failure_count += 1
        else:
            self.neutral_count += 1
        
        # Update averages
        self.average_favorable_move = (
            (self.average_favorable_move * (self.sample_size - 1) + favorable_move) / self.sample_size
        )
        self.average_adverse_move = (
            (self.average_adverse_move * (self.sample_size - 1) + abs(adverse_move)) / self.sample_size
        )
        
        # Update consistency score (how predictable the reactions are)
        if self.sample_size > 1:
            total = self.success_count + self.failure_count + self.neutral_count
            # Higher score if one outcome dominates
            max_outcome = max(self.success_count, self.failure_count, self.neutral_count)
            self.consistency_score = max_outcome / total
        
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "indicator_name": self.indicator_name,
            "parameters": self.parameters,
            "sample_size": self.sample_size,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "neutral_count": self.neutral_count,
            "average_favorable_move": self.average_favorable_move,
            "average_adverse_move": self.average_adverse_move,
            "consistency_score": self.consistency_score,
            "confidence": self.confidence.value,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class PatternReaction:
    """How an asset reacts to a specific pattern"""
    pattern_name: str
    pattern_type: str  # candlestick, classic, harmonic, etc.
    sample_size: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_favorable_move: float = 0.0
    average_move_after_pattern: float = 0.0
    confidence: ConfidenceLevel = ConfidenceLevel.INSUFFICIENT_SAMPLE
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update(self, outcome: str, favorable_move: float, move_after: float):
        """Update with new observation"""
        self.sample_size += 1
        
        if outcome == "success":
            self.success_count += 1
        elif outcome == "failure":
            self.failure_count += 1
        
        self.average_favorable_move = (
            (self.average_favorable_move * (self.sample_size - 1) + favorable_move) / self.sample_size
        )
        self.average_move_after_pattern = (
            (self.average_move_after_pattern * (self.sample_size - 1) + move_after) / self.sample_size
        )
        
        # Update confidence
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
        
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pattern_name": self.pattern_name,
            "pattern_type": self.pattern_type,
            "sample_size": self.sample_size,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "average_favorable_move": self.average_favorable_move,
            "average_move_after_pattern": self.average_move_after_pattern,
            "confidence": self.confidence.value,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class SupportResistanceReaction:
    """How an asset reacts to support/resistance levels"""
    level_type: str  # pivot, swing_high, swing_low, fibonacci, round_number, etc.
    sample_size: int = 0
    reaction_count: int = 0  # Price bounced/reversed
    breakout_count: int = 0  # Price broke through
    false_breakout_count: int = 0
    average_reaction_strength: float = 0.0  # % move after reaction
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def update(
        self, 
        outcome: str,  # "reaction", "breakout", "false_breakout"
        reaction_strength: float
    ):
        """Update with new observation"""
        self.sample_size += 1
        
        if outcome == "reaction":
            self.reaction_count += 1
        elif outcome == "breakout":
            self.breakout_count += 1
        elif outcome == "false_breakout":
            self.false_breakout_count += 1
        
        self.average_reaction_strength = (
            (self.average_reaction_strength * (self.sample_size - 1) + abs(reaction_strength)) / self.sample_size
        )
        
        self.last_updated = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "level_type": self.level_type,
            "sample_size": self.sample_size,
            "reaction_count": self.reaction_count,
            "breakout_count": self.breakout_count,
            "false_breakout_count": self.false_breakout_count,
            "average_reaction_strength": self.average_reaction_strength,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class MarketDNA:
    """
    Complete behavioral DNA profile for a market/asset/timeframe combination.
    """
    market: str
    symbol: str
    timeframe: str
    asset_class: str
    
    # Behavioral profiles
    indicator_reactions: Dict[str, IndicatorReaction] = field(default_factory=dict)
    pattern_reactions: Dict[str, PatternReaction] = field(default_factory=dict)
    support_resistance_reactions: Dict[str, SupportResistanceReaction] = field(default_factory=dict)
    
    # General statistics
    total_signals_observed: int = 0
    overall_success_rate: float = 0.0
    average_volatility: float = 0.0
    typical_favorable_move: float = 0.0
    typical_adverse_move: float = 0.0
    
    # Market condition preferences
    best_market_conditions: List[str] = field(default_factory=list)
    worst_market_conditions: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    
    def update_indicator_reaction(
        self,
        indicator_name: str,
        parameters: Dict[str, Any],
        outcome: str,
        favorable_move: float,
        adverse_move: float,
    ):
        """Update indicator reaction profile"""
        key = f"{indicator_name}_{str(parameters)}"
        
        if key not in self.indicator_reactions:
            self.indicator_reactions[key] = IndicatorReaction(
                indicator_name=indicator_name,
                parameters=parameters,
            )
        
        self.indicator_reactions[key].update(outcome, favorable_move, adverse_move)
        self.last_updated = datetime.utcnow()
    
    def update_pattern_reaction(
        self,
        pattern_name: str,
        pattern_type: str,
        outcome: str,
        favorable_move: float,
        move_after: float,
    ):
        """Update pattern reaction profile"""
        key = f"{pattern_name}_{pattern_type}"
        
        if key not in self.pattern_reactions:
            self.pattern_reactions[key] = PatternReaction(
                pattern_name=pattern_name,
                pattern_type=pattern_type,
            )
        
        self.pattern_reactions[key].update(outcome, favorable_move, move_after)
        self.last_updated = datetime.utcnow()
    
    def update_support_resistance_reaction(
        self,
        level_type: str,
        outcome: str,
        reaction_strength: float,
    ):
        """Update support/resistance reaction profile"""
        if level_type not in self.support_resistance_reactions:
            self.support_resistance_reactions[level_type] = SupportResistanceReaction(
                level_type=level_type,
            )
        
        self.support_resistance_reactions[level_type].update(outcome, reaction_strength)
        self.last_updated = datetime.utcnow()
    
    def update_general_stats(
        self,
        outcome: str,
        favorable_move: float,
        adverse_move: float,
        volatility: float,
    ):
        """Update general statistics"""
        self.total_signals_observed += 1
        
        # Update success rate
        if outcome == "success":
            successes = int(self.overall_success_rate * (self.total_signals_observed - 1)) + 1
        else:
            successes = int(self.overall_success_rate * (self.total_signals_observed - 1))
        
        self.overall_success_rate = successes / self.total_signals_observed
        
        # Update volatility
        self.average_volatility = (
            (self.average_volatility * (self.total_signals_observed - 1) + volatility) / self.total_signals_observed
        )
        
        # Update typical moves
        self.typical_favorable_move = (
            (self.typical_favorable_move * (self.total_signals_observed - 1) + favorable_move) / self.total_signals_observed
        )
        self.typical_adverse_move = (
            (self.typical_adverse_move * (self.total_signals_observed - 1) + abs(adverse_move)) / self.total_signals_observed
        )
        
        self.last_updated = datetime.utcnow()
    
    def get_indicator_confidence(self, indicator_name: str, parameters: Optional[Dict] = None) -> str:
        """Get confidence level for an indicator"""
        key = f"{indicator_name}_{str(parameters or {})}"
        reaction = self.indicator_reactions.get(key)
        
        if not reaction:
            return "no_data"
        
        return reaction.confidence.value
    
    def get_pattern_confidence(self, pattern_name: str, pattern_type: str) -> str:
        """Get confidence level for a pattern"""
        key = f"{pattern_name}_{pattern_type}"
        reaction = self.pattern_reactions.get(key)
        
        if not reaction:
            return "no_data"
        
        return reaction.confidence.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "market": self.market,
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "asset_class": self.asset_class,
            "indicator_reactions": {k: v.to_dict() for k, v in self.indicator_reactions.items()},
            "pattern_reactions": {k: v.to_dict() for k, v in self.pattern_reactions.items()},
            "support_resistance_reactions": {k: v.to_dict() for k, v in self.support_resistance_reactions.items()},
            "total_signals_observed": self.total_signals_observed,
            "overall_success_rate": self.overall_success_rate,
            "average_volatility": self.average_volatility,
            "typical_favorable_move": self.typical_favorable_move,
            "typical_adverse_move": self.typical_adverse_move,
            "best_market_conditions": self.best_market_conditions,
            "worst_market_conditions": self.worst_market_conditions,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "version": self.version,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MarketDNA":
        """Create from dictionary"""
        dna = cls(
            market=data["market"],
            symbol=data["symbol"],
            timeframe=data["timeframe"],
            asset_class=data["asset_class"],
            total_signals_observed=data.get("total_signals_observed", 0),
            overall_success_rate=data.get("overall_success_rate", 0.0),
            average_volatility=data.get("average_volatility", 0.0),
            typical_favorable_move=data.get("typical_favorable_move", 0.0),
            typical_adverse_move=data.get("typical_adverse_move", 0.0),
            best_market_conditions=data.get("best_market_conditions", []),
            worst_market_conditions=data.get("worst_market_conditions", []),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            last_updated=datetime.fromisoformat(data["last_updated"]) if "last_updated" in data else datetime.utcnow(),
            version=data.get("version", 1),
        )
        
        # Restore indicator reactions
        for key, ind_data in data.get("indicator_reactions", {}).items():
            dna.indicator_reactions[key] = IndicatorReaction(
                indicator_name=ind_data["indicator_name"],
                parameters=ind_data.get("parameters", {}),
                sample_size=ind_data.get("sample_size", 0),
                success_count=ind_data.get("success_count", 0),
                failure_count=ind_data.get("failure_count", 0),
                neutral_count=ind_data.get("neutral_count", 0),
                average_favorable_move=ind_data.get("average_favorable_move", 0.0),
                average_adverse_move=ind_data.get("average_adverse_move", 0.0),
                consistency_score=ind_data.get("consistency_score", 0.0),
                last_updated=datetime.fromisoformat(ind_data["last_updated"]) if "last_updated" in ind_data else datetime.utcnow(),
            )
        
        # Restore pattern reactions
        for key, pat_data in data.get("pattern_reactions", {}).items():
            dna.pattern_reactions[key] = PatternReaction(
                pattern_name=pat_data["pattern_name"],
                pattern_type=pat_data.get("pattern_type", ""),
                sample_size=pat_data.get("sample_size", 0),
                success_count=pat_data.get("success_count", 0),
                failure_count=pat_data.get("failure_count", 0),
                average_favorable_move=pat_data.get("average_favorable_move", 0.0),
                average_move_after_pattern=pat_data.get("average_move_after_pattern", 0.0),
                confidence=ConfidenceLevel(pat_data.get("confidence", "insufficient_sample")),
                last_updated=datetime.fromisoformat(pat_data["last_updated"]) if "last_updated" in pat_data else datetime.utcnow(),
            )
        
        # Restore support/resistance reactions
        for key, sr_data in data.get("support_resistance_reactions", {}).items():
            dna.support_resistance_reactions[key] = SupportResistanceReaction(
                level_type=sr_data["level_type"],
                sample_size=sr_data.get("sample_size", 0),
                reaction_count=sr_data.get("reaction_count", 0),
                breakout_count=sr_data.get("breakout_count", 0),
                false_breakout_count=sr_data.get("false_breakout_count", 0),
                average_reaction_strength=sr_data.get("average_reaction_strength", 0.0),
                last_updated=datetime.fromisoformat(sr_data["last_updated"]) if "last_updated" in sr_data else datetime.utcnow(),
            )
        
        return dna


class DNAEngine:
    """
    Manages DNA profiles for all markets/assets/timeframes.
    
    The DNA Engine:
    - Creates and updates behavioral profiles
    - Stores profiles persistently
    - Provides queries for DNA-based insights
    - Ensures statistical validity before making claims
    """
    
    def __init__(self, database: Optional[ResearchDatabase] = None):
        """
        Initialize the DNA Engine.
        
        Args:
            database: ResearchDatabase for persistence
        """
        self.database = database or ResearchDatabase()
        self.dna_cache: Dict[str, MarketDNA] = {}
    
    def get_dna(self, market: str, symbol: str, timeframe: str) -> Optional[MarketDNA]:
        """
        Get DNA profile for a market/asset/timeframe.
        
        Args:
            market: Market name
            symbol: Symbol
            timeframe: Timeframe
            
        Returns:
            MarketDNA or None if not found
        """
        key = f"{market}_{symbol}_{timeframe}"
        
        # Check cache first
        if key in self.dna_cache:
            return self.dna_cache[key]
        
        # Load from database
        dna_data = self.database.load_dna_profile(market, symbol, timeframe)
        
        if dna_data:
            dna = MarketDNA.from_dict(dna_data)
            self.dna_cache[key] = dna
            return dna
        
        return None
    
    def create_or_get_dna(
        self, 
        market: str, 
        symbol: str, 
        timeframe: str,
        asset_class: str = ""
    ) -> MarketDNA:
        """
        Create new DNA profile or get existing one.
        
        Args:
            market: Market name
            symbol: Symbol
            timeframe: Timeframe
            asset_class: Asset class
            
        Returns:
            MarketDNA profile
        """
        existing = self.get_dna(market, symbol, timeframe)
        
        if existing:
            return existing
        
        # Create new DNA
        dna = MarketDNA(
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            asset_class=asset_class,
        )
        
        key = f"{market}_{symbol}_{timeframe}"
        self.dna_cache[key] = dna
        
        return dna
    
    def update_dna_from_backtest(
        self,
        market: str,
        symbol: str,
        timeframe: str,
        asset_class: str,
        signal_outcomes: List[Any],
    ):
        """
        Update DNA profile from backtest results.
        
        Args:
            market: Market name
            symbol: Symbol
            timeframe: Timeframe
            asset_class: Asset class
            signal_outcomes: List of SignalOutcome objects
        """
        dna = self.create_or_get_dna(market, symbol, timeframe, asset_class)
        
        for outcome in signal_outcomes:
            # Update general stats
            favorable = outcome.max_favorable_excursion or 0.0
            adverse = outcome.max_adverse_excursion or 0.0
            volatility = abs(favorable) + abs(adverse)
            
            dna.update_general_stats(
                outcome=outcome.final_outcome,
                favorable_move=favorable,
                adverse_move=adverse,
                volatility=volatility,
            )
            
            # Update indicator reactions
            for indicator in outcome.indicators_used:
                dna.update_indicator_reaction(
                    indicator_name=indicator,
                    parameters={},
                    outcome=outcome.final_outcome,
                    favorable_move=favorable,
                    adverse_move=adverse,
                )
            
            # Update pattern reactions
            for pattern in outcome.patterns_detected:
                dna.update_pattern_reaction(
                    pattern_name=pattern,
                    pattern_type="unknown",
                    outcome=outcome.final_outcome,
                    favorable_move=favorable,
                    move_after=outcome.outcome_after_5candles or 0.0,
                )
        
        # Save to database
        self.database.save_dna_profile(market, symbol, timeframe, dna.to_dict())
    
    def get_all_dnas(self) -> List[MarketDNA]:
        """Get all DNA profiles"""
        # Load from database
        all_profiles = self.database.get_all_dna_profiles()
        
        dns = []
        for profile_data in all_profiles:
            try:
                dna = MarketDNA.from_dict(profile_data)
                key = f"{dna.market}_{dna.symbol}_{dna.timeframe}"
                self.dna_cache[key] = dna
                dns.append(dna)
            except Exception as e:
                logger.error(f"Error loading DNA profile: {e}")
        
        return dns
    
    def find_similar_assets(
        self,
        market: str,
        symbol: str,
        timeframe: str,
        min_similarity: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Find assets with similar behavioral DNA.
        
        Args:
            market: Reference market
            symbol: Reference symbol
            timeframe: Reference timeframe
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar assets with similarity scores
        """
        reference_dna = self.get_dna(market, symbol, timeframe)
        
        if not reference_dna:
            return []
        
        all_dns = self.get_all_dnas()
        similar = []
        
        for dna in all_dns:
            if dna.market == market and dna.symbol == symbol and dna.timeframe == timeframe:
                continue
            
            # Calculate similarity based on indicator reactions
            common_indicators = set(reference_dna.indicator_reactions.keys()) & set(dna.indicator_reactions.keys())
            
            if not common_indicators:
                continue
            
            similarity_scores = []
            for indicator_key in common_indicators:
                ref_reaction = reference_dna.indicator_reactions[indicator_key]
                dna_reaction = dna.indicator_reactions[indicator_key]
                
                # Compare success rates
                if ref_reaction.sample_size > 0 and dna_reaction.sample_size > 0:
                    ref_rate = ref_reaction.success_count / ref_reaction.sample_size
                    dna_rate = dna_reaction.success_count / dna_reaction.sample_size
                    
                    similarity = 1 - abs(ref_rate - dna_rate)
                    similarity_scores.append(similarity)
            
            if similarity_scores:
                avg_similarity = sum(similarity_scores) / len(similarity_scores)
                
                if avg_similarity >= min_similarity:
                    similar.append({
                        "market": dna.market,
                        "symbol": dna.symbol,
                        "timeframe": dna.timeframe,
                        "similarity": avg_similarity,
                        "sample_size": dna.total_signals_observed,
                    })
        
        # Sort by similarity
        similar.sort(key=lambda x: x["similarity"], reverse=True)
        
        return similar
    
    def save_all_cached_dnas(self):
        """Save all cached DNA profiles to database"""
        for key, dna in self.dna_cache.items():
            self.database.save_dna_profile(dna.market, dna.symbol, dna.timeframe, dna.to_dict())
