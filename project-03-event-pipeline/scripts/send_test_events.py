"""Send one valid and one invalid OrderPlaced event to EventBridge.

Run with credentials for the account that owns the event bus:
    python scripts/send_test_events.py
"""

import json

import boto3

events = boto3.client("events", region_name="us-east-1")

samples = [
    {"orderId": "ord-1001", "amount": 42.5},  # valid: processed
    {"orderId": "ord-1002", "amount": -5},    # invalid: lands in the DLQ after 3 tries
]

response = events.put_events(
    Entries=[
        {
            "EventBusName": "default",
            "Source": "app.orders",
            "DetailType": "OrderPlaced",
            "Detail": json.dumps(order),
        }
        for order in samples
    ]
)

print(json.dumps(response, indent=2))
