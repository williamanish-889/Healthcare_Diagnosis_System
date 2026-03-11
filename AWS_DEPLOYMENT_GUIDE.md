# Euron Healthcare — AWS Deployment via GitHub Actions

Everything is done through **two web UIs** — the AWS Console and GitHub.
You never need to run Docker commands locally. GitHub Actions builds and pushes images for you.

---

## HOW IT WORKS

```
You push code to GitHub
        ↓
GitHub Actions automatically:
  1. Builds Docker image
  2. Pushes to AWS ECR
  3. Triggers ECS redeployment
        ↓
AWS ECS pulls the new image and restarts the container
        ↓
Your Browser  →  ALB (Load Balancer)  →  ECS Fargate Containers
                      │
                      ├── /*       → Frontend (Next.js, port 3000)
                      └── /api/*   → Backend  (FastAPI, port 8000)
```

| Resource | Count | Purpose |
|----------|-------|---------|
| ECR Repositories | 2 | Store Docker images |
| VPC + 2 Subnets | 1 | Networking |
| Security Groups | 3 | Firewall rules |
| ALB + Target Groups | 1 + 2 | Route traffic |
| ECS Cluster | 1 | Run containers |
| Task Definitions | 2 | Container blueprints |
| ECS Services | 2 | Running containers |
| CloudWatch Log Groups | 2 | Container logs |
| IAM Role | 1 | ECS permissions |
| GitHub Actions Workflows | 2 | CI/CD pipelines |

**Estimated cost: ~$44/month** (ap-south-1 region, GitHub Actions free tier covers the CI/CD)

---

## STEP 1 — PUSH YOUR CODE TO GITHUB

> Create a GitHub repository and push this project to it.

### 1a. Create the repository

1. Go to **https://github.com/new**
2. Repository name: **`eurondoctorshelp`** (or any name you prefer)
3. Visibility: **Private** (recommended) or Public
4. **Do NOT** check "Add a README file" (you already have code)
5. Click **"Create repository"**

### 1b. Push your code

Open PowerShell in your project folder (`d:\downloads\eurondoctorshelp`) and run:

```powershell
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/eurondoctorshelp.git
git push -u origin main
```

> Replace `YOUR_USERNAME` with your actual GitHub username.

**Verify:** Refresh your GitHub repo page — you should see all your files.

---

## STEP 2 — CREATE ECR REPOSITORIES (AWS Console)

> Store your Docker images in AWS (like Docker Hub but private).

1. Open **https://console.aws.amazon.com/ecr**
2. Make sure your region is set (top-right dropdown) — use **ap-south-1 (Mumbai)** or your preferred region
3. Click **"Get Started"** or **"Create repository"**

### Repository 1 — Backend

4. Visibility: **Private**
5. Repository name: **`euron-backend`**
6. Image tag mutability: **Mutable**
7. Scan on push: **Enabled**
8. Click **"Create repository"**

### Repository 2 — Frontend

9. Click **"Create repository"** again
10. Repository name: **`euron-frontend`**
11. Same settings as above
12. Click **"Create repository"**

You now see both repos listed. Each has a **URI** like:
```
123456789012.dkr.ecr.ap-south-1.amazonaws.com/euron-backend
```

**Write down your Account ID** (the 12-digit number in the URI). You'll need it.

---

## STEP 3 — ADD AWS SECRETS TO GITHUB

> GitHub Actions needs your AWS credentials to push images to ECR and update ECS. This is all done through the GitHub UI.

### 3a. Create an AWS Access Key (if you don't have one)

1. In AWS Console → click your username (top right) → **Security credentials**
2. Scroll to **Access keys** → **Create access key**
3. Use case: choose **Third-party service**
4. Check the acknowledgment → **Create access key**
5. **Copy both keys** (Access Key ID and Secret Access Key) — you won't see the secret again

### 3b. Add secrets to GitHub

1. Go to your GitHub repository page
2. Click **Settings** tab (top bar)
3. Left sidebar → **Secrets and variables** → **Actions**
4. Click **"New repository secret"** and add each of these one by one:

