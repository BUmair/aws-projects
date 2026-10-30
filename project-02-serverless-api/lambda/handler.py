import json
import os
import uuid

import boto3
from botocore.exceptions import ClientError

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def respond(status, body=None):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body) if body is not None else "",
    }


def handler(event, context):
    http = event["requestContext"]["http"]
    method = http["method"]
    path = http["path"]
    item_id = (event.get("pathParameters") or {}).get("id")

    try:
        if method == "GET" and path == "/items":
            return respond(200, table.scan().get("Items", []))

        if method == "POST" and path == "/items":
            body = json.loads(event.get("body") or "{}")
            if "name" not in body:
                return respond(400, {"error": "name is required"})
            item = {"id": str(uuid.uuid4()), "name": body["name"]}
            table.put_item(Item=item)
            return respond(201, item)

        if method == "GET" and item_id:
            item = table.get_item(Key={"id": item_id}).get("Item")
            return respond(200, item) if item else respond(404, {"error": "not found"})

        if method == "DELETE" and item_id:
            table.delete_item(Key={"id": item_id})
            return respond(204)

        return respond(404, {"error": "route not found"})
    except json.JSONDecodeError:
        return respond(400, {"error": "invalid JSON"})
    except ClientError as err:
        print(json.dumps({"level": "ERROR", "message": str(err)}))
        return respond(500, {"error": "internal error"})
