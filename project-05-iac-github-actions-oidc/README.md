# Project 5: Infrastructure as Code + GitHub Actions with OIDC (no stored AWS keys)

Terraform creates an IAM role that GitHub Actions can assume through OpenID Connect (OIDC). The trust policy only allows workflows on the `main` branch of this repo. The workflow then proves it can reach AWS, without any access keys stored in GitHub.

**Status:** Code and steps written. Not yet deployed to AWS.

**Note on tooling:** This is the one project that uses Terraform, because infrastructure as code is the point of the project. The other projects use the console.

## Architecture

```
GitHub Actions (main branch)
      │ requests OIDC token (id-token: write)
      ▼
token.actions.githubusercontent.com ──► AWS IAM OIDC provider
                                             │ trust policy checks aud + sub
                                             ▼
                                   IAM role "github-actions-aws-projects"
                                   (ReadOnlyAccess)
```

## Build steps

1. **Install Terraform** (1.6 or newer) and configure AWS CLI credentials for your account.
2. **Deploy the role:**
   ```bash
   cd project-05-iac-github-actions-oidc
   terraform init
   terraform plan
   terraform apply
   ```
   Copy the `role_arn` output.
3. **Set the GitHub variable:** In the repo, go to **Settings → Secrets and variables → Actions → Variables** and add `AWS_ROLE_ARN` with the role ARN. A variable is used here, not a secret, because a role ARN isn't sensitive.
4. **Run the workflow:** Push to `main`, or run **aws-check** from the **Actions** tab.

## Verification

**Checkpoints:**
- The `aws-check` run is green.
- The **Confirm identity** step prints the assumed-role ARN, which includes `github-actions-aws-projects`.
- Run the workflow from a branch other than `main`. It should fail at the assume-role step, because the trust policy's `sub` condition doesn't match. Seeing that failure confirms the restriction works.

## Teardown

1. Run `terraform destroy`.
2. Delete the `AWS_ROLE_ARN` variable in GitHub, if you don't plan to reuse it.

## Concepts practiced

- Declaring IAM, OIDC providers, and trust policies as code (Terraform)
- Federated identity: short-lived credentials instead of stored keys
- Scoping a trust policy by repo and branch with `sub` and `aud` conditions
