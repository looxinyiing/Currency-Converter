
import streamlit as st
from datetime import date
from typing import Dict
from frankfurter import get_currencies, get_latest_rate, get_historical_rate

# ---------- Page setup ----------
st.set_page_config(page_title="FX Converter", page_icon="🔗", layout="centered")
st.title("FX Converter")

# ---------- Utilities (formatting text exactly like screenshot) ----------
def _trim(s: str) -> str:
    s = s.rstrip("0").rstrip(".")
    return s if s else "0"

def _fmt_amount(x: float) -> str:
    v = float(x)
    # one decimal if integer (e.g., 50.0), else two decimals
    return f"{v:.1f}" if v.is_integer() else _trim(f"{v:.2f}")

def _fmt_rate(r: float) -> str:
    # 5 decimals when < 1.0, else 2 decimals
    return f"{r:.5f}" if r < 1 else _trim(f"{r:.2f}")

def _fmt_inverse(r: float) -> str:
    # Always 4 decimals per screenshot
    return f"{r:.4f}"

def format_message(date_str: str, base: str, target: str, rate: float, amount: float) -> str:
    to_value = amount * rate
    inv = 1.0 / rate
    return (
        f"The conversion rate on {date_str} from {base} to {target} was {_fmt_rate(rate)}. "
        f"So {_fmt_amount(amount)} in {base} correspond to {_fmt_amount(to_value)} in {target}. "
        f"The inverse rate was {_fmt_inverse(inv)}."
    )

@st.cache_data(ttl=6 * 60 * 60)
def load_currencies() -> Dict[str, str]:
    # Sorted dict of currency code -> name
    try:
        import json  # local import to avoid polluting global namespace
        from frankfurter import get_currencies
        data = dict(sorted(get_currencies().items()))
    except Exception:
        data = {}
    return data

currencies = load_currencies()
codes = list(currencies.keys())

# Fallback if API failed
if not codes:
    st.error("Failed to load currencies.")
    st.stop()

# ---------- Controls (match screenshot order & labels) ----------
st.markdown("Enter the amount to be converted:")
amount = st.number_input("", min_value=0.0, value=50.0, step=1.0, key="amount", label_visibility="collapsed")

st.markdown("From Currency:")
from_code = st.selectbox(
    "",
    options=codes,
    index=codes.index("AUD") if "AUD" in codes else 0,
    format_func=lambda c: c,
    key="from",
    label_visibility="collapsed",
)

st.markdown("To Currency:")
to_code = st.selectbox(
    "",
    options=codes,
    index=codes.index("USD") if "USD" in codes else 0,
    format_func=lambda c: c,
    key="to",
    label_visibility="collapsed",
)

# Buttons in the same positions and with exact labels
if st.button("Get Latest Rate"):
    try:
        rate = 1.0 if from_code == to_code else float(get_latest_rate(from_code, to_code))
        st.subheader("Latest Conversion Rate")
        st.write(format_message(date.today().isoformat(), from_code, to_code, rate, amount))
    except Exception as e:
        st.error(f"Failed to fetch latest rate: {e}")

st.markdown("Select a date for historical rates:")
hist_date = st.date_input("", value=date(2024, 9, 1), max_value=date.today(), key="hist_date", label_visibility="collapsed")

if st.button("Conversion Rate"):
    try:
        rate = 1.0 if from_code == to_code else float(get_historical_rate(hist_date, from_code, to_code))
        st.subheader("Conversion Rate")
        st.write(format_message(hist_date.isoformat(), from_code, to_code, rate, amount))
    except Exception as e:
        st.error(f"Failed to fetch historical rate: {e}")
