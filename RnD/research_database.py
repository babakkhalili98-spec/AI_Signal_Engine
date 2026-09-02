"""
Research Database - Storage and retrieval for R&D data.

This module handles persistence of:
- Experiment results
- DNA profiles
- Research findings
- Historical signal data
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import asdict


class ResearchDatabase:
    """
    Database for R&D research data.
    
    Uses JSON files for storage in the datasets/ and knowledge/ directories.
    """
    
    def __init__(self, base_path: str = None):
        """
        Initialize the research database.
        
        Args:
            base_path: Base path for RnD directory. Defaults to /workspace/RnD
        """
        if base_path is None:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        self.base_path = Path(base_path)
        self.datasets_path = self.base_path / "datasets"
        self.experiments_path = self.base_path / "experiments"
        self.reports_path = self.base_path / "reports"
        self.knowledge_path = self.base_path / "knowledge"
        
        # Ensure directories exist
        self.datasets_path.mkdir(parents=True, exist_ok=True)
        self.experiments_path.mkdir(parents=True, exist_ok=True)
        self.reports_path.mkdir(parents=True, exist_ok=True)
        self.knowledge_path.mkdir(parents=True, exist_ok=True)
    
    def save_experiment(self, experiment_data: Dict[str, Any], experiment_id: str):
        """
        Save an experiment result.
        
        Args:
            experiment_data: Dictionary containing experiment data
            experiment_id: Unique experiment identifier
        """
        filepath = self.experiments_path / f"{experiment_id}.json"
        with open(filepath, 'w') as f:
            json.dump(experiment_data, f, indent=2, default=str)
    
    def load_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        """
        Load an experiment by ID.
        
        Args:
            experiment_id: Experiment identifier
            
        Returns:
            Experiment data or None if not found
        """
        filepath = self.experiments_path / f"{experiment_id}.json"
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def list_experiments(self, filters: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        List experiment IDs, optionally filtered.
        
        Args:
            filters: Optional filters (e.g., {"market": "CRYPTO", "timeframe": "4H"})
            
        Returns:
            List of experiment IDs matching filters
        """
        experiment_ids = []
        
        for filepath in self.experiments_path.glob("*.json"):
            if filters:
                data = self.load_experiment(filepath.stem)
                if data:
                    match = True
                    for key, value in filters.items():
                        if data.get(key) != value:
                            match = False
                            break
                    if match:
                        experiment_ids.append(filepath.stem)
            else:
                experiment_ids.append(filepath.stem)
        
        return experiment_ids
    
    def save_dna_profile(self, market: str, symbol: str, timeframe: str, dna_data: Dict[str, Any]):
        """
        Save a DNA profile for a specific market/symbol/timeframe.
        
        Args:
            market: Market name (e.g., CRYPTO)
            symbol: Symbol (e.g., BTCUSDT)
            timeframe: Timeframe (e.g., 4H)
            dna_data: DNA profile data
        """
        filename = f"{market}_{symbol}_{timeframe}_dna.json"
        filepath = self.knowledge_path / "dna" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        dna_data["last_updated"] = datetime.utcnow().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(dna_data, f, indent=2, default=str)
    
    def load_dna_profile(self, market: str, symbol: str, timeframe: str) -> Optional[Dict[str, Any]]:
        """
        Load a DNA profile.
        
        Args:
            market: Market name
            symbol: Symbol
            timeframe: Timeframe
            
        Returns:
            DNA profile data or None if not found
        """
        filename = f"{market}_{symbol}_{timeframe}_dna.json"
        filepath = self.knowledge_path / "dna" / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def save_research_finding(self, category: str, finding_id: str, finding_data: Dict[str, Any]):
        """
        Save a research finding to the knowledge base.
        
        Args:
            category: Category (e.g., "indicator", "pattern", "support_resistance")
            finding_id: Unique finding identifier
            finding_data: Finding data
        """
        filepath = self.knowledge_path / category / f"{finding_id}.json"
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        finding_data["created_at"] = datetime.utcnow().isoformat()
        finding_data["updated_at"] = datetime.utcnow().isoformat()
        
        with open(filepath, 'w') as f:
            json.dump(finding_data, f, indent=2, default=str)
    
    def load_research_finding(self, category: str, finding_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a research finding.
        
        Args:
            category: Category
            finding_id: Finding identifier
            
        Returns:
            Finding data or None if not found
        """
        filepath = self.knowledge_path / category / f"{finding_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def save_historical_signal(self, signal_data: Dict[str, Any], timestamp_str: str, symbol: str, timeframe: str):
        """
        Save a historical signal for later analysis.
        
        Args:
            signal_data: Signal data
            timestamp_str: Timestamp string for filename
            symbol: Symbol
            timeframe: Timeframe
        """
        filename = f"{symbol}_{timeframe}_{timestamp_str}.json"
        filepath = self.datasets_path / "signals" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(signal_data, f, indent=2, default=str)
    
    def load_historical_signals(
        self, 
        symbol: str, 
        timeframe: str, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Load historical signals for a symbol/timeframe.
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            List of signal data dictionaries
        """
        signals = []
        pattern = self.datasets_path / "signals" / f"{symbol}_{timeframe}_*.json"
        
        for filepath in pattern.glob("*.json"):
            with open(filepath, 'r') as f:
                signal_data = json.load(f)
                
                # Apply date filters if provided
                if start_date or end_date:
                    signal_time = datetime.fromisoformat(signal_data.get("timestamp", ""))
                    
                    if start_date and signal_time < start_date:
                        continue
                    if end_date and signal_time > end_date:
                        continue
                
                signals.append(signal_data)
        
        return sorted(signals, key=lambda x: x.get("timestamp", ""))
    
    def save_market_data(self, symbol: str, timeframe: str, data: List[Dict[str, Any]]):
        """
        Save market data (candles) for backtesting.
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            data: List of candle data dictionaries
        """
        filename = f"{symbol}_{timeframe}_market_data.json"
        filepath = self.datasets_path / "market" / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_market_data(self, symbol: str, timeframe: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load market data for backtesting.
        
        Args:
            symbol: Symbol
            timeframe: Timeframe
            
        Returns:
            List of candle data or None if not found
        """
        filename = f"{symbol}_{timeframe}_market_data.json"
        filepath = self.datasets_path / "market" / filename
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r') as f:
            return json.load(f)
    
    def get_all_dna_profiles(self) -> List[Dict[str, Any]]:
        """Get all DNA profiles"""
        profiles = []
        dna_path = self.knowledge_path / "dna"
        
        if dna_path.exists():
            for filepath in dna_path.glob("**/*.json"):
                with open(filepath, 'r') as f:
                    profiles.append(json.load(f))
        
        return profiles
    
    def get_all_research_findings(self, category: str) -> List[Dict[str, Any]]:
        """Get all research findings for a category"""
        findings = []
        category_path = self.knowledge_path / category
        
        if category_path.exists():
            for filepath in category_path.glob("*.json"):
                with open(filepath, 'r') as f:
                    findings.append(json.load(f))
        
        return findings
