# 🚀 StreamBox — Complete AWS Deployment Guide

This guide walks you through deploying **StreamBox** on Amazon Web Services (AWS). Because StreamBox acts as an async HLS reverse proxy that handles chunked video playlists (`.m3u8`) and transport stream segments (`.ts`), it requires a reliable runtime with persistent HTTP connections.

---

## 📊 AWS Hosting Options at a Glance

| Service | Setup Difficulty | Estimated Cost | Scalability | Best For |
|---|---|---|---|---|
| **Option 1: AWS App Runner** *(Recommended)* | ⭐ Very Easy (3 clicks) | ~$5 - $15 / month (Pay-as-you-go) | Fully Auto-scales (0 to N) | **Fastest, zero server maintenance, free SSL** |
| **Option 2: AWS Lightsail / EC2** | ⭐⭐ Easy (Docker) | $3.50 - $5.00 / month (or Free Tier) | Fixed instance capacity | **Cheapest & best for student/college projects** |
| **Option 3: AWS ECS (Fargate)** | ⭐⭐⭐ Intermediate | Based on vCPU & Memory | High enterprise scaling | **Production systems with custom VPCs** |
| **Option 4: AWS Elastic Beanstalk** | ⭐⭐ Easy | EC2 + ALB costs | Standard PaaS scaling | **Classic AWS PaaS users** |

---

## 🌟 Option 1: AWS App Runner (Fastest & Easiest — Recommended)

AWS App Runner is a fully managed service that takes your source code or Docker container directly from GitHub and deploys it with automatic HTTPS/TLS, load balancing, and auto-scaling.

### Step 1: Push your Code to GitHub
Ensure all new deployment files are committed and pushed:
```bash
git add .
git commit -m "Configure AWS deployment with Docker and App Runner"
git push origin main
```

