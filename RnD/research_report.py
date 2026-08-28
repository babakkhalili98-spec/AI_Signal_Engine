"""
Research Report Generator - Generates R&D reports.

This module creates various report types:
- Daily Research Report
- Weekly Research Report
- Market DNA Report
- Indicator Research Report
- Pattern Research Report
- Support/Resistance Report
- Parameter Optimization Report
- Market Comparison Report
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from .research_database import ResearchDatabase
from .dna_engine import DNAEngine, MarketDNA
from .experiment_manager import ExperimentManager
from .metrics import RnDMetrics
from .backtest_engine import BacktestResult

logger = logging.getLogger(__name__)


class ResearchReportGenerator:
    """
    Generates various R&D reports.
    
    Reports are generated as dictionaries that can be:
    - Saved to files
    - Sent via messaging systems
    - Displayed in dashboards
    """
    
    def __init__(
        self, 
        database: Optional[ResearchDatabase] = None,
        dna_engine: Optional[DNAEngine] = None,
        experiment_manager: Optional[ExperimentManager] = None,
    ):
        """
        Initialize the report generator.
        
        Args:
            database: ResearchDatabase
            dna_engine: DNAEngine
            experiment_manager: ExperimentManager
        """
        self.database = database or ResearchDatabase()
        self.dna_engine = dna_engine or DNAEngine(self.database)
        self.experiment_manager = experiment_manager or ExperimentManager(self.database)
    
    def generate_daily_report(
        self,
        date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a daily research report.
        
        Args:
            date: Date for report (defaults to today)
            
        Returns:
            Report dictionary
        """
        if date is None:
            date = datetime.utcnow()
        
        report = {
            "report_type": "daily_research_report",
            "date": date.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {},
            "experiments_completed_today": [],
            "new_dna_profiles": [],
            "key_findings": [],
        }
        
        # Get experiments completed today
        all_experiments = self.experiment_manager.get_completed_experiments()
        
        for exp in all_experiments:
            # Check if completed today (simplified - would need proper date comparison)
            report["experiments_completed_today"].append({
                "experiment_id": exp.experiment_id,
                "hypothesis": exp.hypothesis,
                "sample_size": exp.sample_size,
                "conclusion": exp.conclusion,
                "confidence": exp.confidence.value,
            })
        
        # Get new DNA profiles
        all_dns = self.dna_engine.get_all_dnas()
        
        for dna in all_dns:
            # Check if created/updated today
            report["new_dna_profiles"].append({
                "market": dna.market,
                "symbol": dna.symbol,
                "timeframe": dna.timeframe,
                "total_signals_observed": dna.total_signals_observed,
                "success_rate": dna.overall_success_rate,
            })
        
        # Summary statistics
        exp_stats = self.experiment_manager.get_statistics()
        report["summary"] = {
            "total_experiments": exp_stats.get("total_experiments", 0),
            "completed_experiments": exp_stats.get("completed", 0),
            "total_dna_profiles": len(all_dns),
        }
        
        return report
    
    def generate_weekly_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Generate a weekly research report.
        
        Args:
            start_date: Start of week
            end_date: End of week
            
        Returns:
            Report dictionary
        """
        if end_date is None:
            end_date = datetime.utcnow()
        if start_date is None:
            start_date = end_date - timedelta(days=7)
        
        report = {
            "report_type": "weekly_research_report",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {},
            "experiments_summary": [],
            "dna_updates": [],
            "trends": [],
        }
        
        # Aggregate experiment results
        all_experiments = self.experiment_manager.get_completed_experiments()
        
        total_sample_size = 0
        high_confidence_count = 0
        
        for exp in all_experiments:
            total_sample_size += exp.sample_size
            
            if exp.confidence.value in ["high_confidence", "statistically_relevant_sample"]:
                high_confidence_count += 1
            
            report["experiments_summary"].append({
                "experiment_id": exp.experiment_id,
                "market": exp.market,
                "symbol": exp.symbol,
                "indicator": exp.indicator,
                "sample_size": exp.sample_size,
                "success_rate": exp.metrics.get("success_rate", 0) if exp.metrics else 0,
                "confidence": exp.confidence.value,
                "conclusion": exp.conclusion[:200] if exp.conclusion else "",
            })
        
        report["summary"] = {
            "total_experiments": len(all_experiments),
            "total_signals_analyzed": total_sample_size,
            "high_confidence_findings": high_confidence_count,
        }
        
        return report
    
    def generate_dna_report(
        self,
        market: Optional[str] = None,
        symbol: Optional[str] = None,
        timeframe: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate a Market DNA report.
        
        Args:
            market: Filter by market
            symbol: Filter by symbol
            timeframe: Filter by timeframe
            
        Returns:
            Report dictionary
        """
        report = {
            "report_type": "market_dna_report",
            "generated_at": datetime.utcnow().isoformat(),
            "filters": {
                "market": market,
                "symbol": symbol,
                "timeframe": timeframe,
            },
            "dna_profiles": [],
        }
        
        all_dns = self.dna_engine.get_all_dnas()
        
        for dna in all_dns:
            # Apply filters
            if market and dna.market != market:
                continue
            if symbol and dna.symbol != symbol:
                continue
            if timeframe and dna.timeframe != timeframe:
                continue
            
            profile_data = {
                "market": dna.market,
                "symbol": dna.symbol,
                "timeframe": dna.timeframe,
                "asset_class": dna.asset_class,
                "statistics": {
                    "total_signals": dna.total_signals_observed,
                    "success_rate": dna.overall_success_rate,
                    "average_volatility": dna.average_volatility,
                    "typical_favorable_move": dna.typical_favorable_move,
                    "typical_adverse_move": dna.typical_adverse_move,
                },
                "indicator_reactions": {},
                "pattern_reactions": {},
                "support_resistance_reactions": {},
            }
            
            # Add top indicator reactions (by sample size)
            sorted_indicators = sorted(
                dna.indicator_reactions.items(),
                key=lambda x: x[1].sample_size,
                reverse=True
            )[:10]
            
            for key, reaction in sorted_indicators:
                profile_data["indicator_reactions"][key] = {
                    "sample_size": reaction.sample_size,
                    "success_rate": reaction.success_count / reaction.sample_size if reaction.sample_size > 0 else 0,
                    "avg_favorable_move": reaction.average_favorable_move,
                    "confidence": reaction.confidence.value,
                }
            
            # Add top pattern reactions
            sorted_patterns = sorted(
                dna.pattern_reactions.items(),
                key=lambda x: x[1].sample_size,
                reverse=True
            )[:10]
            
            for key, reaction in sorted_patterns:
                profile_data["pattern_reactions"][key] = {
                    "sample_size": reaction.sample_size,
                    "success_rate": reaction.success_count / reaction.sample_size if reaction.sample_size > 0 else 0,
                    "avg_move": reaction.average_move_after_pattern,
                    "confidence": reaction.confidence.value,
                }
            
            report["dna_profiles"].append(profile_data)
        
        report["summary"] = {
            "total_profiles": len(report["dna_profiles"]),
        }
        
        return report
    
    def generate_indicator_research_report(
        self,
        indicator_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate an indicator research report.
        
        Args:
            indicator_name: Filter by specific indicator
            
        Returns:
            Report dictionary
        """
        report = {
            "report_type": "indicator_research_report",
            "generated_at": datetime.utcnow().isoformat(),
            "indicator_filter": indicator_name,
            "experiments": [],
            "aggregate_metrics": {},
        }
        
        # Get relevant experiments
        if indicator_name:
            experiments = self.experiment_manager.get_experiments_by_indicator(indicator_name)
        else:
            experiments = self.experiment_manager.get_completed_experiments()
            # Filter to only those with indicators
            experiments = [e for e in experiments if e.indicator]
        
        # Aggregate metrics by indicator
        indicator_metrics = {}
        
        for exp in experiments:
            ind_name = exp.indicator or "unknown"
            
            if ind_name not in indicator_metrics:
                indicator_metrics[ind_name] = {
                    "experiment_count": 0,
                    "total_sample_size": 0,
                    "total_successes": 0,
                    "parameters_tested": set(),
                }
            
            metrics = indicator_metrics[ind_name]
            metrics["experiment_count"] += 1
            metrics["total_sample_size"] += exp.sample_size
            
            if exp.metrics:
                metrics["total_successes"] += exp.metrics.get("success_count", 0)
            
            if exp.new_parameters:
                metrics["parameters_tested"].add(str(exp.new_parameters))
            
            report["experiments"].append({
                "experiment_id": exp.experiment_id,
                "market": exp.market,
                "symbol": exp.symbol,
                "timeframe": exp.timeframe,
                "parameters": exp.new_parameters,
                "sample_size": exp.sample_size,
                "success_rate": exp.metrics.get("success_rate", 0) if exp.metrics else 0,
                "confidence": exp.confidence.value,
                "conclusion": exp.conclusion[:200] if exp.conclusion else "",
            })
        
        # Calculate aggregate metrics
        for ind_name, metrics in indicator_metrics.items():
            report["aggregate_metrics"][ind_name] = {
                "experiment_count": metrics["experiment_count"],
                "total_sample_size": metrics["total_sample_size"],
                "overall_success_rate": metrics["total_successes"] / metrics["total_sample_size"] if metrics["total_sample_size"] > 0 else 0,
                "unique_parameter_sets_tested": len(metrics["parameters_tested"]),
            }
        
        return report
    
    def generate_pattern_research_report(self) -> Dict[str, Any]:
        """Generate a pattern research report"""
        report = {
            "report_type": "pattern_research_report",
            "generated_at": datetime.utcnow().isoformat(),
            "patterns_found": [],
        }
        
        # Collect pattern data from all DNA profiles
        all_dns = self.dna_engine.get_all_dnas()
        
        pattern_aggregate = {}
        
        for dna in all_dns:
            for pattern_key, reaction in dna.pattern_reactions.items():
                if pattern_key not in pattern_aggregate:
                    pattern_aggregate[pattern_key] = {
                        "pattern_name": reaction.pattern_name,
                        "pattern_type": reaction.pattern_type,
                        "markets_seen": set(),
                        "total_sample_size": 0,
                        "total_successes": 0,
                    }
                
                agg = pattern_aggregate[pattern_key]
                agg["markets_seen"].add(f"{dna.market}_{dna.timeframe}")
                agg["total_sample_size"] += reaction.sample_size
                agg["total_successes"] += reaction.success_count
        
        for pattern_key, agg in pattern_aggregate.items():
            report["patterns_found"].append({
                "pattern_key": pattern_key,
                "pattern_name": agg["pattern_name"],
                "pattern_type": agg["pattern_type"],
                "markets_count": len(agg["markets_seen"]),
                "markets": list(agg["markets_seen"]),
                "total_sample_size": agg["total_sample_size"],
                "overall_success_rate": agg["total_successes"] / agg["total_sample_size"] if agg["total_sample_size"] > 0 else 0,
            })
        
        # Sort by sample size
        report["patterns_found"].sort(key=lambda x: x["total_sample_size"], reverse=True)
        
        return report
    
    def generate_market_comparison_report(
        self,
        markets: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a market comparison report.
        
        Args:
            markets: List of markets to compare
            
        Returns:
            Report dictionary
        """
        report = {
            "report_type": "market_comparison_report",
            "generated_at": datetime.utcnow().isoformat(),
            "markets_compared": markets or [],
            "comparison_data": [],
        }
        
        all_dns = self.dna_engine.get_all_dnas()
        
        # Group by market
        market_data = {}
        
        for dna in all_dns:
            if markets and dna.market not in markets:
                continue
            
            if dna.market not in market_data:
                market_data[dna.market] = {
                    "market": dna.market,
                    "assets_analyzed": set(),
                    "timeframes_analyzed": set(),
                    "total_signals": 0,
                    "success_rates": [],
                    "volatilities": [],
                }
            
            data = market_data[dna.market]
            data["assets_analyzed"].add(dna.symbol)
            data["timeframes_analyzed"].add(dna.timeframe)
            data["total_signals"] += dna.total_signals_observed
            data["success_rates"].append(dna.overall_success_rate)
            data["volatilities"].append(dna.average_volatility)
        
        for market_name, data in market_data.items():
            avg_success_rate = sum(data["success_rates"]) / len(data["success_rates"]) if data["success_rates"] else 0
            avg_volatility = sum(data["volatilities"]) / len(data["volatilities"]) if data["volatilities"] else 0
            
            report["comparison_data"].append({
                "market": market_name,
                "assets_count": len(data["assets_analyzed"]),
                "timeframes_count": len(data["timeframes_analyzed"]),
                "total_signals_analyzed": data["total_signals"],
                "average_success_rate": avg_success_rate,
                "average_volatility": avg_volatility,
            })
        
        # Sort by total signals
        report["comparison_data"].sort(key=lambda x: x["total_signals_analyzed"], reverse=True)
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: str) -> str:
        """
        Save a report to file.
        
        Args:
            report: Report dictionary
            filename: Filename (without extension)
            
        Returns:
            Full path to saved file
        """
        import json
        
        filepath = self.database.reports_path / f"{filename}.json"
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Saved report to {filepath}")
        
        return str(filepath)
