"""
AI Signal Engine - Tabdeal DNA Collector
----------------------------------------
Research-only collector for asset behavioral DNA.

Design:
- Source: Tabdeal public market API (no API key for market endpoints)
- Raw base timeframe: 15m
- Derived timeframes: 30m, 1H, 4H, 1D
- Aggregation clock: Europe/London with DST-aware timezone handling
- History: 3 years by default, or from the requested start date
- DNA is asset + timeframe + regime specific
- BUY and SELL behavior are measured separately
- This module does NOT generate live signals and does NOT run an AI backtest.

The Tabdeal API is Binance-compatible in naming for public market endpoints.
The historical-kline pagination parameters startTime/endTime are attempted first.
If the endpoint does not honor them, the collector stops rather than silently
creating a false three-year history.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


BASE_URL = os.getenv("TABDEAL_BASE_URL", "https://api1.tabdeal.org").rstrip("/")
KLINES_PATH = "/r/api/v1/klines"
EXCHANGE_INFO_PATH = "/r/api/v1/exchangeInfo"

RAW_INTERVAL = "15m"
TIMEFRAMES = ("15m", "30m", "1H", "4H", "1D")
LONDON_TZ = "Europe/London"
DEFAULT_YEARS = 3
PAGE_LIMIT = 1000
REQUEST_DELAY = 0.15
TIMEOUT = 20

DEFAULT_SYMBOLS = (
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "SOLUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "LINKUSDT",
    "AVAXUSDT",
    "SUIUSDT",
)


@dataclass(frozen=True)
class EventResult:
    name: str
    side: str
    parameters: Dict[str, Any]
    samples: int
    forward_1_mean: float
    forward_4_mean: float
    forward_8_mean: float
    forward_16_mean: float
    win_rate_8: float
    mfe_mean: float
    mae_mean: float
    median_forward_8: float

    def as_dict(self) -> Dict[str, Any]:
        return {
            "event": self.name,
            "side": self.side,
            "parameters": self.parameters,
            "samples": self.samples,
            "forward_return_mean": {
                "1": self.forward_1_mean,
                "4": self.forward_4_mean,
                "8": self.forward_8_mean,
                "16": self.forward_16_mean,
            },
            "win_rate_8": self.win_rate_8,
            "mfe_mean": self.mfe_mean,
            "mae_mean": self.mae_mean,
            "median_forward_8": self.median_forward_8,
        }


def request_json(path: str, params: Optional[Dict[str, Any]] = None) -> Any:
    query = urlencode(params or {})
    url = f"{BASE_URL}{path}"
    if query:
        url += f"?{query}"

    req = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "AI-Signal-Engine-DNA/1.0",
        },
        method="GET",
    )
    with urlopen(req, timeout=TIMEOUT) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_symbol(symbol: str) -> str:
    return (
        str(symbol).strip().upper()
        .replace("/", "")
        .replace("_", "")
        .replace("-", "")
    )


def fetch_exchange_symbols() -> List[str]:
    payload = request_json(EXCHANGE_INFO_PATH)
    result: List[str] = []

    for item in payload.get("symbols", []):
        if not isinstance(item, dict):
            continue
        symbol = item.get("symbol") or item.get("tabdealSymbol")
        if symbol:
            result.append(normalize_symbol(symbol))

    return sorted(set(result))


def _rows_to_frame(rows: List[Any]) -> pd.DataFrame:
    data = []
    for row in rows:
        if isinstance(row, (list, tuple)) and len(row) >= 6:
            data.append(
                {
                    "open_time": int(row[0]),
                    "open": float(row[1]),
                    "high": float(row[2]),
                    "low": float(row[3]),
                    "close": float(row[4]),
                    "volume": float(row[5]),
                }
            )
        elif isinstance(row, dict):
            ts = row.get("open_time", row.get("openTime", row.get("timestamp", row.get("time"))))
            if ts is None:
                continue
            data.append(
                {
                    "open_time": int(ts),
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row.get("volume", row.get("vol", 0))),
                }
            )

    if not data:
        return pd.DataFrame(columns=["open", "high", "low", "close", "volume"])

    df = pd.DataFrame(data)
    df["timestamp"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df = df.drop_duplicates("timestamp").sort_values("timestamp")
    df = df.set_index("timestamp")
    return df[["open", "high", "low", "close", "volume"]]


def fetch_15m_history(
    symbol: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    """Fetch ascending 15m candles using time-window pagination."""
    symbol = normalize_symbol(symbol)
    start_ms = int(start.timestamp() * 1000)
    end_ms = int(end.timestamp() * 1000)

    batches: List[pd.DataFrame] = []
    cursor = start_ms
    previous_last: Optional[int] = None

    while cursor < end_ms:
        params = {
            "symbol": symbol,
            "interval": RAW_INTERVAL,
            "startTime": cursor,
            "endTime": end_ms,
            "limit": PAGE_LIMIT,
        }

        rows = request_json(KLINES_PATH, params)
        page = _rows_to_frame(rows)

        if page.empty:
            break

        batches.append(page)
        last_ms = int(page.index[-1].timestamp() * 1000)

        if previous_last is not None and last_ms <= previous_last:
            raise RuntimeError(
                f"{symbol}: Tabdeal kline endpoint did not advance pagination. "
                "Refusing to fabricate/duplicate history."
            )

        previous_last = last_ms
        next_cursor = last_ms + 15 * 60 * 1000

        if next_cursor <= cursor:
            raise RuntimeError(f"{symbol}: invalid pagination cursor")

        cursor = next_cursor
        time.sleep(REQUEST_DELAY)

        if len(page) < PAGE_LIMIT and last_ms >= end_ms - 15 * 60 * 1000:
            break

    if not batches:
        raise RuntimeError(f"{symbol}: no 15m candles returned")

    df = pd.concat(batches)
    df = df[~df.index.duplicated(keep="first")].sort_index()
    df = df[(df.index >= start) & (df.index < end)]

    # Drop an incomplete current candle.
    now = pd.Timestamp.now(tz="UTC")
    current_open = now.floor("15min")
    df = df[df.index < current_open]

    return df


def expected_bars_for_group(start_local: pd.Timestamp, end_local: pd.Timestamp) -> int:
    delta = end_local.tz_convert("UTC") - start_local.tz_convert("UTC")
    return int(delta.total_seconds() // (15 * 60))


def london_resample(raw: pd.DataFrame, rule: str, expected: Optional[int]) -> pd.DataFrame:
    """Aggregate UTC 15m candles on London clock boundaries, including DST."""
    if raw.empty:
        return raw.copy()

    local = raw.copy()
    local.index = local.index.tz_convert(LONDON_TZ)

    grouped = local.resample(
        rule,
        label="left",
        closed="left",
        origin="start_day",
    )

    result = grouped.agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )

    counts = grouped["close"].count()
    result["source_15m_count"] = counts

    if expected is not None:
        result = result[result["source_15m_count"] == expected]
    elif rule == "1D":
        # London DST makes a local day 23, 24, or 25 hours.
        valid = []
        for idx, row in result.iterrows():
            next_day = idx + pd.Timedelta(days=1)
            needed = expected_bars_for_group(idx, next_day)
            valid.append(int(row["source_15m_count"]) == needed)
        result = result[np.asarray(valid, dtype=bool)]

    result.index.name = "open_time_london"
    return result.drop(columns=["source_15m_count"])


def build_timeframes(raw: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    return {
        "15m": raw.copy(),
        "30m": london_resample(raw, "30min", 2),
        "1H": london_resample(raw, "1h", 4),
        "4H": london_resample(raw, "4h", 16),
        "1D": london_resample(raw, "1D", None),
    }


def ema(s: pd.Series, period: int) -> pd.Series:
    return s.ewm(span=period, adjust=False, min_periods=period).mean()


def rsi(close: pd.Series, period: int) -> pd.Series:
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    avg_up = up.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    avg_down = down.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    rs = avg_up / avg_down.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def macd(close: pd.Series, fast: int, slow: int, signal: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
    line = ema(close, fast) - ema(close, slow)
    sig = ema(line, signal)
    return line, sig, line - sig


def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    prev = df["close"].shift(1)
    tr = pd.concat(
        [
            df["high"] - df["low"],
            (df["high"] - prev).abs(),
            (df["low"] - prev).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def ichimoku(df: pd.DataFrame, tenkan: int, kijun: int, span_b: int) -> pd.DataFrame:
    high = df["high"]
    low = df["low"]
    tenkan_line = (high.rolling(tenkan).max() + low.rolling(tenkan).min()) / 2
    kijun_line = (high.rolling(kijun).max() + low.rolling(kijun).min()) / 2
    span_a = (tenkan_line + kijun_line) / 2
    span_b_line = (high.rolling(span_b).max() + low.rolling(span_b).min()) / 2
    top = pd.concat([span_a, span_b_line], axis=1).max(axis=1)
    bottom = pd.concat([span_a, span_b_line], axis=1).min(axis=1)
    return pd.DataFrame(
        {
            "tenkan": tenkan_line,
            "kijun": kijun_line,
            "cloud_top": top,
            "cloud_bottom": bottom,
        },
        index=df.index,
    )


def forward_event_stats(
    df: pd.DataFrame,
    event: pd.Series,
    side: str,
    name: str,
    parameters: Dict[str, Any],
    horizons: Tuple[int, ...] = (1, 4, 8, 16),
) -> Optional[EventResult]:
    event = event.fillna(False).astype(bool)
    positions = np.flatnonzero(event.to_numpy())

    if len(positions) < 30:
        return None

    close = df["close"].to_numpy(dtype=float)
    high = df["high"].to_numpy(dtype=float)
    low = df["low"].to_numpy(dtype=float)

    returns: Dict[int, List[float]] = {h: [] for h in horizons}
    mfe: List[float] = []
    mae: List[float] = []

    for i in positions:
        if i + max(horizons) >= len(df):
            continue

        entry = close[i]
        if not np.isfinite(entry) or entry <= 0:
            continue

        for h in horizons:
            r = close[i + h] / entry - 1.0
            returns[h].append(float(r if side == "BUY" else -r))

        future_high = high[i + 1 : i + 17]
        future_low = low[i + 1 : i + 17]
        if side == "BUY":
            mfe.append(float(np.max(future_high) / entry - 1.0))
            mae.append(float(1.0 - np.min(future_low) / entry))
        else:
            mfe.append(float(1.0 - np.min(future_low) / entry))
            mae.append(float(np.max(future_high) / entry - 1.0))

    if len(returns[8]) < 30:
        return None

    r8 = np.asarray(returns[8])
    return EventResult(
        name=name,
        side=side,
        parameters=parameters,
        samples=int(len(r8)),
        forward_1_mean=float(np.mean(returns[1])),
        forward_4_mean=float(np.mean(returns[4])),
        forward_8_mean=float(np.mean(returns[8])),
        forward_16_mean=float(np.mean(returns[16])),
        win_rate_8=float(np.mean(r8 > 0)),
        mfe_mean=float(np.mean(mfe)),
        mae_mean=float(np.mean(mae)),
        median_forward_8=float(np.median(r8)),
    )


def indicator_events(df: pd.DataFrame) -> Iterable[Tuple[str, str, Dict[str, Any], pd.Series]]:
    close = df["close"]

    # RSI behavior: both the extreme state and the recovery from the extreme.
    for period in (7, 9, 14, 21):
        x = rsi(close, period)
        for threshold in (20, 30):
            yield (
                "RSI_EXTREME",
                "BUY",
                {"period": period, "threshold": threshold},
                x < threshold,
            )
            yield (
                "RSI_RECOVERY",
                "BUY",
                {"period": period, "threshold": threshold},
                (x.shift(1) < threshold) & (x >= threshold),
            )
        for threshold in (70, 80):
            yield (
                "RSI_EXTREME",
                "SELL",
                {"period": period, "threshold": threshold},
                x > threshold,
            )
            yield (
                "RSI_RECOVERY",
                "SELL",
                {"period": period, "threshold": threshold},
                (x.shift(1) > threshold) & (x <= threshold),
            )

    # MACD variants.
    for fast, slow, signal in ((8, 21, 5), (12, 26, 9), (19, 39, 9)):
        line, sig, hist = macd(close, fast, slow, signal)
        params = {"fast": fast, "slow": slow, "signal": signal}
        yield ("MACD_CROSS", "BUY", params, (line.shift(1) <= sig.shift(1)) & (line > sig))
        yield ("MACD_CROSS", "SELL", params, (line.shift(1) >= sig.shift(1)) & (line < sig))
        yield ("MACD_ZERO", "BUY", params, (hist.shift(1) <= 0) & (hist > 0))
        yield ("MACD_ZERO", "SELL", params, (hist.shift(1) >= 0) & (hist < 0))

    # Ichimoku variants. No forward shift is used for the measured event.
    for tenkan, kijun, span_b in ((9, 26, 52), (7, 22, 44), (12, 30, 60)):
        ichi = ichimoku(df, tenkan, kijun, span_b)
        params = {"tenkan": tenkan, "kijun": kijun, "span_b": span_b}
        yield (
            "ICHIMOKU_CLOUD_STATE",
            "BUY",
            params,
            close > ichi["cloud_top"],
        )
        yield (
            "ICHIMOKU_CLOUD_STATE",
            "SELL",
            params,
            close < ichi["cloud_bottom"],
        )
        yield (
            "ICHIMOKU_KIJUN_RECLAIM",
            "BUY",
            params,
            (close.shift(1) <= ichi["kijun"].shift(1)) & (close > ichi["kijun"]),
        )
        yield (
            "ICHIMOKU_KIJUN_REJECT",
            "SELL",
            params,
            (close.shift(1) >= ichi["kijun"].shift(1)) & (close < ichi["kijun"]),
        )

    # Volume behavior.
    for period in (10, 20, 30, 50):
        vma = df["volume"].rolling(period).mean()
        for multiplier in (1.5, 2.0):
            event = df["volume"] > vma * multiplier
            params = {"volume_ma": period, "multiplier": multiplier}
            yield ("VOLUME_EXPANSION", "BUY", params, event)
            yield ("VOLUME_EXPANSION", "SELL", params, event)

    # Trend regime behavior.
    for fast, slow in ((20, 50), (50, 200)):
        fast_ema = ema(close, fast)
        slow_ema = ema(close, slow)
        params = {"fast": fast, "slow": slow}
        yield ("EMA_TREND", "BUY", params, fast_ema > slow_ema)
        yield ("EMA_TREND", "SELL", params, fast_ema < slow_ema)

    # ATR regime.
    x = atr(df, 14)
    atr_pct = x / close
    med = atr_pct.rolling(100).median()
    yield ("ATR_HIGH_REGIME", "BUY", {"period": 14}, atr_pct > med)
    yield ("ATR_HIGH_REGIME", "SELL", {"period": 14}, atr_pct > med)


def pivot_events(df: pd.DataFrame) -> Iterable[Tuple[str, str, Dict[str, Any], pd.Series]]:
    if len(df) < 10:
        return

    # Previous-bar pivot is deliberately causal.
    prev = df.shift(1)
    pivot = (prev["high"] + prev["low"] + prev["close"]) / 3
    r1 = 2 * pivot - prev["low"]
    s1 = 2 * pivot - prev["high"]

    tolerance = atr(df, 14) * 0.25

    yield (
        "PIVOT_SUPPORT_TOUCH",
        "BUY",
        {"type": "classic", "tolerance_atr": 0.25},
        (df["low"] - s1).abs() <= tolerance,
    )
    yield (
        "PIVOT_RESISTANCE_TOUCH",
        "SELL",
        {"type": "classic", "tolerance_atr": 0.25},
        (df["high"] - r1).abs() <= tolerance,
    )


def fib_events(df: pd.DataFrame) -> Iterable[Tuple[str, str, Dict[str, Any], pd.Series]]:
    # Rolling swings keep this causal and avoid future-looking swing selection.
    lookback = 50
    swing_high = df["high"].rolling(lookback).max().shift(1)
    swing_low = df["low"].rolling(lookback).min().shift(1)
    span = swing_high - swing_low
    atr14 = atr(df, 14)

    for level in (0.778, 0.886, 1.0, 1.272, 1.382, 1.618):
        buy_level = swing_high - span * level
        sell_level = swing_low + span * level
        tol = atr14 * 0.20
        params = {"lookback": lookback, "level": level, "tolerance_atr": 0.20}
        yield ("FIB_REACTION", "BUY", params, (df["low"] - buy_level).abs() <= tol)
        yield ("FIB_REACTION", "SELL", params, (df["high"] - sell_level).abs() <= tol)


def breakout_retest_events(df: pd.DataFrame) -> Iterable[Tuple[str, str, Dict[str, Any], pd.Series]]:
    lookback = 20
    atr14 = atr(df, 14)
    resistance = df["high"].rolling(lookback).max().shift(1)
    support = df["low"].rolling(lookback).min().shift(1)
    tol = atr14 * 0.25

    # A valid retest requires an earlier breakout and then a return to the broken level.
    prior_breakout_up = (df["close"].shift(1) > resistance.shift(1)).rolling(8).max().fillna(0).astype(bool)
    prior_breakout_down = (df["close"].shift(1) < support.shift(1)).rolling(8).min().fillna(0).astype(bool)

    buy_retest = prior_breakout_up & (df["low"] - resistance).abs().le(tol) & (df["close"] > resistance)
    sell_retest = prior_breakout_down & (df["high"] - support).abs().le(tol) & (df["close"] < support)

    params = {"breakout_lookback": lookback, "retest_window": 8, "tolerance_atr": 0.25}
    yield ("BREAKOUT_RETEST", "BUY", params, buy_retest)
    yield ("BREAKOUT_RETEST", "SELL", params, sell_retest)


def calculate_dna(df: pd.DataFrame, symbol: str, timeframe: str) -> Dict[str, Any]:
    events: List[Dict[str, Any]] = []

    generators = [
        indicator_events(df),
        pivot_events(df),
        fib_events(df),
        breakout_retest_events(df),
    ]

    for generator in generators:
        for name, side, params, mask in generator:
            result = forward_event_stats(
                df=df,
                event=mask,
                side=side,
                name=name,
                parameters=params,
            )
            if result is not None:
                events.append(result.as_dict())

    # Compact structural statistics, not a signal score.
    ret = df["close"].pct_change()
    up = ret > 0
    down = ret < 0
    atr_pct = atr(df, 14) / df["close"]

    buy_events = [x for x in events if x["side"] == "BUY"]
    sell_events = [x for x in events if x["side"] == "SELL"]

    return {
        "schema_version": "DNA-1.0",
        "market": "CRYPTO",
        "symbol": symbol,
        "timeframe": timeframe,
        "source": "TABDEAL",
        "raw_base_timeframe": RAW_INTERVAL,
        "clock_timezone": LONDON_TZ,
        "history": {
            "start": df.index[0].isoformat() if len(df) else None,
            "end": df.index[-1].isoformat() if len(df) else None,
            "candles": int(len(df)),
        },
        "structural_behavior": {
            "up_candle_ratio": float(up.mean()),
            "down_candle_ratio": float(down.mean()),
            "median_return": float(ret.median()),
            "median_atr_pct": float(atr_pct.median()),
            "mean_atr_pct": float(atr_pct.mean()),
        },
        "buy_behavior": buy_events,
        "sell_behavior": sell_events,
        "methodology": {
            "separate_buy_sell": True,
            "asset_specific": True,
            "timeframe_specific": True,
            "regime_aware_parameters": True,
            "forward_horizons_bars": [1, 4, 8, 16],
            "no_ai_backtest": True,
            "higher_timeframes_derived_from_15m": True,
            "dst_aware_london_alignment": True,
        },
    }


def save_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out.index = out.index.astype(str)
    out.to_csv(path, index_label="open_time")


def save_json(data: Dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


def collect_symbol(
    symbol: str,
    start: pd.Timestamp,
    end: pd.Timestamp,
    out_dir: Path,
) -> Dict[str, Any]:
    print(f"[DNA] {symbol}: fetching 15m...")
    raw = fetch_15m_history(symbol, start, end)

    raw_dir = out_dir / "raw_15m"
    dna_dir = out_dir / "dna"

    save_frame(raw, raw_dir / f"{symbol}_15m.csv")

    frames = build_timeframes(raw)
    summary: Dict[str, Any] = {
        "symbol": symbol,
        "source": "TABDEAL",
        "raw_15m_candles": int(len(raw)),
        "timeframes": {},
    }

    for timeframe, frame in frames.items():
        if len(frame) < 300:
            print(f"[DNA] {symbol} {timeframe}: only {len(frame)} candles; DNA skipped")
            summary["timeframes"][timeframe] = {"candles": int(len(frame)), "dna": False}
            continue

        print(f"[DNA] {symbol} {timeframe}: {len(frame)} candles -> DNA")
        dna = calculate_dna(frame, symbol, timeframe)
        save_json(dna, dna_dir / f"{symbol}_{timeframe}_dna.json")
        save_frame(frame, out_dir / "derived" / timeframe / f"{symbol}_{timeframe}.csv")
        summary["timeframes"][timeframe] = {"candles": int(len(frame)), "dna": True}

    save_json(summary, out_dir / "summaries" / f"{symbol}_summary.json")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Tabdeal 15m history and build behavioral DNA.")
    parser.add_argument("--symbols", nargs="+", default=list(DEFAULT_SYMBOLS))
    parser.add_argument("--years", type=int, default=DEFAULT_YEARS)
    parser.add_argument("--out-dir", default="RnD/data/tabdeal_dna")
    parser.add_argument("--discover", action="store_true", help="Print Tabdeal symbols and exit.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.discover:
        symbols = fetch_exchange_symbols()
        print(json.dumps(symbols, ensure_ascii=False, indent=2))
        return

    end = pd.Timestamp.now(tz="UTC").floor("15min")
    start = end - pd.DateOffset(years=args.years)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "schema_version": "DNA-1.0",
        "source": "TABDEAL",
        "raw_timeframe": RAW_INTERVAL,
        "derived_timeframes": list(TIMEFRAMES),
        "timezone": LONDON_TZ,
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat(),
        "symbols": [normalize_symbol(s) for s in args.symbols],
    }
    save_json(manifest, out_dir / "manifest.json")

    results = []
    for symbol in [normalize_symbol(s) for s in args.symbols]:
        try:
            results.append(collect_symbol(symbol, start, end, out_dir))
        except Exception as exc:
            print(f"[ERROR] {symbol}: {exc}")
            results.append({"symbol": symbol, "error": str(exc)})

    save_json(
        {"manifest": manifest, "results": results},
        out_dir / "collection_report.json",
    )


if __name__ == "__main__":
    main()
