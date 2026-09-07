"""Build an order and email preview locally. This example never submits or sends."""

from finance.integrations import email_report, preview_order, reconcile_orders


def main():
    order = preview_order(
        "AAPL", 2, "buy", 200, maximum_notional=500, client_order_id="example-aapl-001"
    )
    print(order)
    print(
        reconcile_orders(
            [order],
            [
                {
                    "client_order_id": order.client_order_id,
                    "status": "partially_filled",
                    "filled_qty": "1",
                    "filled_avg_price": "199.5",
                }
            ],
        )
    )
    print(email_report("research@example.com", "reader@example.com", "Order preview", str(order)))


if __name__ == "__main__":
    main()
