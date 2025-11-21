#!/bin/bash

# Quick start script for deploying Route Planner Helm chart
# This script provides an interactive way to deploy the chart

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHART_DIR="$SCRIPT_DIR/helm-chart"
RELEASE_NAME="${1:-route-planner}"
NAMESPACE="${2:-default}"

echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}Route Planner Helm Chart Deployment${NC}"
echo -e "${GREEN}=====================================${NC}\n"

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_info "Checking prerequisites..."

if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed. Please install Helm first."
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install kubectl first."
    exit 1
fi

print_info "Prerequisites check passed ✓"

# Display options
echo -e "\n${YELLOW}Select deployment option:${NC}"
echo "1) Deploy to minikube (development)"
echo "2) Deploy with custom values"
echo "3) Deploy production config"
echo "4) Dry-run (preview manifests)"
echo "5) Uninstall"
echo "6) Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        print_info "Deploying to minikube with development settings..."
        helm install "$RELEASE_NAME" "$CHART_DIR" \
            -n "$NAMESPACE" \
            -f "$CHART_DIR/values-dev.yaml"
        print_info "Deployment successful! ✓"
        echo ""
        echo -e "${GREEN}Access your application:${NC}"
        echo "minikube service $RELEASE_NAME"
        ;;
    2)
        read -p "Enter path to custom values file: " values_file
        if [ ! -f "$values_file" ]; then
            print_error "File not found: $values_file"
            exit 1
        fi
        print_info "Deploying with custom values..."
        helm install "$RELEASE_NAME" "$CHART_DIR" \
            -n "$NAMESPACE" \
            -f "$values_file"
        print_info "Deployment successful! ✓"
        ;;
    3)
        print_info "Deploying production configuration..."
        print_warning "Production config uses LoadBalancer service type."
        read -p "Continue? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            print_info "Cancelled."
            exit 0
        fi
        helm install "$RELEASE_NAME" "$CHART_DIR" \
            -n "$NAMESPACE" \
            -f "$CHART_DIR/values-prod.yaml"
        print_info "Deployment successful! ✓"
        ;;
    4)
        print_info "Generating manifests (dry-run)..."
        helm template "$RELEASE_NAME" "$CHART_DIR" > /tmp/route-planner-manifest.yaml
        print_info "Manifests saved to /tmp/route-planner-manifest.yaml"
        echo ""
        read -p "Display manifests? (y/n): " display
        if [ "$display" = "y" ]; then
            cat /tmp/route-planner-manifest.yaml
        fi
        ;;
    5)
        print_warning "This will uninstall the $RELEASE_NAME release from namespace $NAMESPACE"
        read -p "Are you sure? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            helm uninstall "$RELEASE_NAME" -n "$NAMESPACE"
            print_info "Uninstall successful! ✓"
        else
            print_info "Cancelled."
        fi
        ;;
    6)
        print_info "Exiting."
        exit 0
        ;;
    *)
        print_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
print_info "Done!"
print_info "Check status with: kubectl get all -n $NAMESPACE"

