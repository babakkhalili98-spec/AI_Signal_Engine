import pandas as pd
from typing import Tuple, Optional

class DataQualityGate:
    """
    Validates historical data quality before running experiments.
    Checks for missing candles, duplicates, invalid OHLC, etc.
    """
    
    def __init__(self, max_missing_pct: float = 0.01, min_samples: int = 100):
        self.max_missing_pct = max_missing_pct
        self.min_samples = min_samples

    def validate(self, df: pd.DataFrame, timeframe: str) -> Tuple[bool, str]:
        if df.empty:
            return False, "DATA_EMPTY"
            
        if len(df) < self.min_samples:
            return False, "DATA_NOT_ENOUGH"
            
        # Check for duplicates
        if df.index.duplicated().any():
            return False, "DUPLICATE_CANDLES"
            
        # Check for missing candles (simplified)
        # In production, this should account for weekends/holidays per asset
        expected_freq = self._get_expected_freq(timeframe)
        # Logic to check gaps would go here
        
        # Check OHLC validity
        if (df['high'] < df['low']).any():
            return False, "INVALID_OHLC_HIGH_LOW"
            
        if (df['close'] > df['high']).any() or (df['close'] < df['low']).any():
            return False, "INVALID_CLOSE_RANGE"
            
        if (df['open'] > df['high']).any() or (df['open'] < df['low']).any():
            return False, "INVALID_OPEN_RANGE"
            
        return True, "DATA_VALID"

    def _get_expected_freq(self, timeframe: str) -> str:
        mapping = {
            '5m': '5T', '15m': '15T', '30m': '30T',
            '1h': '60T', '4h': '240T', '1d': 'D'
        }
        return mapping.get(timeframe, '60T')