| Secret Name | Value |
|-------------|-------|
| **`AWS_ACCESS_KEY_ID`** | Your AWS Access Key ID |
| **`AWS_SECRET_ACCESS_KEY`** | Your AWS Secret Access Key |
| **`NEXT_PUBLIC_API_URL`** | `http://placeholder.com` (you'll update this later with your real ALB DNS) |

**How to add each secret:**
1. Click **"New repository secret"**
2. Name: paste the secret name from the table above
3. Secret: paste the value
4. Click **"Add secret"**

After adding all 3, your Secrets page should show:

```
AWS_ACCESS_KEY_ID        Updated just now
AWS_SECRET_ACCESS_KEY    Updated just now
NEXT_PUBLIC_API_URL      Updated just now
```

---

## STEP 4 — CREATE A VPC (AWS Console)

> A Virtual Private Cloud gives your containers a network to live in.

1. Open **https://console.aws.amazon.com/vpc**
2. Click **"Create VPC"**
3. Select **"VPC and more"** (this auto-creates subnets, route tables, gateway)
4. Fill in:
   - Name tag auto-generation: **`euron`**
   - IPv4 CIDR block: **`10.0.0.0/16`**
   - Number of Availability Zones: **2**
   - Number of public subnets: **2**
   - Number of private subnets: **0**
   - NAT gateways: **None**
   - VPC endpoints: **None**
5. Click **"Create VPC"**
6. Wait for it to finish (green checkmarks)

**Write down:**
- VPC ID: `vpc-xxxxxxxxx`
- Public Subnet 1 ID: `subnet-aaaaaaa`
- Public Subnet 2 ID: `subnet-bbbbbbb`

(You can find these under **VPC** → **Subnets**, filter by your VPC)

---

## STEP 5 — CREATE SECURITY GROUPS (AWS Console)

> Firewall rules that control who can talk to what.

Go to **VPC** → **Security Groups** (left sidebar) → **Create security group**

### Security Group 1: ALB (public facing)

- Name: **`euron-alb-sg`**
- Description: `Allow HTTP from internet`
- VPC: select **`euron-vpc`**
- **Inbound rules** → Add rule:
  - Type: **HTTP** | Port: **80** | Source: **Anywhere-IPv4** (`0.0.0.0/0`)
  - Type: **HTTPS** | Port: **443** | Source: **Anywhere-IPv4** (`0.0.0.0/0`)
- Click **"Create security group"**

### Security Group 2: Backend

- Name: **`euron-backend-sg`**
- Description: `Allow traffic from ALB to backend`
- VPC: **`euron-vpc`**
- **Inbound rules** → Add rule:
  - Type: **Custom TCP** | Port: **8000** | Source: **Custom** → type `euron-alb-sg` and select it
- Click **"Create security group"**

### Security Group 3: Frontend

- Name: **`euron-frontend-sg`**
- Description: `Allow traffic from ALB to frontend`
- VPC: **`euron-vpc`**
- **Inbound rules** → Add rule:
  - Type: **Custom TCP** | Port: **3000** | Source: **Custom** → type `euron-alb-sg` and select it
- Click **"Create security group"**

---

## STEP 6 — CREATE TARGET GROUPS (AWS Console)

> Tell the load balancer where to send traffic and how to health-check.

Go to **EC2** → **Target Groups** (left sidebar under Load Balancing) → **Create target group**

### Target Group 1: Backend

- Target type: **IP addresses**
- Name: **`euron-backend-tg`**
- Protocol: **HTTP** | Port: **8000**
- VPC: **`euron-vpc`**
- Health check protocol: **HTTP**
- Health check path: **`/api/health`**
- Click **"Next"**
- **Don't register any targets** → just click **"Create target group"**

### Target Group 2: Frontend

- Target type: **IP addresses**
- Name: **`euron-frontend-tg`**
- Protocol: **HTTP** | Port: **3000**
- VPC: **`euron-vpc`**
- Health check path: **`/`**
- Click **"Next"** → **"Create target group"**

---

## STEP 7 — CREATE APPLICATION LOAD BALANCER (AWS Console)

> The single entry point for your app. Routes traffic to frontend and backend.

Go to **EC2** → **Load Balancers** → **Create Load Balancer** → choose **Application Load Balancer**

1. Name: **`euron-alb`**
2. Scheme: **Internet-facing**
3. IP type: **IPv4**
4. **Network mapping:**
   - VPC: **`euron-vpc`**
   - Select **both** Availability Zones and their public subnets
5. **Security group:** remove the default, select **`euron-alb-sg`**
6. **Listener:**
   - Protocol: **HTTP** | Port: **80**
   - Default action: Forward to → **`euron-frontend-tg`**
7. Click **"Create load balancer"**

### 7b. Add Backend Routing Rule

After the ALB is created:

1. Click on **`euron-alb`** → go to **Listeners and rules** tab
2. Click on the **HTTP:80** listener row → click **Manage rules** → **Add rules**
3. Click **"Add rule"**

**Rule 1:**
- Name: **`backend-api`**
- Click **"Next"**
- **Add condition** → **Path** → Value: **`/api/*`** → Confirm
- Click **"Next"**
- **Action:** Forward to → **`euron-backend-tg`**
- Click **"Next"**
- Priority: **10**
- Click **"Create"**

4. Click **"Add rule"** again

**Rule 2:**
- Name: **`backend-docs`**
- Condition: **Path** → Value: **`/docs*`**
- Action: Forward to → **`euron-backend-tg`**
- Priority: **20**
- Click **"Create"**

### 7c. Copy the ALB DNS

Go to your ALB → copy the **DNS name** from the Description section:
```
euron-alb-XXXXXXXXX.ap-south-1.elb.amazonaws.com
```

**This is your app URL.** Save it — you'll need it in Step 11.

---

## STEP 8 — CREATE CLOUDWATCH LOG GROUPS (AWS Console)

> Where your container logs go.

1. Open **https://console.aws.amazon.com/cloudwatch**
2. Left sidebar → **Logs** → **Log groups** → **Create log group**
3. Name: **`/ecs/euron-backend`** → Retention: **1 month** → Create
4. Create another: **`/ecs/euron-frontend`** → Retention: **1 month** → Create

---

## STEP 9 — CREATE IAM ROLE FOR ECS (AWS Console)

> ECS needs permission to pull images from ECR and write logs.

1. Open **https://console.aws.amazon.com/iam**
2. Left sidebar → **Roles** → **Create role**
3. Trusted entity: **AWS service**
4. Use case: dropdown select **Elastic Container Service** → then select **Elastic Container Service Task**
5. Click **"Next"**
6. Search and check: **`AmazonECSTaskExecutionRolePolicy`**
7. Click **"Next"**
8. Role name: **`ecsTaskExecutionRole`**
9. Click **"Create role"**

**Note:** If this role already exists, skip this step — AWS often creates it automatically.

---

## STEP 10 — CREATE ECS CLUSTER & SERVICES (AWS Console)

### 10a. Create Cluster

1. Open **https://console.aws.amazon.com/ecs**
2. Click **"Create cluster"**
3. Cluster name: **`euron-prod-cluster`**
4. Infrastructure: make sure **AWS Fargate (serverless)** is checked
5. Click **"Create"**

### 10b. Create Task Definition — Backend

Go to **ECS** → **Task definitions** → **Create new task definition**

1. Task definition family: **`euron-backend`**
2. Launch type: **AWS Fargate**
3. Operating system: **Linux/X86_64**
4. CPU: **0.5 vCPU** | Memory: **1 GB**
5. Task role: **`ecsTaskRole`** (or leave blank if you didn't create it)
6. Task execution role: **`ecsTaskExecutionRole`**

**Container details:**
7. Container name: **`euron-backend`**
8. Image URI: **`YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/euron-backend:latest`**
9. Port mappings: Container port **`8000`** | Protocol **TCP**

**Environment variables** (scroll down to the Environment section):
10. Add environment variable:
    - Key: **`MONGODB_URI`** | Value: **your MongoDB Atlas connection string**
11. Add another:
    - Key: **`OPENAI_API_KEY`** | Value: **your OpenAI API key**
12. Add another:
    - Key: **`JWT_SECRET`** | Value: **any random strong string**

**Health check** (expand the section):
13. Command: **`CMD-SHELL,curl -f http://localhost:8000/api/health || exit 1`**
14. Interval: **30** | Timeout: **10** | Retries: **3** | Start period: **60**

**Log collection** (expand Logging section):
15. Log driver: **`awslogs`**
16. awslogs-group: **`/ecs/euron-backend`**
17. awslogs-region: **`ap-south-1`**
18. awslogs-stream-prefix: **`ecs`**

19. Click **"Create"**

### 10c. Create Task Definition — Frontend

1. Click **"Create new task definition"** again
2. Family: **`euron-frontend`**
3. Launch type: **AWS Fargate**
4. CPU: **0.25 vCPU** | Memory: **0.5 GB**
5. Task execution role: **`ecsTaskExecutionRole`**

**Container details:**
6. Name: **`euron-frontend`**
7. Image URI: **`YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/euron-frontend:latest`**
8. Port: **`3000`** | Protocol **TCP**

**Health check:**
9. Command: **`CMD-SHELL,curl -f http://localhost:3000/ || exit 1`**
10. Interval: **30** | Timeout: **10** | Retries: **3** | Start period: **30**

**Log collection:**
11. awslogs-group: **`/ecs/euron-frontend`**
12. awslogs-region: **`ap-south-1`**
13. awslogs-stream-prefix: **`ecs`**

14. Click **"Create"**

### 10d. Create Service — Backend

Go to **ECS** → **Clusters** → click **`euron-prod-cluster`** → **Services** tab → **Create**

1. **Compute options:** Launch type → **FARGATE**
2. **Deployment configuration:**
   - Application type: **Service**
   - Task definition family: **`euron-backend`** | Revision: **LATEST**
   - Service name: **`euron-backend-service`**
   - Desired tasks: **1**
3. **Networking:**
   - VPC: **`euron-vpc`**
   - Subnets: select **both** public subnets
   - Security group: remove default, select **`euron-backend-sg`**
   - Public IP: **Turned ON**
4. **Load balancing:**
   - Load balancer type: **Application Load Balancer**
   - Choose: **Use an existing load balancer** → select **`euron-alb`**
   - Choose: **Use an existing listener** → select **80:HTTP**
   - Choose: **Use an existing target group** → select **`euron-backend-tg`**
5. Click **"Create"**

### 10e. Create Service — Frontend

1. Go back to the cluster → **Create** another service
2. Task definition: **`euron-frontend`** | Revision: **LATEST**
3. Service name: **`euron-frontend-service`**
4. Desired tasks: **1**
5. Networking:
   - VPC: **`euron-vpc`**
   - Subnets: **both** public subnets
   - Security group: **`euron-frontend-sg`**
   - Public IP: **Turned ON**
6. Load balancing:
   - ALB: **`euron-alb`**
   - Listener: **80:HTTP**
   - Target group: **`euron-frontend-tg`**
7. Click **"Create"**

---

## STEP 11 — TRIGGER FIRST DEPLOYMENT FROM GITHUB

> Now use GitHub Actions to build and push your Docker images. No Docker needed on your machine!

### 11a. Deploy Backend (from GitHub UI)

1. Go to your GitHub repository page
2. Click the **"Actions"** tab
3. In the left sidebar you'll see **"Deploy Backend to ECR"**
4. Click on it
5. Click the **"Run workflow"** dropdown button (right side)
6. Branch: **main**
7. Click **"Run workflow"**

You'll see a new workflow run appear. Click on it to watch the progress:
- **Checkout code** — pulls your repo
- **Configure AWS credentials** — uses your secrets
- **Login to Amazon ECR** — authenticates with AWS
- **Build, tag, and push** — builds the Docker image and pushes it to ECR
- **Force new ECS deployment** — tells ECS to pull the new image

Wait for all steps to show green checkmarks (3-5 minutes).

### 11b. Deploy Frontend (from GitHub UI)

1. Still on the **Actions** tab
2. Click **"Deploy Frontend to ECR"** in the left sidebar
3. Click **"Run workflow"** dropdown
4. Branch: **main**
5. **api_url**: enter your ALB DNS from Step 7c in this format:
   ```
   http://euron-alb-XXXXXXXXX.ap-south-1.elb.amazonaws.com
   ```
6. Click **"Run workflow"**

Wait for all steps to show green checkmarks.

### 11c. Update the saved API URL secret

Now that you know your real ALB DNS, update the GitHub secret so future automatic deployments use the correct URL:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click the pencil icon next to **`NEXT_PUBLIC_API_URL`**
3. Update the value to: `http://euron-alb-XXXXXXXXX.ap-south-1.elb.amazonaws.com` (your real ALB DNS)
4. Click **"Update secret"**

---

## STEP 12 — WAIT & VERIFY SERVICES ARE RUNNING

1. Go to **AWS Console** → **ECS** → **Clusters** → **`euron-prod-cluster`** → **Services** tab
2. Click on each service → go to the **Tasks** tab
3. Wait until the task **Last status** changes to **RUNNING** (2-5 minutes)

### If a task keeps failing:
- Click on the task → scroll to **Logs** tab → read the error
- Common fixes:
  - **MongoDB connection error** → Go to MongoDB Atlas → **Network Access** → **Add IP Address** → **Allow Access from Anywhere** (`0.0.0.0/0`)
  - **Image pull error** → Check ECR has images (go to ECR → click the repo → you should see the `latest` tag)
  - **Health check failing** → Check security groups allow ALB → container on the correct port

---

## STEP 13 — SEED DATABASE & TEST

Open your browser or terminal:

### Seed 1000 patient records:

Open this URL in your browser:
```
http://YOUR_ALB_DNS/docs
```

This opens the Swagger API docs. Find **POST /api/data/seed** → click **Try it out** → click **Execute**.

### Verify everything works:

Open in browser:
```
http://YOUR_ALB_DNS           ← Dashboard with charts
http://YOUR_ALB_DNS/patients  ← 1000 patient records
http://YOUR_ALB_DNS/diagnosis ← AI diagnosis tool
http://YOUR_ALB_DNS/docs      ← API documentation
```

---

## YOU'RE LIVE!

Your Euron Healthcare system is now deployed on AWS, powered by GitHub Actions CI/CD.

---

## HOW FUTURE DEPLOYMENTS WORK

After the initial setup, deploying new changes is effortless:

### Option A: Automatic (push to main)

Just push code to the `main` branch. GitHub Actions will automatically:
1. Detect which service changed (backend or frontend)
2. Build a new Docker image
3. Push it to ECR
4. Trigger ECS to pull the new image

```powershell
git add .
git commit -m "your change description"
git push origin main
```

Then go to **GitHub → Actions** tab to watch the deployment.

### Option B: Manual trigger (from GitHub UI)

1. Go to **GitHub → Actions** tab
2. Select the workflow (Backend or Frontend) from the left sidebar
3. Click **"Run workflow"** → **"Run workflow"**

This is useful when you want to redeploy without code changes (e.g., after updating an environment variable in ECS).

### Watching deployment progress

1. **GitHub Actions** tab → click the running workflow → watch each step
2. **AWS ECS Console** → Cluster → Service → Tasks tab → wait for new task to reach **RUNNING**

---

## CHEAT SHEET — DAILY OPERATIONS

### View logs

Go to **CloudWatch** → **Log groups** → click `/ecs/euron-backend` or `/ecs/euron-frontend` → click the latest log stream

### Stop services (save money)

Go to ECS → Cluster → select service → **"Update service"** → set **Desired tasks** to **0** → **"Update"**

### Start services again

Same as above but set **Desired tasks** to **1**

### Scale up

Set **Desired tasks** to **2** or more — ECS and ALB handle the rest automatically

### View GitHub Actions run history

Go to your repo → **Actions** tab → see all past runs, their status, and logs

---

## DELETE EVERYTHING (when done)

Do these in order to avoid charges:

1. **ECS** → Cluster → select each service → Update → set Desired tasks to **0** → wait → **Delete service**
2. **ECS** → Delete the **cluster**
3. **EC2** → Load Balancers → select **`euron-alb`** → **Actions** → **Delete**
4. **EC2** → Target Groups → delete both target groups
5. **VPC** → select **`euron-vpc`** → **Actions** → **Delete VPC** (this deletes subnets, route tables, etc.)
6. **ECR** → select each repository → **Delete**
7. **CloudWatch** → Log groups → delete both
8. **VPC** → Security Groups → delete the 3 custom ones (ALB, backend, frontend)
9. **GitHub** → Settings → Secrets → delete AWS secrets (good security practice)
