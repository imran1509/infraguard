#!/usr/bin/env python3
"""
Simple Metrics API for InfraGuard
Queries Prometheus and returns formatted data for Kestra AI Agent
"""

from flask import Flask, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

PROMETHEUS_URL = os.getenv('PROMETHEUS_URL', 'http://localhost:9090')

def query_prometheus(query):
    """Execute a PromQL query"""
    try:
        response = requests.get(
            f'{PROMETHEUS_URL}/api/v1/query',
            params={'query': query},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'error': str(e)}

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/api/metrics/summary')
def metrics_summary():
    """Get a summary of all metrics for AI Agent"""
    
    summary = {
        'timestamp': datetime.now().isoformat(),
        'namespace': 'demo-apps',
        'metrics': {}
    }
    
    # Pod status
    pod_status = query_prometheus('kube_pod_status_phase{namespace="demo-apps"}')
    if 'data' in pod_status:
        summary['metrics']['pod_status'] = pod_status['data']['result']
    
    # Memory usage
    memory = query_prometheus(
        'sum(container_memory_usage_bytes{namespace="demo-apps", container!=""}) by (pod, container)'
    )
    if 'data' in memory:
        summary['metrics']['memory_usage'] = memory['data']['result']
    
    # CPU usage
    cpu = query_prometheus(
        'sum(rate(container_cpu_usage_seconds_total{namespace="demo-apps", container!=""}[5m])) by (pod, container)'
    )
    if 'data' in cpu:
        summary['metrics']['cpu_usage'] = cpu['data']['result']
    
    # Restarts
    restarts = query_prometheus(
        'sum(kube_pod_container_status_restarts_total{namespace="demo-apps"}) by (pod)'
    )
    if 'data' in restarts:
        summary['metrics']['restarts'] = restarts['data']['result']
    
    return jsonify(summary)

@app.route('/api/alerts/active')
def active_alerts():
    """Get active alerts from Prometheus/AlertManager"""
    
    try:
        # Query AlertManager for active alerts
        response = requests.get(
            f'{PROMETHEUS_URL}/api/v1/alerts',
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Filter for our namespace
        alerts = []
        if 'data' in data and 'alerts' in data['data']:
            for alert in data['data']['alerts']:
                if alert.get('labels', {}).get('namespace') == 'demo-apps' or \
                   alert.get('labels', {}).get('team') == 'infraguard':
                    alerts.append({
                        'name': alert['labels'].get('alertname'),
                        'severity': alert['labels'].get('severity'),
                        'state': alert['state'],
                        'description': alert['annotations'].get('description', ''),
                        'pod': alert['labels'].get('pod', 'N/A'),
                        'container': alert['labels'].get('container', 'N/A')
                    })
        
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'active_alerts': alerts,
            'count': len(alerts)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/incidents/detect')
def detect_incidents():
    """Detect potential incidents based on metrics"""
    
    incidents = []
    
    # Check for high memory usage
    memory_result = query_prometheus('''
        (container_memory_usage_bytes{namespace="demo-apps", container!=""}
        / container_spec_memory_limit_bytes{namespace="demo-apps", container!=""}) > 0.7
    ''')
    
    if 'data' in memory_result:
        for result in memory_result['data'].get('result', []):
            incidents.append({
                'type': 'high_memory',
                'severity': 'warning',
                'pod': result['metric'].get('pod'),
                'container': result['metric'].get('container'),
                'value': float(result['value'][1]) * 100,
                'message': f"Memory usage at {float(result['value'][1]) * 100:.1f}%"
            })
    
    # Check for crash loops
    restart_result = query_prometheus('''
        rate(kube_pod_container_status_restarts_total{namespace="demo-apps"}[15m]) > 0
    ''')
    
    if 'data' in restart_result:
        for result in restart_result['data'].get('result', []):
            incidents.append({
                'type': 'crash_loop',
                'severity': 'critical',
                'pod': result['metric'].get('pod'),
                'container': result['metric'].get('container', 'N/A'),
                'value': float(result['value'][1]),
                'message': f"Pod restarting frequently"
            })
    
    # Check for pods not running
    pod_status = query_prometheus('''
        kube_pod_status_phase{namespace="demo-apps", phase!="Running", phase!="Succeeded"}
    ''')
    
    if 'data' in pod_status:
        for result in pod_status['data'].get('result', []):
            incidents.append({
                'type': 'pod_not_running',
                'severity': 'critical',
                'pod': result['metric'].get('pod'),
                'phase': result['metric'].get('phase'),
                'message': f"Pod in {result['metric'].get('phase')} state"
            })
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'incidents': incidents,
        'count': len(incidents),
        'has_critical': any(i['severity'] == 'critical' for i in incidents)
    })

if __name__ == '__main__':
    print("Starting InfraGuard Metrics API...")
    print(f"Prometheus URL: {PROMETHEUS_URL}")
    app.run(host='0.0.0.0', port=5000, debug=True)
