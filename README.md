# Astronomy Shop: E-commerce Microservices on AWS EKS

An online telescope shop made of **24 microservices** in 10+ languages. This
repo holds the **application code**. Every push builds Docker images, pushes
them to **Amazon ECR**, and updates the **[k8s-file](https://github.com/digitalwitchdemo/k8s-file)**
repo, which **Argo CD** deploys to the EKS cluster automatically.

```
 you push code ──► GitHub Actions ──► Amazon ECR ──► k8s-file repo ──► Argo CD ──► EKS
 (this repo)       builds 24 images   stores images   new image tag    syncs        running shop
```

## 1. What's in this repo

| Path | What it is |
|---|---|
| `src/<service>/` | One folder per microservice, each with its own `Dockerfile` |
| `src/shared/` | Code shared by the AI services (`agent`, `mcp`) |
| `src/flagd/` | Default feature flags (copied into the `flagd-ui` image) |
| `src/react-native-app/` | Mobile app (Android/iOS), **not** a container |
| `pb/demo.proto` | gRPC API definitions shared by the services |
| `telemetry-schema/` | Telemetry definitions used by `telemetry-docs` |
| `.env` | Version pins used during the image builds |
| `.github/workflows/ecr-build-push.yml` | The CI pipeline |

## 2. The services

| Group | Services |
|---|---|
| Entry | `frontend-proxy` (Envoy), `frontend` (Next.js) |
| Browsing | `product-catalog`, `recommendation`, `ad`, `image-provider` |
| Checkout | `checkout`, `cart`, `shipping`, `quote`, `currency`, `payment`, `email` |
| Orders (Kafka) | `kafka`, `accounting`, `fraud-detection` |
| AI assistant | `chatbot`, `agent`, `mcp` |
| Platform | `flagd-ui`, `load-generator`, `opamp-server`, `opensearch`, `telemetry-docs` |

Databases (PostgreSQL, Valkey) and monitoring (Jaeger, Prometheus, Grafana)
use public images, so they're only configured in `k8s-file`.

## 3. How the pipeline works

The workflow runs on every push to `main` that changes `src/`, `pb/` or `.env`.

| Job | What it does |
|---|---|
| **build-and-push** | Builds all 24 images **in parallel** and pushes each to ECR as `ecomerce/<service>`, tagged with the **run number** (the `#N` shown in Actions, e.g. `8`) and `latest` |
| **update-k8s-manifests** | Runs only if **all** images built. Writes the new tag into `k8s-file/kustomization.yaml` and pushes it |

Argo CD watches `k8s-file` and rolls out the new images within ~3 minutes.
No manual deploy step.

## 4. One-time setup

In this repo: **Settings → Secrets and variables → Actions**

| Type | Name | Value |
|---|---|---|
| Secret | `AWS_ROLE_ARN` | IAM role GitHub assumes through OIDC (needs ECR push + `ecr-public:GetAuthorizationToken`) |
| Secret | `K8S_REPO_TOKEN` | GitHub fine-grained token, **Contents: Read and write** on `k8s-file` only |
| Variable | `AWS_REGION` | Region of your ECR and EKS cluster, e.g. `us-west-1` |

> The images' region must match the region in `k8s-file/kustomization.yaml`,
> otherwise pods fail with `ImagePullBackOff`.

## 5. Make a change and deploy it

```bash
# 1. Get the code
git clone https://github.com/digitalwitchdemo/ecommerce-final-project.git
cd ecommerce-final-project

# 2. Change something, e.g. a page in src/frontend/
# 3. Commit and push
git add .
git commit -m "Change the home page title"
git push
```

Then follow it:

| Step | Where to look |
|---|---|
| Images building | GitHub → **Actions** → *Build and Push Images to ECR* |
| Images in ECR | AWS Console → **ECR** → `ecomerce/<service>`; the newest tag = the run number (`#N`) |
| Tag updated | `k8s-file` repo → new commit **"Deploy images from build #N"** |
| Deployed | Argo CD UI → app **astronomy-shop** = `Synced` / `Healthy` |
| Live | https://shop.digitalwitch.online |

**Rebuild without a code change:** Actions → *Build and Push Images to ECR* → **Run workflow**.

## 6. Common build errors

| Error | Cause | Fix |
|---|---|---|
| `429 Too Many Requests` | Registry rate limit on base images | Re-run the failed job |
| `Hash Sum mismatch` (apt) | Ubuntu mirror was syncing | Re-run the failed job |
| `NU1903 … vulnerability` | A .NET package has a security advisory | Upgrade the package in `src/<service>/Directory.Packages.props` |
| `update-k8s-manifests` skipped | At least one image failed | Fix that image; the deploy only runs when all 24 succeed |
| Push to `k8s-file` denied | `K8S_REPO_TOKEN` expired or missing | Create a new token and update the secret |

## 7. Mobile app

`src/react-native-app/` is an Android/iOS app, not deployed to Kubernetes.
Build the Android `.apk` with Docker:

```bash
cd src/react-native-app
docker build -f android.Dockerfile --platform=linux/amd64 --output=. .
```

Install `reactnativeapp.apk` on a phone or emulator. In the app's **Settings**
tab, set the server to `https://shop.digitalwitch.online`.

## License

Based on the [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo),
licensed under the Apache License 2.0 (see [LICENSE](LICENSE)).
