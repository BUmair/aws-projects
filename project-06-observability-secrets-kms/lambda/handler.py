import json
import os

import boto3

secrets = boto3.client("secretsmanager")
SECRET_ID = os.environ["SECRET_ID"]
_cache = {}


def get_config():
    # Cache the secret across warm invocations to cut Secrets Manager calls.
    if "config" not in _cache:
        response = secrets.get_secret_value(SecretId=SECRET_ID)
        _cache["config"] = json.loads(response["SecretString"])
    return _cache["config"]


def handler(event, context):
    try:
        config = get_config()
        # Log the key names only. Never log secret values.
        print(json.dumps({"level": "INFO", "message": "secret loaded", "keys": sorted(config.keys())}))
        return {"statusCode": 200, "body": "ok"}
    except Exception as err:
        print(json.dumps({"level": "ERROR", "message": str(err)}))
        raise
