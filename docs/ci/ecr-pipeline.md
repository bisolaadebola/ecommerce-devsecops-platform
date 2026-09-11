# ECR Build & Push Pipeline — One-Time AWS Setup

`.github/workflows/ecr-build-push.yml` builds Docker images for all 24
buildable services in this repo and pushes them to AWS ECR. It authenticates
using GitHub OIDC — no long-lived AWS access keys are stored in GitHub.

Before the workflow can run successfully, someone with IAM admin access in
the target AWS account needs to complete the one-time setup below.

## 1. Create the GitHub OIDC identity provider (skip if it already exists)

One provider is shared by every repo in the account, so check first whether
it already exists (IAM → Identity providers).

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

Console equivalent: **IAM → Identity providers → Add provider → OpenID
Connect**, Provider URL `https://token.actions.githubusercontent.com`,
Audience `sts.amazonaws.com`.

## 2. Create the IAM role GitHub will assume

Trust policy — replace `<ACCOUNT_ID>` and `<GITHUB_ORG>`. The `sub` condition
scopes this role to pushes/dispatches on this repo's `main` branch only;
widen it to `repo:<GITHUB_ORG>/opentelemetry-demo:*` if you also want
`workflow_dispatch` runs triggered from other branches to work.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::<ACCOUNT_ID>:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:<GITHUB_ORG>/opentelemetry-demo:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

## 3. Attach a permissions policy for ECR

Replace `<REGION>`, `<ACCOUNT_ID>`, and `<ECR_REPO_PREFIX>` (the prefix must
match the `ECR_REPO_PREFIX` variable you set in step 4 — `otel-demo` if you
don't set one).

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": ["ecr:GetAuthorizationToken"],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:CreateRepository",
        "ecr:DescribeRepositories",
        "ecr:BatchCheckLayerAvailability",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload",
        "ecr:PutImage",
        "ecr:BatchGetImage",
        "ecr:GetDownloadUrlForLayer"
      ],
      "Resource": "arn:aws:ecr:<REGION>:<ACCOUNT_ID>:repository/<ECR_REPO_PREFIX>/*"
    }
  ]
}
```

`ecr:GetAuthorizationToken` must use `Resource: "*"` — it doesn't support
resource-level scoping. Everything else is scoped to the repository-name
prefix this workflow uses.

## 4. Set the required GitHub repository variables

**Settings → Secrets and variables → Actions → Variables tab**, add:

| Variable | Example value | Required |
|---|---|---|
| `AWS_ROLE_ARN` | `arn:aws:iam::123456789012:role/github-actions-ecr-push` | Yes |
| `AWS_REGION` | `us-east-1` | Yes |
| `ECR_REPO_PREFIX` | `otel-demo` | No — defaults to `otel-demo` if unset |

## 5. Test it

Go to **Actions → "Build and Push Images to ECR" → Run workflow**
(`workflow_dispatch`). Once it completes, confirm images appear in the ECR
console under `<prefix>/<service-name>` repositories (e.g. `otel-demo/cart`),
each tagged `latest` and with an 8-character git SHA.

After that, every push to `main` touching `src/**`, `pb/**`, `.env`, or the
workflow file itself will rebuild and push automatically.
