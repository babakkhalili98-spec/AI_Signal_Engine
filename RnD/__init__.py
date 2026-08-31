"""
R&D Module - Market Research Laboratory

This module provides research and experimentation capabilities for the Signal Engine.
It focuses on:
- Historical signal simulation
- Market behavior analysis
- DNA profiling for assets
- Indicator and pattern research
- Parameter optimization
- Experiment management

IMPORTANT: This is NOT a Risk Engine or Trading Execution System.
"""

from .research_engine import ResearchEngine
from .backtest_engine import BacktestEngine
from .historical_signal_simulator import HistoricalSignalSimulator
from .market_behavior_analyzer import MarketBehaviorAnalyzer
from .dna_engine import DNAEngine
from .experiment_manager import ExperimentManager
from .experiment_result import ExperimentResult
from .metrics import RnDMetrics
from .research_database import ResearchDatabase
from .research_report import ResearchReportGenerator

__all__ = [
    "ResearchEngine",
    "BacktestEngine",
    "HistoricalSignalSimulator",
    "MarketBehaviorAnalyzer",
    "DNAEngine",
    "ExperimentManager",
    "ExperimentResult",
    "RnDMetrics",
    "ResearchDatabase",
    "ResearchReportGenerator",
]