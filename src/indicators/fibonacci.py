"""محاسبه سطوح فیبوناچی Retracement و Extension بین دو نقطه سوینگ."""
from typing import Dict


RETRACEMENT_LEVELS = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
EXTENSION_LEVELS = [1.272, 1.414, 1.618, 2.0, 2.618]


def fibonacci_retracement(swing_high: float, swing_low: float) -> Dict[float, float]:
    """در روند صعودی: swing_low -> swing_high؛ در نزولی برعکس بده."""
    diff = swing_high - swing_low
    return {level: swing_high - diff * level for level in RETRACEMENT_LEVELS}


def fibonacci_extension(swing_high: float, swing_low: float) -> Dict[float, float]:
    diff = swing_high - swing_low
    return {level: swing_low + diff * level for level in EXTENSION_LEVELS}
