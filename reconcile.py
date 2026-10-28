#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP

latest_events = {}

with open("payments.jsonl") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        previous = latest_events.get(txn_id)
        if previous is None or event["ts"] >= previous["ts"]:
            latest_events[txn_id] = event

total = Decimal("0")
successful_events = [
    event for event in latest_events.values() if event["status"] == "success"
]
for event in successful_events:
    amount = str(event["amount"]).replace(",", "")
    total += Decimal(amount)

count = len(successful_events)

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    rounded_total = total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    print(f"Your code: KOYA-{rounded_total}")
