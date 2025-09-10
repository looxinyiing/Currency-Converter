from datetime import date, datetime
from typing import Any, Dict, Iterable, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://api.frankfurter.app"

def _build_session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, read=3, connect=3,
                  backoff_factor=0.3,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=frozenset(["GET"]),
                  raise_on_status=False)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent": "fx-converter/1.0"})
    return s

_SESSION = _build_session()

DateLike = Union[str, date, datetime]

def _iso_date(d: DateLike) -> str:
    if isinstance(d, str):
        return d[:10]
    if isinstance(d, datetime):
        return d.date().isoformat()
    if isinstance(d, date):
        return d.isoformat()
    raise TypeError("Unsupported date type")

def _comma_list(symbols: Union[str, Iterable[str]]) -> str:
    if isinstance(symbols, str):
        return symbols
    return ",".join(list(symbols))

def _get(path: str, params: Optional[Dict[str, Any]] = None, timeout: float = 10.0) -> Dict[str, Any]:
    url = f"{BASE_URL}{path}"
    r = _SESSION.get(url, params=params or {}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def currencies() -> Dict[str, str]:
    return _get("/currencies")

def latest(base: str, symbols: Union[str, Iterable[str]], amount: Optional[float] = None) -> Dict[str, Any]:
    if not base:
        raise ValueError("base is required")
    params: Dict[str, Any] = {"from": base, "to": _comma_list(symbols)}
    if amount is not None:
        params["amount"] = amount
    return _get("/latest", params=params)

def historical(on_date: DateLike, base: str, symbols: Union[str, Iterable[str]], amount: Optional[float] = None) -> Dict[str, Any]:
    if not base:
        raise ValueError("base is required")
    day = _iso_date(on_date)
    params: Dict[str, Any] = {"from": base, "to": _comma_list(symbols)}
    if amount is not None:
        params["amount"] = amount
    return _get(f"/{day}", params=params)
