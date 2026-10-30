# Project 6: Observability, Secrets, and Encryption (CloudWatch + Secrets Manager + KMS)

A Lambda function reads its settings from Secrets Manager. The secret is encrypted with a customer-managed KMS key. The function writes structured logs to CloudWatch. A metric filter counts errors, and an alarm sends an email when errors appear.

**Status:** Code and steps written. Not yet deployed to AWS.

## Architecture

```
Lambda "config-reader"
  │ secretsmanager:GetSecretValue
  ▼
Secrets Manager secret "app/config"  ──encrypted with──► KMS key (alias: app-config-key)
  │
  │ logs (JSON)
  ▼
CloudWatch log group /aws/lambda/config-reader
  │ metric filter: { $.level = "ERROR" }
  ▼
CloudWatch metric "ConfigErrors" ──alarm (>= 1)──► SNS topic ──► email
```

## Build steps (AWS console)

Use **us-east-1** for the whole project.

1. **KMS:** Create a symmetric key with alias `app-config-key`. Key administrators: your user. Key users: the Lambda role, which you can add after step 3.
2. **Secrets Manager:** Store a new secret named `app/config`. Choose the `app-config-key` KMS key, not the default. Add two keys, for example `api_base_url` and `feature_flag`.
3. **Lambda:** Create `config-reader`, runtime Python 3.12. Paste `lambda/handler.py` and deploy. Add environment variable `SECRET_ID = app/config`.
4. **Lambda permissions:** On the execution role, add:
   - `secretsmanager:GetSecretValue` on the `app/config` secret ARN only
   - `kms:Decrypt` on the `app-config-key` key ARN only
5. **Log retention:** Under **CloudWatch → Log groups → /aws/lambda/config-reader**, set retention to **7 days**. The default is never expire, which quietly costs money.
6. **Metric filter:** On the same log group, create a metric filter:
   - Filter pattern: `{ $.level = "ERROR" }`
   - Metric namespace `ConfigReader`, metric name `ConfigErrors`, value `1`
7. **SNS:** Create topic `config-alerts` with an email subscription, and confirm it from your inbox.
8. **Alarm:** Create an alarm on `ConfigReader / ConfigErrors`, statistic Sum, period 1 minute, threshold greater than or equal to 1. Action: notify `config-alerts`.

## Verification

```bash
# Good run: expect 200 and an INFO log line listing the secret's key names
aws lambda invoke --function-name config-reader --region us-east-1 out.json && cat out.json

# Bad run: temporarily change SECRET_ID to a missing secret, invoke, and expect a failure
```

**Checkpoints:**
- The log group shows one `INFO` line with `keys` and no secret values.
- After the bad run, the `ConfigErrors` metric goes above 0 and the alarm goes to **In alarm**. You get an email.
- Remove the bad `SECRET_ID` change and reinvoke to clear the alarm.
- In the secret's **Versions** view, the value is never shown in the logs.

## Teardown

1. Delete the CloudWatch alarm and the metric filter.
2. Delete the SNS topic and its subscription.
3. Delete the Lambda function, then its log group.
4. Delete the Secrets Manager secret. It has a 7-to-30-day recovery window, so schedule deletion with the shortest window.
5. Schedule the KMS key for deletion (7 days, the minimum). KMS keys can't be deleted immediately.

## Concepts practiced

- Encrypting data at rest with customer-managed KMS keys
- Storing and retrieving secrets without hard-coding them
- Least-privilege policies that name specific secret and key ARNs
- Structured logs, metric filters, and alarms in CloudWatch
