"""Data leakage, temporal integrity and market-data validation."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Mapping, Any
import math

@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    rows: int
    errors: tuple[str,...]
    warnings: tuple[str,...]

def validate_ohlcv(rows: Sequence[Mapping[str,Any]]) -> ValidationReport:
    errors=[]; warnings=[]; last=None
    for i,r in enumerate(rows):
        for k in ("open","high","low","close"):
            try: x=float(r[k])
            except (KeyError,TypeError,ValueError): errors.append(f"row {i}: missing {k}"); continue
            if not math.isfinite(x) or x<=0: errors.append(f"row {i}: invalid {k}")
        try:
            o,h,l,c=[float(r[k]) for k in ("open","high","low","close")]
            if h<max(o,c) or l>min(o,c) or l>h: errors.append(f"row {i}: invalid OHLC geometry")
        except Exception: pass
        if "timestamp" in r:
            t=r["timestamp"]
            if last is not None and t<=last: errors.append(f"row {i}: timestamps not strictly increasing")
            last=t
        if "volume" in r:
            try:
                if float(r["volume"])<0: errors.append(f"row {i}: negative volume")
            except (TypeError,ValueError): warnings.append(f"row {i}: invalid volume")
    return ValidationReport(not errors,len(rows),tuple(errors),tuple(warnings))

def assert_no_future_features(feature_timestamps: Sequence[Any], label_timestamps: Sequence[Any]) -> None:
    if len(feature_timestamps)!=len(label_timestamps): raise ValueError("feature/label length mismatch")
    for i,(f,l) in enumerate(zip(feature_timestamps,label_timestamps)):
        if f>l: raise ValueError(f"future feature leakage at row {i}")
