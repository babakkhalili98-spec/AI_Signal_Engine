from typing import List, Dict, Any
import pandas as pd

class WalkForwardValidator:
    """
    Performs Walk-Forward Validation on experiment results.
    Splits data into Train, Validation, and Out-of-Sample (OOS) periods.
    """
    
    def __init__(self, train_ratio: float = 0.6, val_ratio: float = 0.2, oos_ratio: float = 0.2):
        if not abs((train_ratio + val_ratio + oos_ratio) - 1.0) < 1e-6:
            raise ValueError("Ratios must sum to 1.0")
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.oos_ratio = oos_ratio

    def split_data(self, data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        n = len(data)
        train_end = int(n * self.train_ratio)
        val_end = int(n * (self.train_ratio + self.val_ratio))
        
        return {
            "train": data.iloc[:train_end],
            "validation": data.iloc[train_end:val_end],
            "oos": data.iloc[val_end:]
        }

    def validate(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates results across different periods.
        Returns validation status and metrics.
        """
        # Placeholder logic for splitting results by period
        # In real implementation, backtest engine should return period-specific metrics
        
        train_metrics = results.get("train_metrics", {})
        val_metrics = results.get("validation_metrics", {})
        oos_metrics = results.get("oos_metrics", {})
        
        # Check for significant degradation in OOS
        train_pf = train_metrics.get("profit_factor", 0)
        oos_pf = oos_metrics.get("profit_factor", 0)
        
        degradation = (train_pf - oos_pf) / train_pf if train_pf > 0 else 0
        
        status = "REAL_DATA_VALIDATED" if degradation < 0.3 and oos_pf > 1.0 else "CANDIDATE"
        
        return {
            "status": status,
            "degradation_score": degradation,
            "train_metrics": train_metrics,
            "validation_metrics": val_metrics,
            "oos_metrics": oos_metrics
        }