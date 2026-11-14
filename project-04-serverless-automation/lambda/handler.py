import json
import urllib.parse
import boto3

s3 = boto3.client("s3")
OUTPUT_BUCKET = "documents-processed-example"

def lambda_handler(event, context):
    processed = []
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])
        body = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
        output_key = "processed/" + key.split("/")[-1]
        s3.put_object(Bucket=OUTPUT_BUCKET, Key=output_key, Body=body)
        print(json.dumps({"input": key, "output": output_key, "bytes": len(body)}))
        processed.append(output_key)
    return {"processed": processed}
