# Project 4: Containers on ECS Fargate behind an Application Load Balancer

A small Python web service packaged in a Docker image, pushed to ECR, and run on ECS Fargate (no servers to manage). An Application Load Balancer (ALB) spreads traffic across tasks in two Availability Zones and checks their health.

**Status:** Code and steps written. Not yet deployed to AWS.

## Architecture

```
Internet ──► ALB (public subnets, 2 AZs, HTTP :80)
                │  health check: GET /health
                ▼
        Target group (IP targets)
          ├── Fargate task (private subnet, AZ a)
          └── Fargate task (private subnet, AZ b)
                ▲
                │ pulls image
              ECR repo "static-app"
```

## Build steps (AWS console and terminal)

Use **us-east-1** for the whole project. Replace `ACCOUNT_ID` with your 12-digit account ID.

1. **Build and push the image** (needs Docker and the AWS CLI):
   ```bash
   aws ecr create-repository --repository-name static-app
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
   docker build -t static-app .
   docker tag static-app:latest ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/static-app:latest
   docker push ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/static-app:latest
   ```
2. **VPC:** Use the **VPC wizard** with 2 AZs, 2 public and 2 private subnets, and one NAT gateway. The NAT gateway costs money while it's running, so tear it down right after the test.
3. **Security groups:**
   - `alb-sg`: allow inbound TCP 80 from `0.0.0.0/0`.
   - `task-sg`: allow inbound TCP 8080 from `alb-sg` only.
4. **ECS:** Create cluster `static-cluster` with the **Fargate** capacity provider.
5. **Task definition:** Launch type Fargate, 0.25 vCPU and 0.5 GB memory. Container image is the ECR URI from step 1, container port `8080`. Task execution role: `ecsTaskExecutionRole` (the console creates it).
6. **ALB:** Create an internet-facing Application Load Balancer across both public subnets. Use the `alb-sg` security group.
7. **Target group:** Type **IP**, protocol HTTP on port 8080, health check path `/health`. Register no targets manually.
8. **Service:** In the cluster, create service `static-service` from the task definition. Desired tasks: 2. Put tasks in the **private** subnets with `task-sg`. Attach it to the target group from step 7.

## Verification

```bash
# Expect {"message": "hello from ECS Fargate", "task": "..."}
curl -s http://ALB_DNS_NAME/

# Expect {"status": "ok"}
curl -s http://ALB_DNS_NAME/health

# Run several times: the "task" value should change between the two tasks
for i in 1 2 3 4; do curl -s http://ALB_DNS_NAME/; echo; done
```

**Checkpoints:**
- Both tasks show **RUNNING** and the target group shows both targets **healthy**.
- Repeated requests return different `task` values, which shows the ALB is balancing.
- Stop one task from the console. ECS starts a replacement and the target group recovers.

## Teardown

1. Set the ECS service desired count to 0, then delete the service.
2. Delete the cluster.
3. Delete the ALB, then the target group.
4. Delete the NAT gateway, then release its Elastic IP.
5. Delete the VPC, which removes the subnets, route tables, and security groups.
6. Delete the ECR repository (and its images).

## Concepts practiced

- Container images and registries (Docker, ECR)
- Serverless containers (ECS on Fargate)
- Load balancing and health checks (ALB, target groups)
- Public and private subnets, NAT gateways, and layered security groups