### Step 2: Create App Runner Service
1. Open the [AWS App Runner Console](https://console.aws.amazon.com/apprunner).
2. Click **Create service**.
3. Under **Source**:
   - Choose **Source code repository**.
   - Click **Add new** to link your GitHub account and authorize AWS.
   - Select your repository: `saurabh-yadav-ggu/cricket_live_stream`.
   - Select branch: `main`.
4. Under **Deployment trigger**:
   - Choose **Automatic** *(App Runner will automatically rebuild and redeploy whenever you push new commits)*.
5. Click **Next**.

### Step 3: Configure Build & Runtime
App Runner can automatically use the included [`apprunner.yaml`](apprunner.yaml) file:
- Select **Use a configuration file** (it will read `apprunner.yaml` automatically).
- *Alternatively, if you select "Configure all settings here":*
  - **Runtime**: `Python 3`
  - **Build command**: `pip install -r requirements.txt`
  - **Start command**: `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2`
  - **Port**: `8000`

### Step 4: Health Check Settings
In **Service configuration**:
- **CPU & Memory**: `1 vCPU` and `2 GB` (optimal for live video proxying).
- Expand **Health check**:
  - **Protocol**: `HTTP`
  - **Path**: `/health`
  - **Interval**: `20` seconds
  - **Timeout**: `5` seconds
  - **Healthy threshold**: `1`
  - **Unhealthy threshold**: `3`

### Step 5: Review & Deploy
Click **Create & Deploy**. Within 3 to 4 minutes, AWS will provision your service and provide a public URL:
```text
https://xxxxxxxxxx.us-east-1.awsapprunner.com
```
Visit this URL in your browser to view your live player!

---

## 💰 Option 2: AWS Lightsail or EC2 with Docker (Cheapest — $3.50/mo or Free Tier)

For student projects, personal portfolios, or high-bandwidth video streaming, an **AWS Lightsail** virtual machine ($3.50/month with 1 TB free outbound transfer) or an **AWS EC2 Free Tier (`t2.micro` or `t3.micro`)** is the most cost-effective solution.

### Step 1: Launch an Ubuntu Instance
1. Go to **AWS EC2 Console** or **Amazon Lightsail Console**.
2. Create an instance:
   - **OS**: `Ubuntu 22.04 LTS` or `Ubuntu 24.04 LTS`
   - **Instance Type**: `t2.micro` / `t3.micro` (EC2) or **$3.50/mo 512MB/1GB** (Lightsail).
   - **SSH Key Pair**: Download your `.pem` key pair (e.g. `streambox-key.pem`).

### Step 2: Open Security Group / Firewall Ports
Ensure the following inbound rules are allowed:
- `Port 22` (SSH) — For remote access
- `Port 80` (HTTP) — For web traffic & Let's Encrypt
- `Port 443` (HTTPS) — For secure SSL traffic
- `Port 8000` (Custom TCP) — Direct FastAPI access (optional if using Nginx)

### Step 3: Connect via SSH
On Windows PowerShell or Terminal:
```bash
ssh -i "path/to/streambox-key.pem" ubuntu@<YOUR-INSTANCE-PUBLIC-IP>
```

### Step 4: Run the 1-Click Automated Setup Script
Run these 3 commands inside your EC2/Lightsail terminal:
```bash
git clone https://github.com/saurabh-yadav-ggu/cricket_live_stream.git
cd cricket_live_stream
chmod +x deploy-ec2.sh
./deploy-ec2.sh
```

**What this script automatically does:**
1. Installs official Docker Engine and Docker Compose.
2. Sets up Nginx reverse proxy using the optimized [`nginx.conf`](nginx.conf) with video chunk streaming buffers disabled.
3. Builds and launches the StreamBox container via `docker compose up -d`.
4. Tests the `/health` endpoint to ensure the application is running smoothly.

### Step 5: (Optional) Add a Custom Domain & Free SSL with Let's Encrypt
If you point a domain (e.g. `stream.yourdomain.com`) to your instance's public IP:
```bash
sudo apt update
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d stream.yourdomain.com
```
Certbot will automatically install a free SSL certificate and renew it periodically.

---

## 🏢 Option 3: AWS ECS (Elastic Container Service) with Fargate

For production and enterprise setups where you need automated container scaling across availability zones without managing servers:

### Step 1: Create an ECR Repository
```bash
aws ecr create-repository --repository-name streambox --region us-east-1
```

### Step 2: Build, Tag, and Push Docker Image
```bash
# Log in Docker to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build Docker image
docker build -t streambox:latest .

# Tag image for ECR
docker tag streambox:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/streambox:latest

# Push image
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/streambox:latest
```

### Step 3: Register Task Definition
Replace `<AWS_ACCOUNT_ID>` and `<AWS_REGION>` inside [`ecs-task-definition.json`](ecs-task-definition.json), then run:
```bash
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json
```

### Step 4: Create ECS Cluster and Service
1. Go to **AWS ECS Console** -> **Clusters** -> **Create Cluster** (Networking only / Fargate).
2. Inside cluster, click **Create Service**:
   - Launch type: `FARGATE`.
   - Task definition: `streambox-task`.
   - Desired tasks: `1` or `2`.
   - Application Load Balancer: Route port 80/443 to target group pointing to container port `8000` with health check path `/health`.

---

## ☁️ Option 4: AWS CloudFormation 1-Click Deployment

If you want to use infrastructure-as-code:
1. Open the [AWS CloudFormation Console](https://console.aws.amazon.com/cloudformation).
2. Click **Create stack (with new resources)**.
3. Choose **Upload a template file** and select [`aws-cloudformation-apprunner.yaml`](aws-cloudformation-apprunner.yaml).
4. Enter your parameters (GitHub repository URL and App Runner GitHub Connection ARN).
5. Click **Submit**. CloudFormation will provision the entire App Runner service automatically.

---

## 🔄 Automated CI/CD Pipeline (GitHub Actions)

A fully automated CI/CD pipeline is provided in [`.github/workflows/deploy.yml`](.github/workflows/deploy.yml).

### Pipeline Flow:
```mermaid
flowchart LR
    A[git push to main] --> B[CI: Lint & Flake8]
    B --> C[CI: Pytest Suite]
    C --> D[CI: Docker Buildx]
    D --> E[CI: Container Smoke Test]
    E --> F{Target Configured?}
    F -->|App Runner ARN| G[AWS App Runner Auto-Deploy]
    F -->|ECR Repo| H[Push to ECR & Update ECS]
    F -->|EC2 Host/SSH| I[SSH to EC2 & docker compose up]
```

### GitHub Secrets Setup:
Go to your GitHub repo -> **Settings** -> **Secrets and variables** -> **Actions** -> **New repository secret**:

#### For AWS App Runner:
| Secret Name | Description | Example |
|---|---|---|
| `AWS_ACCESS_KEY_ID` | IAM User Access Key with App Runner permissions | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM User Secret Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS Region where App Runner service is hosted | `us-east-1` or `ap-south-1` |
| `AWS_APP_RUNNER_ARN` | The ARN of your App Runner service | `arn:aws:apprunner:us-east-1:...` |

*(Note: If you enabled **Automatic Deployment** in App Runner's console, App Runner will also rebuild on GitHub push automatically without needing secrets!)*

#### For AWS EC2 / Lightsail (SSH):
| Secret Name | Description | Example |
|---|---|---|
| `EC2_HOST` | Public IP or DNS of your EC2/Lightsail instance | `13.233.xxx.xxx` |
| `EC2_SSH_KEY` | Private SSH Key (`.pem`) content | `-----BEGIN RSA PRIVATE KEY-----...` |
| `EC2_USER` | SSH Username (optional, defaults to `ubuntu`) | `ubuntu` |

---

## 🧪 Verification & Post-Deployment Checklist

Once deployed, verify that all core endpoints are responsive:

1. **Health Check**:
   ```bash
   curl -I https://<YOUR-APP-URL>/health
   # Expected: HTTP/1.1 200 OK
   # Response: {"status": "healthy", "service": "streambox", ...}
   ```
2. **Stream Status**:
   ```bash
   curl -s https://<YOUR-APP-URL>/api/stream/status
   ```
3. **Channel Catalog**:
   ```bash
   curl -s https://<YOUR-APP-URL>/api/channels
   ```
4. **Web UI**:
   Open `https://<YOUR-APP-URL>` in your browser. The Video.js player should initialize and load live cricket/sports HLS feeds with quality selector controls.

---

## 🔧 Environment Variables Reference

| Variable | Default | Description |
|---|---|---|
| `PORT` | `8000` | The port the FastAPI server listens on inside the container. |
| `HOST` | `0.0.0.0` | Bind IP address (`0.0.0.0` required for containers/AWS). |
| `PYTHONUNBUFFERED` | `1` | Forces real-time log output to CloudWatch / Docker logs. |

---

## ❓ Frequently Asked Questions & Troubleshooting

### Why is AWS Lambda not recommended for this application?
AWS Lambda has a 6 MB response payload limit for buffered responses, execution timeouts (maximum 15 minutes), and does not support long-lived HTTP keep-alive connections needed to reverse-proxy live HLS video streams efficiently. AWS App Runner, ECS Fargate, or EC2/Lightsail provide seamless streaming with zero buffer timeouts.

### How does CORS proxying work on AWS?
When a user plays a video, the browser sends requests to your AWS URL: `/api/stream/proxy?url=<CDN_STREAM_URL>`. StreamBox forwards the request with clean browser headers, rewrites relative `.ts` segments and child `.m3u8` playlists, and streams them directly to Video.js with `Access-Control-Allow-Origin: *`.

### How do I check container logs on AWS?
- **AWS App Runner**: Go to App Runner Console -> Service -> **Logs** -> **Application logs**.
- **AWS EC2 / Lightsail**: Run `docker compose logs -f --tail=100` on the server.
- **AWS ECS**: Go to **CloudWatch Logs** -> `/ecs/streambox`.
