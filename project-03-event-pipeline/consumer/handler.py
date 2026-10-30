import json


def handler(event, context):
    failures = []

    for record in event["Records"]:
        message_id = record["messageId"]
        try:
            order = json.loads(record["body"])["detail"]
            amount = float(order["amount"])
            if amount <= 0:
                raise ValueError("amount must be positive")
            print(json.dumps({"level": "INFO", "orderId": order["orderId"], "amount": amount}))
        except (KeyError, ValueError, json.JSONDecodeError) as err:
            print(json.dumps({"level": "ERROR", "messageId": message_id, "error": str(err)}))
            failures.append({"itemIdentifier": message_id})

    # Only failed messages are returned to the queue (partial batch response).
    return {"batchItemFailures": failures}
