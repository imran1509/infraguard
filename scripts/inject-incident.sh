#!/bin/bash

# InfraGuard - Incident Injection Script
# Usage: ./inject-incident.sh [incident-type]

set -e

NAMESPACE="demo-apps"

function show_usage() {
    echo "Usage: $0 [incident-type]"
    echo ""
    echo "Incident types:"
    echo "  memory-leak    - Simulate memory leak in api-server"
    echo "  cpu-spike      - Simulate CPU spike"
    echo "  crash-loop     - Force pod into CrashLoopBackOff"
    echo "  scale-down     - Scale deployment to 0 (outage)"
    echo "  resource-limit - Hit resource limits"
    echo "  cleanup        - Restore normal state"
    echo ""
}

function inject_memory_leak() {
    echo "🔴 Injecting memory leak incident..."
    
    # Deploy a pod that consumes memory
    kubectl run memory-hog \
        --namespace=$NAMESPACE \
        --image=polinux/stress \
        --restart=Never \
        --labels="app=memory-hog,incident=true" \
        -- stress --vm 1 --vm-bytes 200M --vm-hang 300
    
    echo "✅ Memory leak injected. Pod 'memory-hog' consuming 200MB"
    echo "   Run './inject-incident.sh cleanup' to remove"
}

function inject_cpu_spike() {
    echo "🔴 Injecting CPU spike incident..."
    
    kubectl run cpu-hog \
        --namespace=$NAMESPACE \
        --image=polinux/stress \
        --restart=Never \
        --labels="app=cpu-hog,incident=true" \
        -- stress --cpu 2 --timeout 300
    
    echo "✅ CPU spike injected. Pod 'cpu-hog' consuming CPU"
    echo "   Will auto-terminate in 5 minutes or run cleanup"
}

function inject_crash_loop() {
    echo "🔴 Injecting crash loop incident..."
    
    # Create a pod that crashes immediately
    kubectl run crash-pod \
        --namespace=$NAMESPACE \
        --image=busybox \
        --restart=Always \
        --labels="app=crash-pod,incident=true" \
        -- /bin/sh -c "exit 1"
    
    echo "✅ Crash loop injected. Pod 'crash-pod' will CrashLoopBackOff"
}

function inject_scale_down() {
    echo "🔴 Injecting outage (scaling to 0)..."
    
    kubectl scale deployment/api-server --replicas=0 -n $NAMESPACE
    
    echo "✅ api-server scaled to 0 replicas (simulated outage)"
}

function inject_resource_limit() {
    echo "🔴 Injecting resource limit breach..."
    
    # Patch the deployment with very low limits
    kubectl patch deployment api-server -n $NAMESPACE --type='json' -p='[
        {"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "8Mi"}
    ]'
    
    echo "✅ Memory limit reduced to 8Mi - pods will be OOMKilled"
}

function cleanup() {
    echo "🧹 Cleaning up incidents..."
    
    # Delete incident pods
    kubectl delete pod -n $NAMESPACE -l incident=true --ignore-not-found=true
    
    # Restore api-server replicas
    kubectl scale deployment/api-server --replicas=2 -n $NAMESPACE
    
    # Restore resource limits
    kubectl patch deployment api-server -n $NAMESPACE --type='json' -p='[
        {"op": "replace", "path": "/spec/template/spec/containers/0/resources/limits/memory", "value": "64Mi"}
    ]'
    
    echo "✅ Cleanup complete. System restored to normal."
}

# Main
case "${1:-}" in
    memory-leak)
        inject_memory_leak
        ;;
    cpu-spike)
        inject_cpu_spike
        ;;
    crash-loop)
        inject_crash_loop
        ;;
    scale-down)
        inject_scale_down
        ;;
    resource-limit)
        inject_resource_limit
        ;;
    cleanup)
        cleanup
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
