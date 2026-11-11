# 🎓 Project 16 — Troubleshooting: 502 Bad Gateway

> **Docker & Jenkins College Assignment**
> Demonstrates how an incorrect Nginx reverse proxy configuration causes a
> 502 Bad Gateway error, how to diagnose it using Docker commands, and how to fix it.

---

## 📋 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Project Structure](#-project-structure)
3. [Prerequisites](#-prerequisites)
4. [Quick Start](#-quick-start)
5. [How It Works](#-how-it-works)
6. [Troubleshooting Demonstration](#-troubleshooting-demonstration)
7. [Useful Docker Commands](#-useful-docker-commands)
8. [Testing Checklist](#-testing-checklist)
9. [Cleanup](#-cleanup)
10. [Key Concepts Explained](#-key-concepts-explained)

---

## 🏗 Architecture Overview

```
                    ┌──────────────────────────────────────────────┐
                    │           Docker Compose Network             │
                    │              (app-network)                   │
                    │                                              │
 User Browser ────▶│  ┌─────────┐    ┌──────────┐   ┌─────────┐  │
 http://localhost   │  │  Nginx  │───▶│ Frontend │   │   DB    │  │
        :80         │  │ (proxy) │    │ (React)  │   │(Postgres│  │
                    │  │  :80    │    │  :3000   │   │  :5432) │  │
                    │  │         │    └──────────┘   └────▲────┘  │
                    │  │         │    ┌──────────┐        │       │
                    │  │         │───▶│ Backend  │────────┘       │
                    │  │         │    │(FastAPI) │                │
                    │  └─────────┘    │  :8000   │                │
                    │                 └──────────┘                │
                    └──────────────────────────────────────────────┘

 Exposed to host:  Only port 80 (Nginx)
 Internal only:    Ports 3000, 8000, 5432
```

### Request Flow

1. **User** opens `http://localhost` in a browser.
2. **Nginx** receives the request on port 80.
3. For `/` requests → Nginx forwards to the **React frontend** on port 3000.
4. For `/api/*` requests → Nginx forwards to the **FastAPI backend** on port 8000.
5. **FastAPI** queries **PostgreSQL** on port 5432 and returns data.
6. The response travels back through Nginx to the user's browser.

---

## 📂 Project Structure

```
AWS-PROJECT/
├── frontend/                   # React application
│   ├── Dockerfile              # Multi-stage build (build + serve)
│   ├── package.json            # Node.js dependencies
│   ├── public/
│   │   └── index.html          # HTML template
│   └── src/
│       ├── index.js            # React entry point
│       ├── index.css           # Global styles
│       ├── App.js              # Main component (form + table + health)
│       └── App.css             # Component styles
│
├── backend/                    # FastAPI application
│   ├── Dockerfile              # Python 3.11 slim image
│   ├── requirements.txt        # Python dependencies
│   └── app/
│       ├── __init__.py         # Package marker
│       ├── main.py             # API routes and startup logic
│       ├── database.py         # SQLAlchemy connection setup
│       ├── models.py           # ORM model (Student table)
│       └── schemas.py          # Pydantic validation schemas
│
├── nginx/                      # Nginx reverse proxy
│   ├── Dockerfile              # Nginx Alpine image
│   ├── nginx.conf              # ✅ Correct proxy config
│   ├── nginx-broken.conf       # ❌ Broken config (for demo)
│   └── 502.html                # Custom 502 error page
│
├── docker-compose.yml          # Orchestrates all 4 services
├── .env.example                # Template for environment variables
├── .env                        # Actual environment variables (gitignored)
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

---

## ✅ Prerequisites

Make sure you have these installed:

| Tool           | Minimum Version | Check Command            |
|----------------|-----------------|--------------------------|
| Docker         | 20.10+          | `docker --version`       |
| Docker Compose | 2.0+ (V2)       | `docker compose version` |
| Git            | 2.30+           | `git --version`          |

---

## 🚀 Quick Start

### Step 1 — Clone and Configure

```bash
# Clone the repository (or navigate to the project folder)
cd AWS-PROJECT

# Create the .env file from the template
cp .env.example .env

# (Optional) Edit .env to change the database credentials
```

### Step 2 — Build and Start

```bash
# Build all Docker images and start containers in detached mode
docker compose up --build -d
```

This command:
- Builds the React frontend (multi-stage: npm build → serve)
- Builds the FastAPI backend (Python 3.11)
- Pulls PostgreSQL 15 and Nginx 1.25 images
- Creates the `app-network` bridge network
- Creates the `postgres_data` volume
- Starts all four containers

### Step 3 — Verify Everything Works

```bash
# Check all containers are running
docker ps

# Expected output: 4 containers (nginx-proxy, react-frontend, fastapi-backend, postgres-db)
```

| URL                            | What You Should See          |
|--------------------------------|------------------------------|
| http://localhost                | React frontend (Student Records UI) |
| http://localhost/api/health     | JSON health check response   |
| http://localhost/api/docs       | FastAPI Swagger documentation |

### Step 4 — Test the Application

1. Open http://localhost in your browser.
2. Click **"Check Health"** — should show ✅ status.
3. Fill in the **Add New Student** form and click **"Add Student"**.
4. Verify the student appears in the **Student Records** table.
5. Try deleting a student.

---

## 🔧 Troubleshooting Demonstration

This is the core of Project 16. Follow these steps to intentionally break the
application, diagnose the issue, and fix it.

### Phase 1 — Confirm Everything Works

```bash
# Make sure all containers are running
docker compose up --build -d

# Verify health
curl http://localhost/api/health
# Expected: {"status":"healthy","service":"student-records-api","database":"connected","version":"1.0.0"}

# Open the frontend
# Visit http://localhost in your browser — should load the React app
```

### Phase 2 — Break It (Introduce the 502 Error)

```bash
# Copy the BROKEN Nginx config into the running container
docker cp nginx/nginx-broken.conf nginx-proxy:/etc/nginx/conf.d/default.conf

# Reload Nginx to apply the broken config
docker exec nginx-proxy nginx -s reload
```

> **Why wrong ports, not wrong hostnames?**
> Nginx resolves upstream hostnames at config-load time. If a hostname is
> invalid (e.g. `webserver` when no such service exists), `nginx -s reload`
> is **rejected** and Nginx keeps its previous working config — so you'd
> never see a 502. Using valid service names with wrong ports lets the reload
> succeed, but every proxied request gets "Connection refused" → reliable 502.

Now try:
```bash
curl http://localhost
# Result: 502 Bad Gateway ❌

curl http://localhost/api/health
# Result: 502 Bad Gateway ❌
```

**Open http://localhost in your browser → you'll see the custom 502 error page.**

### Phase 3 — Investigate the Problem

Use these Docker commands to diagnose the issue:

#### 1. Check running containers

```bash
docker ps
```

You'll see all four containers are running. So the issue is NOT that a
container is down — it's a configuration problem.

#### 2. Check Nginx error logs

```bash
docker compose logs nginx
# or
docker logs nginx-proxy
```

Look for lines like:
```
[error] ... connect() failed (111: Connection refused) while connecting to upstream ... upstream: "http://frontend:9999/..."
[error] ... connect() failed (111: Connection refused) while connecting to upstream ... upstream: "http://backend:9999/..."
```

This tells us:
- Port `9999` on `frontend` is not reachable (should be `3000`)
- Port `9999` on `backend` is not reachable (should be `8000`)

#### 3. Inspect the Nginx configuration

```bash
docker exec nginx-proxy cat /etc/nginx/conf.d/default.conf
```

You'll see the broken config:
```nginx
upstream frontend_server {
    server frontend:9999;    # ❌ Wrong! Should be port 3000
}
upstream backend_server {
    server backend:9999;      # ❌ Wrong! Should be port 8000
}
```

#### 4. Verify service names and correct ports on the Docker network

```bash
# List all containers and their names
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Inspect the Docker network to see what names are available
docker network inspect aws-project_app-network
```

You'll see that the network has services named `frontend`, `backend`, `db`,
and `nginx`. The names are correct — the ports are wrong.

#### 5. Test internal connectivity

```bash
# From inside the Nginx container, test the CORRECT ports — these work
docker exec nginx-proxy wget -qO- http://frontend:3000 2>&1 | head -5
docker exec nginx-proxy wget -qO- http://backend:8000/api/health 2>&1

# Test the WRONG ports used in the broken config — these fail
docker exec nginx-proxy wget -qO- http://frontend:9999 2>&1
docker exec nginx-proxy wget -qO- http://backend:9999 2>&1
```

#### 6. (Bonus) Demonstrate invalid hostname separately

```bash
# Show what happens with a completely wrong hostname.
# This resolves nothing — Docker DNS returns no result.
docker exec nginx-proxy wget -qO- http://webserver:3000 2>&1
# Output: "bad address 'webserver:3000'" — host does not exist on the network
```

### Phase 4 — Fix the Problem

```bash
# Copy the CORRECT Nginx config into the container
docker cp nginx/nginx.conf nginx-proxy:/etc/nginx/conf.d/default.conf

# Reload Nginx (no need to restart the container)
docker exec nginx-proxy nginx -s reload
```

### Phase 5 — Verify the Fix

```bash
# Test the API
curl http://localhost/api/health
# Expected: {"status":"healthy",...} ✅

# Test the frontend
curl -s http://localhost | head -5
# Expected: HTML content from React app ✅
```

Open http://localhost in your browser — the app is working again! 🎉

---

## 📎 Useful Docker Commands

### Container Management

```bash
# Start all services
docker compose up --build -d

# Stop all services (keep volumes)
docker compose down

# Stop and delete everything including data
docker compose down -v

# Restart a specific service
docker compose restart nginx

# View running containers
docker ps
```

### Logs and Debugging

```bash
# View all logs
docker compose logs

# View logs for a specific service (follow mode)
docker compose logs -f nginx

# View last 50 lines of backend logs
docker logs --tail 50 fastapi-backend

# Open a shell inside a container
docker exec -it nginx-proxy sh
docker exec -it fastapi-backend bash
docker exec -it postgres-db psql -U student_user -d student_db
```

### Network and Inspection

```bash
# List Docker networks
docker network ls

# Inspect the project network
docker network inspect aws-project_app-network

# Check container health status
docker inspect --format='{{.State.Health.Status}}' fastapi-backend

# View container resource usage
docker stats
```

### Image Management

```bash
# List project images
docker images | grep aws-project

# Rebuild without cache (useful if Dockerfile changed)
docker compose build --no-cache

# Remove unused images
docker image prune
```

---

## ✅ Testing Checklist

Use this checklist to verify your project works correctly:

### Infrastructure

- [ ] `docker compose up --build -d` completes without errors
- [ ] `docker ps` shows 4 running containers
- [ ] All health checks pass (`docker inspect --format='{{.State.Health.Status}}' <container>`)
- [ ] PostgreSQL data persists after `docker compose down` and `docker compose up -d`
- [ ] Only port 80 is exposed on the host (verify with `docker ps`)

### Frontend

- [ ] http://localhost loads the React UI
- [ ] Page has a header, health check section, form, and student list
- [ ] Responsive design works on mobile viewport

### Backend API

- [ ] `GET  /api/health` returns `{"status":"healthy","database":"connected",...}`
- [ ] `POST /api/students` creates a new student record
- [ ] `GET  /api/students` returns the list of students
- [ ] `GET  /api/students/{id}` returns a single student
- [ ] `DELETE /api/students/{id}` removes a student
- [ ] Duplicate email returns 400 error
- [ ] `/api/docs` shows Swagger UI

### Database

- [ ] Student records persist after container restart
- [ ] Database credentials come from environment variables
- [ ] Database is not accessible from host (no port mapping)

### Troubleshooting Demo

- [ ] Broken config (`nginx-broken.conf`) causes 502 on both `/` and `/api/`
- [ ] `docker logs nginx-proxy` shows "Connection refused" on wrong ports
- [ ] `docker exec nginx-proxy cat /etc/nginx/conf.d/default.conf` reveals the wrong ports
- [ ] Internal connectivity test confirms correct ports work, wrong ports fail
- [ ] Fixing the config and running `nginx -s reload` restores functionality
- [ ] No container restart needed — just Nginx reload

---

## 🧹 Cleanup

```bash
# Stop containers and remove the network
docker compose down

# Stop containers, remove network, AND delete database volume
docker compose down -v

# Also remove built images
docker compose down -v --rmi all

# Remove any dangling images
docker image prune -f
```

---

## 📘 Key Concepts Explained

### What is a 502 Bad Gateway?

A **502 Bad Gateway** error means the server acting as a gateway or proxy
(Nginx in our case) received an invalid response from an upstream server.
Common causes:
- The upstream server is not running.
- The proxy is configured with the wrong hostname or port.
- A firewall is blocking the connection.
- The upstream server is overloaded.

### How Does Docker Compose Networking Work?

When you run `docker compose up`, Docker creates a **bridge network** for
your project. Each service gets a DNS entry matching its **service name**
in `docker-compose.yml`. So:
- `db` resolves to the PostgreSQL container's IP
- `backend` resolves to the FastAPI container's IP
- `frontend` resolves to the React container's IP

This is why using the wrong service name (like `webserver` instead of
`frontend`) causes a DNS resolution failure and a 502 error.

### What is an Nginx Reverse Proxy?

A **reverse proxy** sits in front of your application servers and forwards
client requests to the appropriate backend. Benefits:
- **Single entry point** — users only see port 80.
- **Security** — backend services are hidden from the internet.
- **Routing** — different URL paths go to different services.
- **SSL termination** — HTTPS can be handled at the proxy level.

### Why Keep Ports Private?

By not mapping backend or database ports to the host, we ensure:
- No accidental exposure of database credentials.
- No direct access to internal APIs that bypass the proxy.
- A more realistic production-like setup.

### What Does `nginx -s reload` Do?

It tells Nginx to gracefully reload its configuration without dropping
existing connections. This is much faster than restarting the entire
container and avoids downtime.

---

## 👤 Author

**Student Name:** _(Your Name Here)_
**Course:** _(Your Course Here)_
**Date:** November 2026

---

## 📄 License

This project is for educational purposes as part of a Docker & Jenkins
college assignment (Project 16).
