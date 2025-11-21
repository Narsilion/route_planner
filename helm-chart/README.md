# Route Planner Helm Chart

This Helm chart packages the Route Planner application for deployment on Kubernetes clusters.

## Prerequisites

- Kubernetes 1.20+
- Helm 3.0+
- Docker image of route-planner available

## Installation

### Basic Installation

```bash
helm install route-planner ./helm-chart
```

### Installation with custom values

```bash
helm install route-planner ./helm-chart -f values-custom.yaml
```

### Using a specific namespace

```bash
helm install route-planner ./helm-chart -n route-planner --create-namespace
```

## Uninstallation

```bash
helm uninstall route-planner
```

## Configuration

The following table lists the configurable parameters and their default values:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `1` |
| `image.repository` | Image repository | `localhost:5000/route-planner` |
| `image.tag` | Image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `service.type` | Service type | `NodePort` |
| `service.port` | Service port | `80` |
| `service.nodePort` | NodePort number | `30080` |
| `containerPort` | Container port | `8080` |
| `autoscaling.enabled` | Enable autoscaling | `false` |
| `autoscaling.minReplicas` | Min replicas for autoscaling | `1` |
| `autoscaling.maxReplicas` | Max replicas for autoscaling | `100` |
| `resources` | CPU/Memory resources | `{}` |

## Usage Examples

### Deploy with custom replicas and image

```bash
helm install route-planner ./helm-chart \
  --set replicaCount=3 \
  --set image.tag=v1.0.0
```

### Deploy with LoadBalancer service

```bash
helm install route-planner ./helm-chart \
  --set service.type=LoadBalancer
```

### Deploy with resource limits

```bash
helm install route-planner ./helm-chart \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi \
  --set resources.requests.cpu=250m \
  --set resources.requests.memory=256Mi
```

### Deploy with autoscaling

```bash
helm install route-planner ./helm-chart \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10
```

## Accessing the Application

### For NodePort service:

```bash
# Get the NodePort
kubectl get svc route-planner -o jsonpath='{.spec.ports[0].nodePort}'

# For minikube
minikube service route-planner
```

### For LoadBalancer service:

```bash
kubectl get svc route-planner -w
```

## Verification

### Check if the deployment is running

```bash
kubectl get deployments
kubectl get pods
```

### View logs

```bash
kubectl logs deployment/route-planner
kubectl logs deployment/route-planner -f  # follow logs
```

### Check service endpoints

```bash
kubectl get svc route-planner
kubectl describe svc route-planner
```

## Upgrading

```bash
helm upgrade route-planner ./helm-chart
```

## Rollback

```bash
helm rollback route-planner
```

## Chart Structure

```
helm-chart/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration values
├── templates/
│   ├── deployment.yaml      # Kubernetes Deployment
│   ├── service.yaml         # Kubernetes Service
│   ├── serviceaccount.yaml  # Service Account
│   ├── _helpers.tpl         # Template helpers
│   └── hpa.yaml            # (Optional) Horizontal Pod Autoscaler
└── charts/              # Chart dependencies (if any)
```

## License

See LICENSE file for details.

