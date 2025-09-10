
from datetime import date, datetime
from typing import Dict, Union
from api import currencies as _currencies, latest as _latest, historical as _historical

DateLike = Union[str, date, datetime]

def get_currencies() -> Dict[str, str]:
    """Return mapping of currency code -> currency name."""
    return _currencies()

def get_latest_rate(base: str, target: str) -> float:
    """Get latest exchange rate from `base` to `target`."""
    if not base or not target:
        raise ValueError("base/target required")
    data = _latest(base, target)
    rate = data.get("rates", {}).get(target)
    if rate is None:
        raise ValueError("rate not found")
    return float(rate)

def get_historical_rate(on_date: DateLike, base: str, target: str) -> float:
    """Get historical exchange rate on `on_date` (YYYY-MM-DD) from base to target."""
    if not base or not target:
        raise ValueError("base/target required")
    data = _historical(on_date, base, target)
    rate = data.get("rates", {}).get(target)
    if rate is None:
        raise ValueError("rate not found")
    return float(rate)
