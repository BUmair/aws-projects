# Project 2: Serverless REST API (API Gateway + Lambda + DynamoDB + Cognito)

A REST API for a simple items list. API Gateway receives requests, a Lambda function runs the logic, DynamoDB stores the data, and Cognito protects the write routes.

**Status:** Code and steps written. Not yet deployed to AWS.

## Architecture

```
Client ──(JWT for POST/DELETE)──► API Gateway (HTTP API)
                                      │  JWT authorizer (Cognito user pool)
                                      ▼
                                 Lambda (Python 3.12)
                                      │
                                      ▼
                                 DynamoDB table "items" (partition key: id)
```

## Routes

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/items` | Public | List all items |
| GET | `/items/{id}` | Public | Get one item |
| POST | `/items` | Cognito JWT | Create an item |
| DELETE | `/items/{id}` | Cognito JWT | Delete an item |

## Build steps (AWS console)

Use **us-east-1** for the whole project.

1. **DynamoDB:** Create table `items`, partition key `id` (String). Use on-demand capacity.
2. **Cognito:** Create a user pool with email sign-in. Create an app client without a client secret. Create one test user.
3. **Lambda:** Create function `items-api`, runtime **Python 3.12**. Paste `lambda/handler.py` into the code editor and deploy. Under **Configuration → Environment variables**, add `TABLE_NAME = items`.
4. **Lambda permissions:** On the execution role, attach a policy that allows `dynamodb:Scan`, `GetItem`, `PutItem`, and `DeleteItem` on the `items` table ARN only.
5. **API Gateway:** Create an **HTTP API**. Add the four routes above, with the Lambda as the integration for all of them.
6. **Authorizer:** Create a JWT authorizer with the Cognito user pool's issuer URL and the app client ID as the audience. Attach it to the POST and DELETE routes only.
7. **Deploy:** Create the `$default` stage with auto-deploy on. Copy the invoke URL.

## Verification

Replace `API_URL` with your invoke URL and `TOKEN` with an ID token from the Cognito test user (sign in through the hosted UI or `aws cognito-idp initiate-auth`).

```bash
# Public: should return []
curl -s API_URL/items

# Protected: without a token, expect 401
curl -s -o /dev/null -w "%{http_code}\n" -X POST API_URL/items -H "Content-Type: application/json" -d '{"name":"test"}'

# Protected: with a token, expect 201 and an id
curl -s -X POST API_URL/items -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" -d '{"name":"test"}'
```

**Checkpoints:**
- The unauthenticated POST returns `401`.
- The authenticated POST returns `201` and the item appears in DynamoDB's **Explore items** view.
- The Lambda's CloudWatch log group shows one invocation per request.

## Teardown

1. Delete the API Gateway HTTP API.
2. Delete the Lambda function and its execution role.
3. Delete the Cognito user pool.
4. Delete the DynamoDB table.
5. Confirm the CloudWatch log group `/aws/lambda/items-api` is deleted or set to a short retention.

## Concepts practiced

- Serverless compute and event-driven invocation (Lambda)
- Managed NoSQL with a partition key (DynamoDB)
- JWT authorization with a managed identity provider (Cognito + API Gateway)
- Least-privilege IAM for a single table
