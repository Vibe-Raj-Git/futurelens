# Deploying FutureLens with Docker

## Files in this setup

| File | Purpose |
|---|---|
| `Dockerfile` | Multi-stage build: Node builds the frontend, Python runs the backend and serves both |
| `docker/start.sh` | Container entry point; starts uvicorn on the port the host assigns |
| `.dockerignore` | Keeps the image small; excludes secrets, backups, dependencies |
| `docker-compose.yml` | Optional; runs the container locally with one command |

## Build the image

From the project root:

    docker build -t futurelens:latest .

## Run locally

    docker run --rm -p 8000:8000 --env-file .env futurelens:latest

Open http://localhost:8000

## Run with compose

    docker compose up --build

## Deploy to GCP Cloud Run

### 1. Set variables

    $PROJECT_ID = "your-gcp-project-id"
    $REGION = "asia-south1"
    $IMAGE = "$REGION-docker.pkg.dev/$PROJECT_ID/futurelens/app:latest"

### 2. Authenticate and enable services

    gcloud auth login
    gcloud config set project $PROJECT_ID
    gcloud services enable artifactregistry.googleapis.com run.googleapis.com

### 3. Create the Artifact Registry repository (one time)

    gcloud artifacts repositories create futurelens `
        --repository-format=docker `
        --location=$REGION

### 4. Configure Docker authentication

    gcloud auth configure-docker "$REGION-docker.pkg.dev"

### 5. Build and push

    docker build -t $IMAGE .
    docker push $IMAGE

### 6. Deploy

    gcloud run deploy futurelens `
        --image $IMAGE `
        --region $REGION `
        --platform managed `
        --allow-unauthenticated `
        --port 8000 `
        --memory 512Mi `
        --cpu 1 `
        --timeout 60 `
        --set-env-vars "GEMINI_API_KEY=$env:GEMINI_API_KEY"

### 7. Get the URL

    gcloud run services describe futurelens --region $REGION --format "value(status.url)"

## Secrets

Never bake `GEMINI_API_KEY` into the image. Pass it at runtime:

- Locally: `--env-file .env`
- Cloud Run: `--set-env-vars` or Google Secret Manager

The `.dockerignore` excludes `.env` so it cannot be accidentally copied
into an image layer.

## What the container serves

- `/` - the built Vite frontend (static files)
- `/health` - health check
- `/api/locations/search` - location autocomplete
- `/api/forecast` - the forecast endpoint
- `/api/chat` - the conversational endpoint

Both the frontend and backend are served from the same origin, so no
CORS configuration is required in production.
