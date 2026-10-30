# Project 3: Event-Driven Pipeline (EventBridge + SQS + Lambda + DLQ + SNS)

Orders are published as events to EventBridge. A rule routes them to an SQS queue, a Lambda consumer processes them, and messages that keep failing move to a dead-letter queue (DLQ). An SNS email alert fires when anything reaches the DLQ.

**Status:** Code and steps written. Not yet deployed to AWS.

## Architecture

```
send_test_events.py
      │ put_events (source: app.orders, type: OrderPlaced)
      ▼
EventBridge default bus ──rule──► SQS queue "orders-queue"
                                      │ 3 failed receives
                                      ▼
                              SQS DLQ "orders-dlq" ──► CloudWatch alarm ──► SNS topic ──► email
                                      ▲
Lambda "order-consumer" ◄────────────┘ (event source mapping, partial batch failures)
```

## Why each service

- **EventBridge:** Decouples producers from consumers. The producer doesn't know who reads the event.
- **SQS:** Buffers work and retries it. Lambda reads at its own pace.
- **DLQ:** Holds messages that keep failing, so they can be inspected instead of lost.
- **SNS:** Sends the alert when the DLQ gets a message.

## Build steps (AWS console)

Use **us-east-1** for the whole project.

1. **SNS:** Create a standard topic `orders-alerts`. Create an email subscription and confirm it from your inbox.
2. **SQS (DLQ first):** Create a standard queue `orders-dlq`.
3. **SQS (main):** Create a standard queue `orders-queue`. Set **Visibility timeout** to 60 seconds. Under **Dead-letter queue**, choose `orders-dlq` with **Maximum receives** = 3.
4. **Lambda:** Create function `order-consumer`, runtime Python 3.12. Paste `consumer/handler.py` and deploy.
5. **Lambda trigger:** Add an SQS trigger for `orders-queue`. Set batch size to 5, and under **Additional settings** turn on **Report batch item failures**.
6. **Lambda permissions:** Give the execution role `sqs:ReceiveMessage`, `DeleteMessage`, and `GetQueueAttributes` on `orders-queue`. The console adds these when you create the trigger.
7. **EventBridge rule:** On the default bus, create rule `order-placed`. Event pattern:
   ```json
   {
     "source": ["app.orders"],
     "detail-type": ["OrderPlaced"]
   }
   ```
   Target: SQS queue `orders-queue`.
8. **Queue policy:** EventBridge needs permission to send to the queue. Let the console create the resource policy when you choose the target, then confirm it allows `events.amazonaws.com`.
9. **Alarm:** In CloudWatch, create an alarm on the `orders-dlq` metric `ApproximateNumberOfMessagesVisible`. Threshold: greater than or equal to 1. Action: notify `orders-alerts`.

## Verification

```bash
# Requires AWS CLI credentials for the account
python scripts/send_test_events.py
```

**Checkpoints:**
- `FailedEntryCount` in the output is `0`.
- Within a minute, the Lambda log group shows one `INFO` line for `ord-1001` and one `ERROR` line for `ord-1002`.
- Wait a few minutes. `ord-1002` is retried 3 times and then appears in `orders-dlq`. The CloudWatch alarm goes to ALARM and you get an email.
- Purge `orders-dlq` after the test, which also clears the alarm.

## Teardown

1. Delete the CloudWatch alarm.
2. Delete the EventBridge rule.
3. Delete the Lambda function and the SQS trigger.
4. Delete both SQS queues.
5. Delete the SNS topic and its subscription.
6. Delete the Lambda log group.

## Concepts practiced

- Event routing with EventBridge patterns
- Queue-based decoupling and retry behavior (SQS visibility timeout, max receives)
- Dead-letter queues and partial batch responses
- Alarm-to-notification chains (CloudWatch → SNS)
