# Before & After: YAML to Helm Conversion

## Original vs. Templated Comparison

### Original Kubernetes YAML Files

#### k8s/deployment.yaml (BEFORE)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: route-planner
  labels:
    app: route-planner
spec:
  replicas: 1                          # ← HARDCODED
  selector:
    matchLabels:
      app: route-planner
  template:
    metadata:
      labels:
        app: route-planner
    spec:
      containers:
        - name: route-planner
          image: localhost:5000/route-planner:latest  # ← HARDCODED
          ports:
            - containerPort: 80        # ← HARDCODED
```

#### k8s/service.yaml (BEFORE)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: route-planner
spec:
  type: NodePort
  selector:
    app: route-planner
  ports:
    - name: http
      port: 80
      targetPort: 80
      nodePort: 30080
```

### New Helm Chart Templates

#### templates/deployment.yaml (AFTER)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "route-planner.fullname" . }}  # ← DYNAMIC
  labels:
    {{- include "route-planner.labels" . | nindent 4 }}  # ← REUSABLE LABELS
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}            # ← PARAMETERIZED
  {{- end }}
  selector:
    matchLabels:
      {{- include "route-planner.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      {{- with .Values.podAnnotations }}
      annotations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      labels:
        {{- include "route-planner.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "route-planner.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"  # ← PARAMETERIZED
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: {{ .Values.containerPort }}    # ← PARAMETERIZED
          protocol: TCP
        {{- if .Values.livenessProbe }}
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 12 }}
        {{- end }}
        {{- if .Values.readinessProbe }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 12 }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
        {{- with .Values.volumeMounts }}
        volumeMounts:
          {{- toYaml . | nindent 12 }}
        {{- end }}
      {{- with .Values.volumes }}
      volumes:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

#### templates/service.yaml (AFTER)
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "route-planner.fullname" . }}  # ← DYNAMIC
  labels:
    {{- include "route-planner.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}                 # ← PARAMETERIZED
  ports:
    - port: {{ .Values.service.port }}            # ← PARAMETERIZED
      targetPort: http
      protocol: TCP
      name: http
      {{- if and (eq .Values.service.type "NodePort") .Values.service.nodePort }}
      nodePort: {{ .Values.service.nodePort }}    # ← PARAMETERIZED
      {{- end }}
  selector:
    {{- include "route-planner.selectorLabels" . | nindent 4 }}
```

## Benefits of the Conversion

| Aspect | Before | After |
|--------|--------|-------|
| **Reusability** | Need separate YAML per environment | Single chart, multiple value files |
| **Configuration** | Edit YAML files manually | Use `--set` flags or values files |
| **Consistency** | Labels may be inconsistent | Standardized via helpers |
| **Version Control** | Hard to track what changed | Clear separation of chart and values |
| **Scaling** | Modify replicas manually | `--set replicaCount=N` |
| **Image Updates** | Edit deployment file | `--set image.tag=v1.0.0` |
| **Rollback** | Manual process | `helm rollback` command |
| **Multiple Environments** | Multiple copies of files | One chart, different values |
| **Documentation** | None built-in | Included with chart |
| **Validation** | Manual kubectl check | `helm lint` command |

## Usage Comparison

### Scenario: Deploy with 3 replicas

**Before (Manual YAML Editing):**
```bash
# Edit deployment.yaml, change replicas: 1 to replicas: 3
vim k8s/deployment.yaml
kubectl apply -f k8s/deployment.yaml
```

**After (Helm):**
```bash
helm install route-planner ./helm-chart --set replicaCount=3
# or
helm upgrade route-planner ./helm-chart --set replicaCount=3
```

### Scenario: Switch to LoadBalancer service

**Before (Manual YAML Editing):**
```bash
# Edit service.yaml, change type: NodePort to type: LoadBalancer
vim k8s/service.yaml
kubectl apply -f k8s/service.yaml
```

**After (Helm):**
```bash
helm upgrade route-planner ./helm-chart --set service.type=LoadBalancer
```

### Scenario: Update Docker image tag

**Before (Manual YAML Editing):**
```bash
# Edit deployment.yaml, update image tag
vim k8s/deployment.yaml
kubectl apply -f k8s/
```

**After (Helm):**
```bash
helm upgrade route-planner ./helm-chart --set image.tag=v1.2.3
```

## Generated Manifest Example

When you run `helm template route-planner ./helm-chart`, you get:

```yaml
---
# Source: route-planner/templates/serviceaccount.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: route-planner
  labels:
    helm.sh/chart: route-planner-0.1.0
    app.kubernetes.io/name: route-planner
    app.kubernetes.io/instance: route-planner
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/managed-by: Helm
---
# Source: route-planner/templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: route-planner
  labels:
    helm.sh/chart: route-planner-0.1.0
    app.kubernetes.io/name: route-planner
    app.kubernetes.io/instance: route-planner
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/managed-by: Helm
spec:
  type: NodePort
  ports:
    - port: 80
      targetPort: http
      protocol: TCP
      name: http
      nodePort: 30080
  selector:
    app.kubernetes.io/name: route-planner
    app.kubernetes.io/instance: route-planner
---
# Source: route-planner/templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: route-planner
  labels:
    helm.sh/chart: route-planner-0.1.0
    app.kubernetes.io/name: route-planner
    app.kubernetes.io/instance: route-planner
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/managed-by: Helm
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: route-planner
      app.kubernetes.io/instance: route-planner
  template:
    metadata:
      labels:
        app.kubernetes.io/name: route-planner
        app.kubernetes.io/instance: route-planner
    spec:
      serviceAccountName: route-planner
      containers:
      - name: route-planner
        image: "localhost:5000/route-planner:latest"
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
        livenessProbe:
            httpGet:
              path: /
              port: http
        readinessProbe:
            httpGet:
              path: /
              port: http
        resources: {}
```

## Key Improvements

✅ **Standard Labels** - Follows Kubernetes recommended labels
✅ **Flexible Configuration** - No need to edit files
✅ **Better Naming** - Consistent naming conventions
✅ **Service Account** - Properly managed for RBAC
✅ **Health Checks** - Built-in liveness and readiness probes
✅ **Scalability** - Easy to enable autoscaling
✅ **Maintainability** - DRY (Don't Repeat Yourself) principle
✅ **Versioning** - Chart versioning support
✅ **Rollback** - Simple rollback mechanism
✅ **Documentation** - Professional chart documentation


