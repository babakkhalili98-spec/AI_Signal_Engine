"""
Research Engine - Main orchestrator for R&D operations.

This is the primary entry point for R&D functionality, coordinating:
- Historical signal simulation
- Backtest analysis
- DNA profile updates
- Experiment management
- Report generation
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
import logging

from .historical_signal_simulator import HistoricalSignalSimulator, HistoricalSignal
from .backtest_engine import BacktestEngine, BacktestConfig, BacktestResult
from .dna_engine import DNAEngine
from .experiment_manager import ExperimentManager
from .research_database import ResearchDatabase
from .research_report import ResearchReportGenerator
from .metrics import RnDMetrics

logger = logging.getLogger(__name__)


class ResearchEngine:
    """
    Main orchestrator for R&D operations.
    
    Provides a unified interface for:
    - Running historical simulations
    - Analyzing signal outcomes
    - Building DNA profiles
    - Managing experiments
    - Generating reports
    """
    
    def __init__(
        self,
        database: Optional[ResearchDatabase] = None,
        backtest_config: Optional[BacktestConfig] = None,
    ):
        """
        Initialize the Research Engine.
        
        Args:
            database: ResearchDatabase for persistence
            backtest_config: Configuration for backtests
        """
        self.database = database or ResearchDatabase()
        self.backtest_config = backtest_config or BacktestConfig()
        
        # Initialize components
        self.simulator = HistoricalSignalSimulator()
        self.backtest_engine = BacktestEngine(self.backtest_config)
        self.dna_engine = DNAEngine(self.database)
        self.experiment_manager = ExperimentManager(self.database)
        self.report_generator = ResearchReportGenerator(
            self.database,
            self.dna_engine,
            self.experiment_manager,
        )
        
        self.results_cache: List[BacktestResult] = []
    
    def run_full_backtest(
        self,
        candles: List[Dict[str, Any]],
        symbol: str,
        market: str,
        asset_class: str,
        timeframe: str,
        signal_generator: Callable,
        update_dna: bool = True,
    ) -> BacktestResult:
        """
        Run a complete backtest from simulation to DNA update.
        
        Args:
            candles: Historical candle data
            symbol: Trading symbol
            market: Market name
            asset_class: Asset class
            timeframe: Timeframe
            signal_generator: Function to generate signals
            update_dna: Whether to update DNA profiles
            
        Returns:
            BacktestResult with full analysis
        
        The signal_generator function signature:
            def generate_signal(historical_candles: List[Dict], current_candle: Dict) -> Optional[Dict]
        """
        logger.info(f"Starting full backtest for {symbol} {timeframe}")
        
        # Step 1: Simulate historical signals
        signals = self.simulator.simulate(
            candles=candles,
            symbol=symbol,
            market=market,
            asset_class=asset_class,
            timeframe=timeframe,
            signal_generator=signal_generator,
        )
        
        if not signals:
            logger.warning(f"No signals generated for {symbol} {timeframe}")
            return self._empty_backtest_result(symbol, market, asset_class, timeframe)
        
        logger.info(f"Generated {len(signals)} historical signals")
        
        # Step 2: Analyze signal outcomes
        result = self.backtest_engine.analyze(
            signals=signals,
            candles=candles,
            symbol=symbol,
            market=market,
            asset_class=asset_class,
            timeframe=timeframe,
        )
        
        logger.info(f"Backtest complete: {result.total_signals} signals analyzed")
        
        # Step 3: Update DNA profile
        if update_dna and result.signal_outcomes:
            self.dna_engine.update_dna_from_backtest(
                market=market,
                symbol=symbol,
                timeframe=timeframe,
                asset_class=asset_class,
                signal_outcomes=result.signal_outcomes,
            )
            logger.info(f"Updated DNA profile for {symbol} {timeframe}")
        
        # Cache result
        self.results_cache.append(result)
        
        return result
    
    def create_experiment_and_backtest(
        self,
        hypothesis: str,
        candles: List[Dict[str, Any]],
        symbol: str,
        market: str,
        timeframe: str,
        asset_class: str = "",
        indicator: Optional[str] = None,
        new_parameters: Optional[Dict[str, Any]] = None,
        signal_generator: Optional[Callable] = None,
    ) -> Dict[str, Any]:
        """
        Create an experiment and run backtest as part of it.
        
        Args:
            hypothesis: What is being tested
            candles: Historical candle data
            symbol: Trading symbol
            market: Market name
            timeframe: Timeframe
            asset_class: Asset class
            indicator: Indicator being tested
            new_parameters: Parameters being tested
            signal_generator: Signal generation function
            
        Returns:
            Dictionary with experiment_id and backtest_result
        """
        # Create experiment
        experiment = self.experiment_manager.create_experiment(
            hypothesis=hypothesis,
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            asset_class=asset_class,
            indicator=indicator,
            new_parameters=new_parameters,
        )
        
        logger.info(f"Created experiment {experiment.experiment_id}")
        
        # Start experiment
        self.experiment_manager.start_experiment(experiment.experiment_id)
        
        # Run backtest
        if signal_generator:
            result = self.run_full_backtest(
                candles=candles,
                symbol=symbol,
                market=market,
                asset_class=asset_class,
                timeframe=timeframe,
                signal_generator=signal_generator,
                update_dna=True,
            )
            
            # Add outcomes to experiment
            for outcome in result.signal_outcomes:
                self.experiment_manager.add_signal_outcome(
                    experiment.experiment_id,
                    outcome,
                )
            
            # Complete experiment
            conclusion = (
                f"Tested {indicator or 'strategy'} with {new_parameters or 'default parameters'}. "
                f"Success rate: {result.summary.get('success_rate', 0):.2%}. "
                f"Sample size: {result.total_signals}."
            )
            
            self.experiment_manager.complete_experiment(
                experiment.experiment_id,
                conclusion,
            )
            
            return {
                "experiment_id": experiment.experiment_id,
                "backtest_result": result,
                "experiment": experiment,
            }
        else:
            # No signal generator - just create placeholder experiment
            self.experiment_manager.fail_experiment(
                experiment.experiment_id,
                "No signal generator provided",
            )
            
            return {
                "experiment_id": experiment.experiment_id,
                "backtest_result": None,
                "experiment": experiment,
            }
    
    def get_dna_for_asset(
        self,
        market: str,
        symbol: str,
        timeframe: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Get DNA profile for an asset.
        
        Args:
            market: Market name
            symbol: Symbol
            timeframe: Timeframe
            
        Returns:
            DNA profile dictionary or None
        """
        dna = self.dna_engine.get_dna(market, symbol, timeframe)
        
        if dna:
            return dna.to_dict()
        
        return None
    
    def find_similar_assets(
        self,
        market: str,
        symbol: str,
        timeframe: str,
        min_similarity: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """
        Find assets with similar behavioral patterns.
        
        Args:
            market: Reference market
            symbol: Reference symbol
            timeframe: Reference timeframe
            min_similarity: Minimum similarity threshold
            
        Returns:
            List of similar assets
        """
        return self.dna_engine.find_similar_assets(
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            min_similarity=min_similarity,
        )
    
    def generate_report(
        self,
        report_type: str,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Generate a research report.
        
        Args:
            report_type: Type of report (daily, weekly, dna, indicator, pattern, market_comparison)
            **kwargs: Additional arguments for specific report types
            
        Returns:
            Report dictionary
        """
        report_generators = {
            "daily": self.report_generator.generate_daily_report,
            "weekly": self.report_generator.generate_weekly_report,
            "dna": self.report_generator.generate_dna_report,
            "indicator": self.report_generator.generate_indicator_research_report,
            "pattern": self.report_generator.generate_pattern_research_report,
            "market_comparison": self.report_generator.generate_market_comparison_report,
        }
        
        generator = report_generators.get(report_type)
        
        if not generator:
            logger.error(f"Unknown report type: {report_type}")
            return {"error": f"Unknown report type: {report_type}"}
        
        return generator(**kwargs)
    
    def save_report(self, report: Dict[str, Any], filename: str) -> str:
        """
        Save a report to file.
        
        Args:
            report: Report dictionary
            filename: Filename without extension
            
        Returns:
            Full path to saved file
        """
        return self.report_generator.save_report(report, filename)
    
    def _empty_backtest_result(
        self,
        symbol: str,
        market: str,
        asset_class: str,
        timeframe: str,
    ) -> BacktestResult:
        """Create an empty backtest result"""
        now = datetime.utcnow()
        return BacktestResult(
            symbol=symbol,
            market=market,
            asset_class=asset_class,
            timeframe=timeframe,
            start_date=now,
            end_date=now,
            total_signals=0,
            metrics=RnDMetrics(),
            signal_outcomes=[],
            config=self.backtest_config,
            summary={},
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall R&D statistics"""
        return {
            "experiments": self.experiment_manager.get_statistics(),
            "backtests_run": len(self.results_cache),
            "dna_profiles": len(self.dna_engine.get_all_dnas()),
        }
