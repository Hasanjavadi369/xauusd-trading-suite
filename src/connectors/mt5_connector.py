"""
اتصال به MetaTrader 5.

این ماژول مسئول موارد زیر است:
  - برقراری اتصال به ترمینال MT5 نصب‌شده روی سیستم
  - دریافت داده‌های تاریخی و زنده (OHLCV) برای XAUUSD یا هر نماد دیگر
  - ارسال، ویرایش و بستن سفارش‌ها (Market / Pending)
  - دریافت اطلاعات حساب، موقعیت‌های باز و تاریخچه‌ی معاملات

توجه: پکیج رسمی ``MetaTrader5`` فقط روی ویندوز (یا Wine) کار می‌کند، چون
از طریق DLL با ترمینال MT5 ارتباط برقرار می‌کند. برای اجرا روی لینوکس/مک
باید MT5 را داخل یک ماشین مجازی ویندوزی یا از طریق Wine اجرا کنید، یا
از یک سرویس واسط (مثل یک اکسپرت آدوایزر + سوکت/فایل) استفاده کنید.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

import pandas as pd
from loguru import logger

try:
    import MetaTrader5 as mt5
except ImportError:  # pragma: no cover - در محیط‌های غیر ویندوزی
    mt5 = None
    logger.warning(
        "پکیج MetaTrader5 در دسترس نیست. حالت اتصال زنده غیرفعال است؛ "
        "فقط از داده‌های CSV/تاریخی می‌توانید استفاده کنید."
    )


TIMEFRAME_MAP = {
    "M1": "TIMEFRAME_M1",
    "M5": "TIMEFRAME_M5",
    "M15": "TIMEFRAME_M15",
    "M30": "TIMEFRAME_M30",
    "H1": "TIMEFRAME_H1",
    "H4": "TIMEFRAME_H4",
    "D1": "TIMEFRAME_D1",
    "W1": "TIMEFRAME_W1",
}


@dataclass
class MT5Credentials:
    login: Optional[int] = None
    password: Optional[str] = None
    server: Optional[str] = None
    path: Optional[str] = None  # مسیر terminal64.exe در صورت نیاز


class MT5Connector:
    """پوششی (wrapper) تمیز و امن روی پکیج MetaTrader5."""

    def __init__(self, credentials: Optional[MT5Credentials] = None, symbol: str = "XAUUSD"):
        self.credentials = credentials or MT5Credentials()
        self.symbol = symbol
        self._connected = False

    # ------------------------------------------------------------------ #
    # اتصال / قطع اتصال
    # ------------------------------------------------------------------ #
    def connect(self) -> bool:
        if mt5 is None:
            raise RuntimeError("پکیج MetaTrader5 نصب نیست یا سیستم‌عامل پشتیبانی نمی‌شود.")

        init_kwargs = {}
        if self.credentials.path:
            init_kwargs["path"] = self.credentials.path

        if not mt5.initialize(**init_kwargs):
            logger.error(f"اتصال اولیه به MT5 ناموفق بود: {mt5.last_error()}")
            return False

        if self.credentials.login and self.credentials.password and self.credentials.server:
            authorized = mt5.login(
                login=self.credentials.login,
                password=self.credentials.password,
                server=self.credentials.server,
            )
            if not authorized:
                logger.error(f"ورود به حساب ناموفق بود: {mt5.last_error()}")
                mt5.shutdown()
                return False

        if not mt5.symbol_select(self.symbol, True):
            logger.warning(f"نماد {self.symbol} در Market Watch فعال نشد.")

        self._connected = True
        logger.info(f"اتصال به MT5 برقرار شد. نماد فعال: {self.symbol}")
        return True

    def disconnect(self) -> None:
        if mt5 is not None and self._connected:
            mt5.shutdown()
            self._connected = False
            logger.info("اتصال MT5 قطع شد.")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    # ------------------------------------------------------------------ #
    # داده‌های بازار
    # ------------------------------------------------------------------ #
    def get_ohlcv(self, timeframe: str = "H1", n_bars: int = 1000) -> pd.DataFrame:
        """دریافت n_bars کندل آخر برای نماد فعال."""
        if mt5 is None:
            raise RuntimeError("MetaTrader5 در دسترس نیست.")
        tf_const = getattr(mt5, TIMEFRAME_MAP[timeframe])
        rates = mt5.copy_rates_from_pos(self.symbol, tf_const, 0, n_bars)
        if rates is None or len(rates) == 0:
            raise RuntimeError(f"دریافت داده برای {self.symbol}/{timeframe} ناموفق بود: {mt5.last_error()}")
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.rename(columns={
            "time": "datetime", "open": "open", "high": "high",
            "low": "low", "close": "close", "tick_volume": "volume",
        })
        return df[["datetime", "open", "high", "low", "close", "volume"]].set_index("datetime")

    def get_ohlcv_range(self, timeframe: str, start: datetime, end: datetime) -> pd.DataFrame:
        if mt5 is None:
            raise RuntimeError("MetaTrader5 در دسترس نیست.")
        tf_const = getattr(mt5, TIMEFRAME_MAP[timeframe])
        rates = mt5.copy_rates_range(self.symbol, tf_const, start, end)
        if rates is None:
            raise RuntimeError(f"دریافت داده تاریخی ناموفق بود: {mt5.last_error()}")
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df = df.rename(columns={"time": "datetime", "tick_volume": "volume"})
        return df[["datetime", "open", "high", "low", "close", "volume"]].set_index("datetime")

    def get_current_price(self) -> Optional[dict]:
        if mt5 is None:
            return None
        tick = mt5.symbol_info_tick(self.symbol)
        if tick is None:
            return None
        return {"bid": tick.bid, "ask": tick.ask, "time": datetime.fromtimestamp(tick.time)}

    # ------------------------------------------------------------------ #
    # حساب و موقعیت‌ها
    # ------------------------------------------------------------------ #
    def get_account_info(self) -> Optional[dict]:
        if mt5 is None:
            return None
        info = mt5.account_info()
        return info._asdict() if info else None

    def get_open_positions(self) -> List[dict]:
        if mt5 is None:
            return []
        positions = mt5.positions_get(symbol=self.symbol) or []
        return [p._asdict() for p in positions]

    # ------------------------------------------------------------------ #
    # ارسال / مدیریت سفارش
    # ------------------------------------------------------------------ #
    def send_market_order(
        self,
        direction: str,          # "BUY" یا "SELL"
        volume: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        comment: str = "xauusd-suite",
        deviation: int = 20,
        magic: int = 123456,
    ) -> dict:
        if mt5 is None:
            raise RuntimeError("MetaTrader5 در دسترس نیست.")

        tick = mt5.symbol_info_tick(self.symbol)
        order_type = mt5.ORDER_TYPE_BUY if direction.upper() == "BUY" else mt5.ORDER_TYPE_SELL
        price = tick.ask if direction.upper() == "BUY" else tick.bid

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": order_type,
            "price": price,
            "deviation": deviation,
            "magic": magic,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        if stop_loss:
            request["sl"] = stop_loss
        if take_profit:
            request["tp"] = take_profit

        result = mt5.order_send(request)
        if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
            logger.error(f"ارسال سفارش ناموفق بود: {result}")
        return result._asdict() if result else {}

    def modify_position(self, ticket: int, stop_loss: Optional[float] = None,
                         take_profit: Optional[float] = None) -> dict:
        if mt5 is None:
            raise RuntimeError("MetaTrader5 در دسترس نیست.")
        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": self.symbol,
            "position": ticket,
        }
        if stop_loss:
            request["sl"] = stop_loss
        if take_profit:
            request["tp"] = take_profit
        result = mt5.order_send(request)
        return result._asdict() if result else {}

    def close_position(self, ticket: int, volume: float) -> dict:
        if mt5 is None:
            raise RuntimeError("MetaTrader5 در دسترس نیست.")
        positions = mt5.positions_get(ticket=ticket)
        if not positions:
            raise ValueError(f"موقعیت {ticket} پیدا نشد.")
        pos = positions[0]
        tick = mt5.symbol_info_tick(self.symbol)
        close_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": self.symbol,
            "volume": volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "xauusd-suite-close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        result = mt5.order_send(request)
        return result._asdict() if result else {}
