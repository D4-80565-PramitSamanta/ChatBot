# Kubernetes Deployment Guide

This directory contains a Helm chart for deploying the FastAPI Chatbot to Kubernetes.

## Prerequisites

- Kubernetes cluster (1.20+)
- Helm 3.x
- kubectl configured to access your cluster
- Docker image of the chatbot application

## Building the Docker Image

```bash
# Build the image
docker build -t chatbot:latest .

# Tag for your registry
docker tag chatbot:latest <your-registry>/chatbot:latest

# Push to registry
docker push <your-registry>/chatbot:latest
```

## Installation Steps

### 1. Create Kubernetes Secret for API Key

```bash
kubectl create secret generic chatbot-secrets \
  --from-literal=GEMINI_API_KEY=your-actual-api-key \
  -n default
```

### 2. Create Namespace (Optional)

```bash
kubectl create namespace chatbot
```

### 3. Deploy with Helm

#### Using default values:
```bash
helm install chatbot ./helm/chatbot \
  --set image.repository=<your-registry>/chatbot \
  --set image.tag=latest
```

#### Using a values file:
```bash
helm install chatbot ./helm/chatbot -f helm/chatbot/values-prod.yaml
```

#### For a specific namespace:
```bash
helm install chatbot ./helm/chatbot \
  --namespace chatbot \
  --set image.repository=<your-registry>/chatbot
```

### 4. Verify Deployment

```bash
# Check deployment status
kubectl get deployments
kubectl describe deployment chatbot

# Check pods
kubectl get pods -l app.kubernetes.io/name=chatbot
kubectl logs -l app.kubernetes.io/name=chatbot -f

# Check service
kubectl get svc chatbot
```

## Configuration

### Custom Values

Create a `values-prod.yaml` for production:

```yaml
replicaCount: 3

image:
  repository: your-registry/chatbot
  tag: v1.0.0

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

ingress:
  enabled: true
  hosts:
    - host: chatbot.example.com
      paths:
        - path: /
          pathType: Prefix

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
```

### Available Options

- `replicaCount`: Number of pod replicas (default: 2)
- `image.repository`: Docker image repository
- `image.tag`: Docker image tag (default: latest)
- `resources`: CPU/Memory limits and requests
- `autoscaling`: Enable HPA with min/max replicas
- `ingress`: Enable and configure ingress
- `data.volumeSize`: PVC size for data (default: 1Gi)

## Common Commands

### Update Deployment
```bash
helm upgrade chatbot ./helm/chatbot --values values-prod.yaml
```

### Rollback
```bash
helm rollback chatbot 1
```

### View Helm Chart
```bash
helm get values chatbot
helm get manifest chatbot
```

### Delete Deployment
```bash
helm uninstall chatbot
```

### Port Forward (Development)
```bash
kubectl port-forward svc/chatbot 8080:8080
```

## Monitoring

### Check Logs
```bash
# Recent logs
kubectl logs -l app.kubernetes.io/name=chatbot

# Follow logs
kubectl logs -l app.kubernetes.io/name=chatbot -f

# Specific pod logs
kubectl logs chatbot-deployment-xxxxx
```

### Check Pod Status
```bash
kubectl get pods -l app.kubernetes.io/name=chatbot -o wide
kubectl describe pod chatbot-deployment-xxxxx
```

### Check Health
```bash
# Port forward to access health endpoint
kubectl port-forward svc/chatbot 8080:8080

# In another terminal
curl http://localhost:8080/api/health
```

## Ingress Setup (Production)

For production, enable ingress with TLS:

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: api.zentrumhub.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: chatbot-tls
      hosts:
        - api.zentrumhub.com
```

## Scaling

### Manual Scaling
```bash
kubectl scale deployment chatbot --replicas=5
```

### Auto Scaling
Already configured via HPA in the Helm chart. Check status:

```bash
kubectl get hpa
kubectl describe hpa chatbot
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Image pull errors
```bash
kubectl get events
# Check image repository and credentials
```

### Health check failures
```bash
kubectl port-forward svc/chatbot 8080:8080
curl http://localhost:8080/api/health
```

## Notes

- The chart uses ClusterIP service by default
- Liveness and readiness probes check `/api/health` endpoint
- Non-root user (UID 1000) for security
- Pod anti-affinity preferred for high availability
- HPA configured for 80% CPU/Memory utilization
