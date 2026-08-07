"""
سیستم چندزبانه (فارسی/انگلیسی) داشبورد.

استفاده:
    from src.i18n import t, current_lang, set_lang, LANGS

    t("app_title")                 # متن ترجمه‌شده بر اساس زبان جاری (session_state)
    t("card_win_rate", wr=57.2)     # پشتیبانی از placeholder با .format()
"""
from __future__ import annotations

try:
    import streamlit as st
    _HAS_ST = True
except Exception:  # pragma: no cover
    _HAS_ST = False

from .translations import TRANSLATIONS

LANGS = {
    "fa": {"label": "🇮🇷 فارسی", "dir": "rtl", "font": "'Vazirmatn', Tahoma, sans-serif"},
    "en": {"label": "🇬🇧 English", "dir": "ltr", "font": "'Inter', 'Segoe UI', sans-serif"},
}

DEFAULT_LANG = "fa"


def current_lang() -> str:
    if _HAS_ST:
        return st.session_state.get("lang", DEFAULT_LANG)
    return DEFAULT_LANG


def set_lang(lang: str) -> None:
    if lang not in LANGS:
        lang = DEFAULT_LANG
    if _HAS_ST:
        st.session_state["lang"] = lang


def t(key: str, **kwargs) -> str:
    """رشته‌ی ترجمه‌شده را برمی‌گرداند. اگر کلید در زبان جاری نبود، به فارسی و سپس به خود کلید برمی‌گردد."""
    lang = current_lang()
    table = TRANSLATIONS.get(lang, {})
    text = table.get(key)
    if text is None:
        text = TRANSLATIONS.get(DEFAULT_LANG, {}).get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
