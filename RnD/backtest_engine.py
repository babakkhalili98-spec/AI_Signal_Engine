For each signal, measures:
- Price movement at multiple time horizons
- Maximum favorable excursion (MFE)
- Maximum adverse excursion (MAE)
- Time to reach maximum moves
- Final outcome (success/failure/neutral)
"""

def __init__(self, config: Optional[BacktestConfig] = None):
    """
    Initialize the backtest engine.
    
    Args:
        config: Backtest configuration
    """
    self.config = config or BacktestConfig()
    self.results: List[BacktestResult] = []

def analyze(
    self,
    signals: List[HistoricalSignal],
    candles: List[Dict[str, Any]],
    symbol: str,
    market: str,
    asset_class: str,
    timeframe: str,
) -> BacktestResult:
    """
    Analyze historical signals against candle data.
    
    Args:
        signals: List of historical signals
        candles: Full candle data (must include data after signals)
        symbol: Trading symbol
        market: Market name
        asset_class: Asset class
        timeframe: Timeframe
        
    Returns:
        BacktestResult with analysis
    """
    if not signals:
        logger.warning("No signals to analyze")
        return self._empty_result(symbol, market, asset_class, timeframe)
    
    if not candles:
        logger.error("No candle data provided for outcome analysis")
        return self._empty_result(symbol, market, asset_class, timeframe)
    
    # Sort candles by timestamp
    sorted_candles = sorted(candles, key=lambda x: x.get("timestamp", ""))
    
    # Create candle lookup by timestamp for efficient access
    candle_by_timestamp = {}
    for candle in sorted_candles:
        ts = candle.get("timestamp")
        if ts:
            candle_by_timestamp[self._normalize_timestamp(ts)] = candle
    
    # Also create indexed list for horizon calculations
    candle_list = sorted_candles
    timestamp_to_index = {
        self._normalize_timestamp(c.get("timestamp")): i 
        for i, c in enumerate(candle_list)
    }
    
    metrics = RnDMetrics()
    signal_outcomes = []
    
    # Analyze each signal
    for signal in signals:
        signal_time = self._normalize_timestamp(signal.timestamp)
        
        # Find signal candle index
        if signal_time not in timestamp_to_index:
            logger.warning(f"Signal timestamp {signal_time} not found in candle data")
            continue
        
        signal_index = timestamp_to_index[signal_time]
        entry_price = signal.entry_price
        
        # Calculate outcomes at different horizons
        outcomes_at_horizons = {}
        max_favorable = 0.0
        max_adverse = 0.0
        candles_to_max_favorable = 0
        candles_to_max_adverse = 0
        
        for horizon in self.config.horizons:
            target_index = signal_index + horizon
            
            if target_index >= len(candle_list):
                outcomes_at_horizons[horizon] = None
                continue
            
            target_candle = candle_list[target_index]
            target_price = target_candle.get("close", entry_price)
            
            # Calculate percentage change based on direction
            if signal.direction.lower() in ["buy", "long"]:
                pct_change = ((target_price - entry_price) / entry_price) * 100
            else:  # sell/short
                pct_change = ((entry_price - target_price) / entry_price) * 100
            
            outcomes_at_horizons[horizon] = pct_change
        
        # Calculate MFE and MAE across all available future candles
        for i in range(signal_index + 1, min(signal_index + self.config.max_lookahead + 1, len(candle_list))):
            future_candle = candle_list[i]
            high = future_candle.get("high", future_candle.get("close", entry_price))
            low = future_candle.get("low", future_candle.get("close", entry_price))
            
            if signal.direction.lower() in ["buy", "long"]:
                favorable_pct = ((high - entry_price) / entry_price) * 100
                adverse_pct = ((low - entry_price) / entry_price) * 100
            else:
                favorable_pct = ((entry_price - low) / entry_price) * 100
                adverse_pct = ((entry_price - high) / entry_price) * 100
            
            if favorable_pct > max_favorable:
                max_favorable = favorable_pct
                candles_to_max_favorable = i - signal_index
            
            if adverse_pct < max_adverse:
                max_adverse = adverse_pct
                candles_to_max_adverse = i - signal_index
        
        # Determine final outcome
        final_outcome = self._determine_outcome(
            max_favorable, 
            max_adverse,
            outcomes_at_horizons.get(max(self.config.horizons), 0)
        )
        
        # Create SignalOutcome
        outcome = SignalOutcome(
            timestamp=signal.timestamp,
            direction=signal.direction,
            entry_price=entry_price,
            outcome_after_1candle=outcomes_at_horizons.get(1),
            outcome_after_3candles=outcomes_at_horizons.get(3),
            outcome_after_5candles=outcomes_at_horizons.get(5),
            outcome_after_10candles=outcomes_at_horizons.get(10),
            outcome_after_20candles=outcomes_at_horizons.get(20),
            max_favorable_excursion=max_favorable,
            max_adverse_excursion=max_adverse,
            candles_to_max_favorable=candles_to_max_favorable if max_favorable > 0 else None,
            candles_to_max_adverse=candles_to_max_adverse if max_adverse < 0 else None,
            final_outcome=final_outcome,
            indicators_used=signal.indicators,
            patterns_detected=signal.patterns,
            market_context=signal.market_context,
        )
        
        signal_outcomes.append(outcome)
        
        # Update metrics
        market_condition = signal.market_context.get("condition", "unknown") if signal.market_context else "unknown"
        
        metrics.add_signal_result(
            direction=signal.direction,
            final_outcome=final_outcome,
            favorable_excursion=max_favorable,
            adverse_excursion=max_adverse,
            candles_to_favorable=candles_to_max_favorable if max_favorable > 0 else None,
            candles_to_adverse=candles_to_max_adverse if max_adverse < 0 else None,
            timeframe=timeframe,
            market=market,
            asset=symbol,
            indicators=signal.indicators,
            patterns=signal.patterns,
            market_condition=market_condition,
        )
    
    # Determine date range
    timestamps = [s.timestamp for s in signals]
    start_date = min(timestamps) if timestamps else datetime.utcnow()
    end_date = max(timestamps) if timestamps else datetime.utcnow()
    
    # Create summary
    summary = {
        "success_rate": metrics.success_rate,
        "failure_rate": metrics.failure_rate,
        "avg_favorable_excursion": metrics.average_favorable_excursion,
        "avg_adverse_excursion": metrics.average_adverse_excursion,
        "total_signals_analyzed": len(signal_outcomes),
    }
    
    result = BacktestResult(
        symbol=symbol,
        market=market,
        asset_class=asset_class,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        total_signals=len(signal_outcomes),
        metrics=metrics,
        signal_outcomes=signal_outcomes,
        config=self.config,
        summary=summary,
    )
    
    self.results.append(result)
    return result

def _determine_outcome(
    self, 
    max_favorable: float, 
    max_adverse: float,
    final_move: Optional[float]
) -> str:
    """
    Determine if signal was successful, failed, or neutral.
    
    Logic:
    - If price moved favorably beyond threshold before moving adversely beyond threshold: success
    - If price moved adversely beyond threshold before moving favorably beyond threshold: failure
    - Otherwise: neutral
    """
    if final_move is None:
        return "neutral"
    
    if max_favorable >= self.config.success_threshold:
        if abs(max_adverse) < self.config.failure_threshold:
            return "success"
        # If both thresholds hit, check which came first would require tick data
        # For candle data, we consider it success if favorable > adverse
        if max_favorable > abs(max_adverse):
            return "success"
    
    if abs(max_adverse) >= self.config.failure_threshold:
        if max_favorable < self.config.success_threshold:
            return "failure"
        if abs(max_adverse) > max_favorable:
            return "failure"
    
    if abs(final_move) < self.config.neutral_zone:
        return "neutral"
    
    # Default based on final move direction
    if final_move > 0:
        return "success"
    elif final_move < 0:
        return "failure"
    else:
        return "neutral"

def _empty_result(
    self, 
    symbol: str, 
    market: str, 
    asset_class: str, 
    timeframe: str
) -> BacktestResult:
    """Create an empty result"""
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
        config=self.config,
        summary={},
    )

def _normalize_timestamp(self, timestamp) -> str:
    """Normalize timestamp to string for comparison"""
    if isinstance(timestamp, datetime):
        return timestamp.isoformat()
    if isinstance(timestamp, str):
        return timestamp
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp).isoformat()
    return str(timestamp)

def get_all_results(self) -> List[BacktestResult]:
    """Get all backtest results"""
    return self.results

def get_aggregate_metrics(self) -> Dict[str, Any]:
    """Get aggregate metrics across all backtests"""
    if not self.results:
        return {}
    
    total_signals = sum(r.total_signals for r in self.results)
    total_successes = sum(r.metrics.successful_signals for r in self.results)
    total_failures = sum(r.metrics.failed_signals for r in self.results)
    
    return {
        "total_backtests": len(self.results),
        "total_signals": total_signals,
        "overall_success_rate": total_successes / total_signals if total_signals > 0 else 0,
        "overall_failure_rate": total_failures / total_signals if total_signals > 0 else 0,
        "markets_analyzed": list(set(r.market for r in self.results)),
        "symbols_analyzed": list(set(r.symbol for r in self.results)),
        "timeframes_analyzed": list(set(r.timeframe for r in self.results)),
    }