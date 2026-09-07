"""Explicit brokerage operations. No orders are placed by strategies or imports."""

import json
import math
import re
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class OrderPreview:
    symbol: str
    quantity: float
    side: str
    reference_price: float
    estimated_notional: float
    client_order_id: str


def preview_order(
    symbol: str,
    quantity: float,
    side: str,
    price: float,
    *,
    maximum_notional: float,
    client_order_id: str,
) -> OrderPreview:
    if not re.fullmatch(r"[A-Z][A-Z0-9./-]{0,20}", symbol) or side not in ("buy", "sell"):
        raise ValueError("valid symbol and buy/sell side required")
    if not all(math.isfinite(x) and x > 0 for x in (quantity, price, maximum_notional)):
        raise ValueError("positive finite quantity, price and notional limit required")
    if not re.fullmatch(r"[\w-]{1,48}", client_order_id):
        raise ValueError("provide a stable 1–48 character client_order_id for this intended order")
    notional = quantity * price
    if notional > maximum_notional:
        raise ValueError("order exceeds maximum_notional")
    return OrderPreview(symbol, quantity, side, price, notional, client_order_id)


@dataclass(frozen=True)
class Alpaca:
    api_key: str = field(repr=False)
    secret_key: str = field(repr=False)
    paper: bool = True
    timeout: float = 20

    def _request(self, method: str, path: str, payload: dict | None = None):
        if not self.api_key or not self.secret_key or self.timeout <= 0:
            raise ValueError("Alpaca credentials and positive timeout required")
        host = "https://paper-api.alpaca.markets" if self.paper else "https://api.alpaca.markets"
        request = Request(
            host + path,
            method=method,
            data=json.dumps(payload).encode() if payload else None,
            headers={
                "APCA-API-KEY-ID": self.api_key,
                "APCA-API-SECRET-KEY": self.secret_key,
                "Content-Type": "application/json",
            },
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read()
            return json.loads(body) if body else None
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            # A timeout after submitting can mean accepted: look up the same client ID before retrying.
            raise RuntimeError(
                f"Alpaca {method} {path} failed ({type(exc).__name__}); reconcile order state before resubmitting"
            ) from exc

    def account(self) -> dict:
        return self._request("GET", "/v2/account")

    def positions(self) -> list[dict]:
        return self._request("GET", "/v2/positions")

    def orders(self) -> list[dict]:
        return self._request("GET", "/v2/orders?status=all&limit=100")

    def order_by_client_id(self, client_order_id: str) -> dict:
        return self._request(
            "GET",
            "/v2/orders:by_client_order_id?client_order_id=" + quote(client_order_id, safe=""),
        )

    def submit(self, order: OrderPreview, *, limit_price: float, allow_live: bool = False) -> dict:
        """Day limit order with a stable ID; caller reconciles fills/cancellations using broker state."""
        if not self.paper and not allow_live:
            raise ValueError("live execution requires allow_live=True")
        preview_order(
            order.symbol,
            order.quantity,
            order.side,
            order.reference_price,
            maximum_notional=order.estimated_notional,
            client_order_id=order.client_order_id,
        )
        if not float(order.quantity).is_integer():
            raise ValueError("this stock limit-order adapter requires whole shares")
        if not math.isfinite(limit_price) or limit_price <= 0:
            raise ValueError("positive finite limit_price required")
        if order.quantity * limit_price > order.estimated_notional * (1 + 1e-12):
            raise ValueError(
                "limit notional exceeds preview; generate a fresh preview at this limit"
            )
        return self._request(
            "POST",
            "/v2/orders",
            {
                "symbol": order.symbol,
                "qty": str(order.quantity),
                "side": order.side,
                "type": "limit",
                "time_in_force": "day",
                "limit_price": str(limit_price),
                "client_order_id": order.client_order_id,
            },
        )

    def cancel(self, order_id: str, *, allow_live: bool = False) -> None:
        if not self.paper and not allow_live:
            raise ValueError("live cancellation requires allow_live=True")
        self._request("DELETE", "/v2/orders/" + quote(order_id, safe=""))


def reconcile_orders(previews: list[OrderPreview], broker_orders: list[dict]):
    """Match intended IDs to broker state; unmatched intents are unknown, never assumed unfilled."""
    import pandas as pd

    keys = [p.client_order_id for p in previews]
    if len(keys) != len(set(keys)):
        raise ValueError("intended client IDs must be unique")
    known = {}
    for order in broker_orders:
        if "client_order_id" not in order or "status" not in order:
            raise ValueError("broker orders require client_order_id and status")
        key = order["client_order_id"]
        if key in known:
            raise ValueError("duplicate broker client ID")
        known[key] = order
    rows = []
    for preview in previews:
        order = known.get(preview.client_order_id)
        filled = float(order.get("filled_qty", 0)) if order else 0.0
        if not math.isfinite(filled) or filled < 0 or filled > preview.quantity + 1e-10:
            raise ValueError("invalid filled quantity")
        rows.append(
            {
                "client_order_id": preview.client_order_id,
                "symbol": preview.symbol,
                "status": order["status"] if order else "unknown",
                "quantity": preview.quantity,
                "filled_quantity": filled,
                "remaining_quantity": preview.quantity - filled,
                "average_fill_price": float(order["filled_avg_price"])
                if order and order.get("filled_avg_price")
                else None,
            }
        )
    return pd.DataFrame(rows)
