# Helm Chart Conversion Guide

## Overview

This Helm chart converts the existing Kubernetes YAML files into a templated, reusable Helm chart for the Route Planner application.

## What Was Converted

### Original Files
- `k8s/deployment.yaml` → `helm-chart/templates/deployment.yaml`
- `k8s/service.yaml` → `helm-chart/templates/service.yaml`

### New Files Created
- `helm-chart/templates/_helpers.tpl` - Helper templates for common labels and naming
- `helm-chart/templates/serviceaccount.yaml` - Service Account configuration
- `helm-chart/templates/hpa.yaml` - Horizontal Pod Autoscaler (optional)
- `helm-chart/values.yaml` - Default configuration values
- `helm-chart/values-dev.yaml` - Development environment values
- `helm-chart/values-prod.yaml` - Production environment values
- `helm-chart/Chart.yaml` - Chart metadata

## Key Features

### 1. **Parameterized Configuration**
All hardcoded values have been replaced with configurable parameters:
- Image repository and tag
- Replica count
- Service type and ports
- Container port
- Resource limits and requests
- Autoscaling settings
- Liveness and readiness probes

### 2. **Helper Templates**
Common naming and labeling conventions are centralized in `_helpers.tpl`:
- Consistent naming across resources
- Standard Kubernetes labels (helm.sh/chart, app.kubernetes.io/*)
- Service account naming

### 3. **Environment-Specific Values**
Different configurations for different environments:
- **values.yaml** - Default/base values
- **values-dev.yaml** - Development environment (low resources, NodePort)
- **values-prod.yaml** - Production environment (high availability, LoadBalancer)

### 4. **Optional Components**
Components can be enabled/disabled via configuration:
- Horizontal Pod Autoscaler (HPA) - disabled by default
- Service Account - created by default
- Security contexts - available but not enforced by default

## Deployment Instructions

### Prerequisites
```bash
# Install Helm (if not already installed)
brew install helm  # macOS
# or use your package manager
```

### Basic Deployment to Minikube

```bash
# 1. Navigate to the helm chart directory
cd /Users/darkcreation/Documents/PycharmProjects/route_planner/helm-chart

# 2. Build and push your Docker image to minikube
eval $(minikube docker-env)
docker build -t localhost:5000/route-planner:latest ..
docker push localhost:5000/route-planner:latest
eval $(minikube docker-env -u)

# 3. Deploy using the Helm chart
helm install route-planner .

# Or with specific values
helm install route-planner . -f values-dev.yaml
```

### Verify Deployment

```bash
# Check Helm releases
helm list

# Check Kubernetes resources
kubectl get deployments
kubectl get services
kubectl get pods

# View logs
kubectl logs -f deployment/route-planner

# Access the application (for minikube)
minikube service route-planner
```

### Upgrade Deployment

```bash
# Make changes to values.yaml or code, then:
helm upgrade route-planner .

# Or upgrade with new values
helm upgrade route-planner . -f values-dev.yaml
```

### Rollback Deployment

```bash
# See deployment history
helm history route-planner

# Rollback to previous release
helm rollback route-planner 1
```

### Uninstall Deployment

```bash
helm uninstall route-planner
```

## Common Use Cases

### 1. Update Image Tag

```bash
helm upgrade route-planner . --set image.tag=v1.0.0
```

### 2. Scale Replicas

```bash
helm upgrade route-planner . --set replicaCount=5
```

### 3. Change Service Type to LoadBalancer

```bash
helm upgrade route-planner . --set service.type=LoadBalancer
```

### 4. Set Resource Limits

```bash
helm upgrade route-planner . \
  --set resources.limits.cpu=500m \
  --set resources.limits.memory=512Mi \
  --set resources.requests.cpu=250m \
  --set resources.requests.memory=256Mi
```

### 5. Enable Autoscaling

```bash
helm upgrade route-planner . \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=2 \
  --set autoscaling.maxReplicas=10 \
  --set autoscaling.targetCPUUtilizationPercentage=80
```

### 6. Deploy to Different Namespace

```bash
helm install route-planner . \
  -n production \
  --create-namespace \
  -f values-prod.yaml
```

## Template Preview

To preview the generated Kubernetes manifests:

```bash
# Preview with default values
helm template route-planner .

# Preview with specific values file
helm template route-planner . -f values-prod.yaml

# Preview with specific overrides
helm template route-planner . --set replicaCount=3
```

## Troubleshooting

### Chart Validation

```bash
# Lint the chart for errors
helm lint .

# Validate template syntax
helm template route-planner . > /tmp/manifest.yaml
kubectl apply -f /tmp/manifest.yaml --dry-run=client
```

### Check Values

```bash
# See effective values being used
helm get values route-planner

# See all values including defaults
helm get values route-planner --all
```

### Debug Rendering

```bash
# See detailed template rendering
helm template route-planner . --debug
```

## Next Steps

1. **Add Additional Templates**: Consider adding:
   - Ingress configuration
   - ConfigMaps for application configuration
   - Secrets for sensitive data
   - Network Policies
   - Pod Disruption Budgets

2. **CI/CD Integration**: 
   - Add chart to version control
   - Set up automated testing with `chart-testing`
   - Configure automated deployment pipelines

3. **Package Chart**:
   ```bash
   helm package .
   ```

4. **Host Chart Repository**: 
   - Use GitHub Pages, Chartmuseum, or other chart repositories
   - Make it accessible for team/organization

## References

- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

