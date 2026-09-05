import itertools
from typing import List, Dict, Any
from datetime import datetime
import uuid

class ExperimentGenerator:
    """
    Generates experiment matrix based on campaign configuration.
    Creates unique IDs for each experiment.
    """
    
    def __init__(self, max_experiments: int = 1000):
        self.max_experiments = max_experiments

    def generate_matrix(
        self, 
        assets: List[str], 
        directions: List[str], 
        timeframes: List[str],
        regimes: List[str],
        tool_sets: List[List[str]],
        parameter_sets: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Generates a list of experiment configurations.
        """
        combinations = list(itertools.product(
            assets, directions, timeframes, regimes, tool_sets, parameter_sets
        ))
        
        if len(combinations) > self.max_experiments:
            # Simple sampling strategy if too many combinations
            # In production, this should be smarter (e.g., stratified sampling)
            import random
            random.shuffle(combinations)
            combinations = combinations[:self.max_experiments]
            
        experiments = []
        for asset, direction, timeframe, regime, tools, params in combinations:
            exp_id = f"RND-EXP-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"
            experiments.append({
                "experiment_id": exp_id,
                "asset": asset,
                "direction": direction,
                "timeframe": timeframe,
                "regime": regime,
                "tools": tools,
                "parameters": params,
                "status": "PENDING"
            })
            
        return experiments