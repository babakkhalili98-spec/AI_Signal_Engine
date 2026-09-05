"""
Experiment Manager - Manages R&D experiments.

This module handles:
- Creating and tracking experiments
- Managing experiment lifecycle
- Storing and retrieving experiment results
- Preventing duplicate experiments
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

from .experiment_result import ExperimentResult, ExperimentStatus, ConfidenceLevel, SignalOutcome
from .research_database import ResearchDatabase

logger = logging.getLogger(__name__)


class ExperimentManager:
    """
    Manages the lifecycle of R&D experiments.
    
    Features:
    - Create new experiments with unique IDs
    - Track experiment status
    - Store and retrieve results
    - Query experiments by filters
    - Manage experiment versions
    """
    
    def __init__(self, database: Optional[ResearchDatabase] = None):
        """
        Initialize the Experiment Manager.
        
        Args:
            database: ResearchDatabase for persistence
        """
        self.database = database or ResearchDatabase()
        self.active_experiments: Dict[str, ExperimentResult] = {}
        self.experiment_counter = 0
    
    def create_experiment(
        self,
        hypothesis: str,
        market: str,
        symbol: str,
        timeframe: str,
        asset_class: str = "",
        indicator: Optional[str] = None,
        old_parameters: Optional[Dict[str, Any]] = None,
        new_parameters: Optional[Dict[str, Any]] = None,
        limitations: Optional[List[str]] = None,
    ) -> ExperimentResult:
        """
        Create a new experiment.
        
        Args:
            hypothesis: What is being tested
            market: Market name
            symbol: Symbol
            timeframe: Timeframe
            asset_class: Asset class
            indicator: Indicator being tested (if applicable)
            old_parameters: Previous parameters (for optimization)
            new_parameters: New parameters being tested
            limitations: Known limitations
            
        Returns:
            New ExperimentResult with unique ID
        """
        self.experiment_counter += 1
        
        # Generate unique ID
        date_str = datetime.utcnow().strftime('%Y%m%d')
        experiment_id = f"EXP-{date_str}-{self.experiment_counter:06d}"
        
        # Check if ID already exists (unlikely but safe)
        while self.database.load_experiment(experiment_id) is not None:
            self.experiment_counter += 1
            experiment_id = f"EXP-{date_str}-{self.experiment_counter:06d}"
        
        experiment = ExperimentResult(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            market=market,
            symbol=symbol,
            timeframe=timeframe,
            asset_class=asset_class,
            indicator=indicator,
            old_parameters=old_parameters,
            new_parameters=new_parameters,
            limitations=limitations or [],
            status=ExperimentStatus.PLANNED,
        )
        
        self.active_experiments[experiment_id] = experiment
        
        logger.info(f"Created experiment {experiment_id}: {hypothesis}")
        
        return experiment
    
    def start_experiment(self, experiment_id: str) -> bool:
        """
        Mark an experiment as running.
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            True if successful, False if experiment not found
        """
        experiment = self._get_experiment(experiment_id)
        
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found")
            return False
        
        experiment.status = ExperimentStatus.RUNNING
        experiment.updated_at = datetime.utcnow()
        
        logger.info(f"Started experiment {experiment_id}")
        
        return True
    
    def add_signal_outcome(
        self,
        experiment_id: str,
        outcome: SignalOutcome,
    ) -> bool:
        """
        Add a signal outcome to an experiment.
        
        Args:
            experiment_id: Experiment identifier
            outcome: Signal outcome to add
            
        Returns:
            True if successful, False if experiment not found
        """
        experiment = self._get_experiment(experiment_id)
        
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found")
            return False
        
        if experiment.status != ExperimentStatus.RUNNING:
            logger.warning(f"Experiment {experiment_id} is not running")
            return False
        
        experiment.add_signal_outcome(outcome)
        
        return True
    
    def complete_experiment(
        self,
        experiment_id: str,
        conclusion: str,
    ) -> bool:
        """
        Mark an experiment as completed.
        
        Args:
            experiment_id: Experiment identifier
            conclusion: Summary conclusion
            
        Returns:
            True if successful, False if experiment not found
        """
        experiment = self._get_experiment(experiment_id)
        
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found")
            return False
        
        experiment.calculate_metrics()
        experiment.conclusion = conclusion
        experiment.status = ExperimentStatus.COMPLETED
        experiment.updated_at = datetime.utcnow()
        
        # Save to database
        self.database.save_experiment(experiment.to_dict(), experiment_id)
        
        # Remove from active experiments
        if experiment_id in self.active_experiments:
            del self.active_experiments[experiment_id]
        
        logger.info(f"Completed experiment {experiment_id}: {conclusion}")
        
        return True
    
    def fail_experiment(
        self,
        experiment_id: str,
        reason: str,
    ) -> bool:
        """
        Mark an experiment as failed.
        
        Args:
            experiment_id: Experiment identifier
            reason: Failure reason
            
        Returns:
            True if successful, False if experiment not found
        """
        experiment = self._get_experiment(experiment_id)
        
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found")
            return False
        
        experiment.conclusion = f"FAILED: {reason}"
        experiment.status = ExperimentStatus.FAILED
        experiment.updated_at = datetime.utcnow()
        
        self.database.save_experiment(experiment.to_dict(), experiment_id)
        
        if experiment_id in self.active_experiments:
            del self.active_experiments[experiment_id]
        
        logger.warning(f"Failed experiment {experiment_id}: {reason}")
        
        return True
    
    def invalidate_experiment(
        self,
        experiment_id: str,
        reason: str,
    ) -> bool:
        """
        Invalidate an experiment (e.g., due to flawed methodology).
        
        Args:
            experiment_id: Experiment identifier
            reason: Invalidation reason
            
        Returns:
            True if successful, False if experiment not found
        """
        experiment = self._get_experiment(experiment_id)
        
        if not experiment:
            logger.error(f"Experiment {experiment_id} not found")
            return False
        
        experiment.conclusion = f"INVALIDATED: {reason}"
        experiment.status = ExperimentStatus.INVALIDATED
        experiment.updated_at = datetime.utcnow()
        
        self.database.save_experiment(experiment.to_dict(), experiment_id)
        
        if experiment_id in self.active_experiments:
            del self.active_experiments[experiment_id]
        
        logger.warning(f"Invalidated experiment {experiment_id}: {reason}")
        
        return True
    
    def _get_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """Get experiment from cache or database"""
        if experiment_id in self.active_experiments:
            return self.active_experiments[experiment_id]
        
        data = self.database.load_experiment(experiment_id)
        
        if data:
            experiment = ExperimentResult.from_dict(data)
            self.active_experiments[experiment_id] = experiment
            return experiment
        
        return None
    
    def get_experiment(self, experiment_id: str) -> Optional[ExperimentResult]:
        """
        Get an experiment by ID.
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            ExperimentResult or None
        """
        return self._get_experiment(experiment_id)
    
    def list_experiments(
        self,
        filters: Optional[Dict[str, Any]] = None,
        status_filter: Optional[ExperimentStatus] = None,
    ) -> List[str]:
        """
        List experiment IDs matching filters.
        
        Args:
            filters: Field filters (e.g., {"market": "CRYPTO"})
            status_filter: Filter by status
            
        Returns:
            List of experiment IDs
        """
        # Get all experiment IDs from database
        all_ids = self.database.list_experiments(filters)
        
        # Also include active experiments
        for exp_id, exp in self.active_experiments.items():
            if exp_id not in all_ids:
                match = True
                
                if filters:
                    for key, value in filters.items():
                        if getattr(exp, key, None) != value:
                            match = False
                            break
                
                if status_filter and exp.status != status_filter:
                    match = False
                
                if match:
                    all_ids.append(exp_id)
        
        return all_ids
    
    def get_experiments_by_market(self, market: str) -> List[ExperimentResult]:
        """Get all experiments for a specific market"""
        ids = self.list_experiments({"market": market})
        return [exp for exp_id in ids if (exp := self.get_experiment(exp_id)) is not None]
    
    def get_experiments_by_indicator(self, indicator: str) -> List[ExperimentResult]:
        """Get all experiments for a specific indicator"""
        ids = self.list_experiments({"indicator": indicator})
        return [exp for exp_id in ids if (exp := self.get_experiment(exp_id)) is not None]
    
    def get_completed_experiments(self) -> List[ExperimentResult]:
        """Get all completed experiments"""
        ids = self.list_experiments(status_filter=ExperimentStatus.COMPLETED)
        return [exp for exp_id in ids if (exp := self.get_experiment(exp_id)) is not None]
    
    def get_failed_experiments(self) -> List[ExperimentResult]:
        """Get all failed experiments"""
        ids = self.list_experiments(status_filter=ExperimentStatus.FAILED)
        return [exp for exp_id in ids if (exp := self.get_experiment(exp_id)) is not None]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall experiment statistics"""
        all_ids = self.list_experiments()
        
        total = len(all_ids)
        completed = sum(1 for exp_id in all_ids if self.get_experiment(exp_id).status == ExperimentStatus.COMPLETED)
        failed = sum(1 for exp_id in all_ids if self.get_experiment(exp_id).status == ExperimentStatus.FAILED)
        invalidated = sum(1 for exp_id in all_ids if self.get_experiment(exp_id).status == ExperimentStatus.INVALIDATED)
        running = sum(1 for exp_id in all_ids if self.get_experiment(exp_id).status == ExperimentStatus.RUNNING)
        planned = sum(1 for exp_id in all_ids if self.get_experiment(exp_id).status == ExperimentStatus.PLANNED)
        
        # Calculate average sample sizes
        total_sample_size = 0
        high_confidence_count = 0
        
        for exp_id in all_ids:
            exp = self.get_experiment(exp_id)
            if exp and exp.status == ExperimentStatus.COMPLETED:
                total_sample_size += exp.sample_size
                if exp.confidence in [ConfidenceLevel.HIGH_CONFIDENCE, ConfidenceLevel.STATISTICALLY_RELEVANT]:
                    high_confidence_count += 1
        
        return {
            "total_experiments": total,
            "completed": completed,
            "failed": failed,
            "invalidated": invalidated,
            "running": running,
            "planned": planned,
            "average_sample_size": total_sample_size / completed if completed > 0 else 0,
            "high_confidence_results": high_confidence_count,
            "active_experiments_in_memory": len(self.active_experiments),
        }
