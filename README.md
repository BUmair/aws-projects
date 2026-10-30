# AWS Projects

Hands-on AWS projects built to learn the services behind the AWS Certified Solutions Architect – Associate and AWS Certified Cloud Practitioner exams. Each project has its own README covering architecture, build steps, verification, and teardown, so nothing is left running after the project ends.

## Projects

| # | Project | Services | Status |
|---|---------|----------|--------|
| 1 | [Static site on private S3 + CloudFront](project-01-static-site-s3-cloudfront/) | S3, CloudFront, OAC | Deployed, verified, torn down |
| 2 | [Serverless REST API](project-02-serverless-api/) | API Gateway, Lambda, DynamoDB, Cognito | Deployed, verified, torn down |

## Conventions

- Each project lives in its own folder with a README covering architecture, build steps, verification, teardown, and the concepts practiced.
- Projects are built in the AWS console unless noted. Project 5 uses Terraform because infrastructure as code is its focus.
- Every project ends with a teardown section so nothing keeps running and costing money.
