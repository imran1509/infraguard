#!/usr/bin/env python3
"""
Generate synthetic training data for InfraGuard action selection model.
Uses Oumi's data format for GRPO training.
"""

import json
import random
from typing import List, Dict
from datetime import datetime, timedelta

# Incident types and their characteristics
INCIDENT_TYPES = {
    'high_memory': {
        'severity_range': ['warning', 'critical'],
        'metrics': ['memory_usage_percent', 'memory_limit_mb'],
        'likely_causes': ['memory_leak', 'insufficient_limits', 'traffic_spike'],
    },
    'high_cpu': {
        'severity_range': ['warning', 'critical'],
        'metrics': ['cpu_usage_percent', 'cpu_limit_cores'],
        'likely_causes': ['compute_heavy_task', 'infinite_loop', 'traffic_spike'],
    },
    'crash_loop': {
        'severity_range': ['critical'],
        'metrics': ['restart_count', 'time_since_last_restart'],
        'likely_causes': ['oom_killed', 'config_error', 'dependency_failure', 'code_bug'],
    },
    'pod_pending': {
        'severity_range': ['warning', 'critical'],
        'metrics': ['pending_duration_seconds', 'available_nodes'],
        'likely_causes': ['insufficient_resources', 'node_selector_mismatch', 'pvc_not_bound'],
    },
    'high_latency': {
        'severity_range': ['warning', 'critical'],
        'metrics': ['p99_latency_ms', 'request_rate'],
        'likely_causes': ['database_slow', 'downstream_timeout', 'resource_contention'],
    }
}

# Possible actions
ACTIONS = [
    'restart_pod',
    'scale_horizontal',
    'increase_memory_limit',
    'increase_cpu_limit',
    'rollback_deployment',
    'drain_node',
    'patch_config',
    'escalate_to_human',
    'no_action_needed'
]

# Action success rates based on incident type and cause
ACTION_SUCCESS_RATES = {
    'high_memory': {
        'memory_leak': {'restart_pod': 0.3, 'increase_memory_limit': 0.5, 'patch_config': 0.8, 'escalate_to_human': 0.9},
        'insufficient_limits': {'increase_memory_limit': 0.9, 'restart_pod': 0.2, 'scale_horizontal': 0.6},
        'traffic_spike': {'scale_horizontal': 0.9, 'increase_memory_limit': 0.7, 'no_action_needed': 0.3},
    },
    'crash_loop': {
        'oom_killed': {'increase_memory_limit': 0.8, 'restart_pod': 0.3, 'rollback_deployment': 0.7},
        'config_error': {'patch_config': 0.9, 'rollback_deployment': 0.8, 'restart_pod': 0.2},
        'dependency_failure': {'restart_pod': 0.4, 'escalate_to_human': 0.8, 'no_action_needed': 0.1},
        'code_bug': {'rollback_deployment': 0.9, 'patch_config': 0.3, 'escalate_to_human': 0.8},
    },
    'high_cpu': {
        'compute_heavy_task': {'scale_horizontal': 0.8, 'increase_cpu_limit': 0.7, 'no_action_needed': 0.4},
        'infinite_loop': {'restart_pod': 0.6, 'rollback_deployment': 0.9, 'patch_config': 0.7},
        'traffic_spike': {'scale_horizontal': 0.9, 'increase_cpu_limit': 0.6},
    },
    'pod_pending': {
        'insufficient_resources': {'scale_horizontal': 0.3, 'drain_node': 0.5, 'escalate_to_human': 0.7},
        'node_selector_mismatch': {'patch_config': 0.9, 'escalate_to_human': 0.8},
        'pvc_not_bound': {'patch_config': 0.6, 'escalate_to_human': 0.9},
    },
    'high_latency': {
        'database_slow': {'escalate_to_human': 0.8, 'scale_horizontal': 0.4, 'restart_pod': 0.3},
        'downstream_timeout': {'restart_pod': 0.5, 'patch_config': 0.6, 'escalate_to_human': 0.7},
        'resource_contention': {'scale_horizontal': 0.8, 'increase_cpu_limit': 0.7, 'increase_memory_limit': 0.6},
    }
}


def generate_incident_context(incident_type: str) -> Dict:
    """Generate realistic incident context."""
    
    config = INCIDENT_TYPES[incident_type]
    cause = random.choice(config['likely_causes'])
    severity = random.choice(config['severity_range'])
    
    # Generate metrics based on incident type
    metrics = {}
    if incident_type == 'high_memory':
        metrics['memory_usage_percent'] = random.uniform(75, 98)
        metrics['memory_limit_mb'] = random.choice([64, 128, 256, 512])
    elif incident_type == 'high_cpu':
        metrics['cpu_usage_percent'] = random.uniform(80, 99)
        metrics['cpu_limit_cores'] = random.choice([0.1, 0.25, 0.5, 1.0])
    elif incident_type == 'crash_loop':
        metrics['restart_count'] = random.randint(3, 20)
        metrics['time_since_last_restart'] = random.randint(30, 300)
    elif incident_type == 'pod_pending':
        metrics['pending_duration_seconds'] = random.randint(60, 600)
        metrics['available_nodes'] = random.randint(0, 3)
    elif incident_type == 'high_latency':
        metrics['p99_latency_ms'] = random.randint(500, 5000)
        metrics['request_rate'] = random.randint(100, 10000)
    
    return {
        'incident_type': incident_type,
        'severity': severity,
        'cause': cause,
        'metrics': metrics,
        'pod_name': f"app-{random.choice(['api', 'worker', 'web', 'db'])}-{random.randint(1000, 9999)}",
        'namespace': 'demo-apps',
        'timestamp': (datetime.now() - timedelta(minutes=random.randint(1, 60))).isoformat(),
    }


def calculate_reward(incident_type: str, cause: str, action: str) -> float:
    """Calculate reward for taking an action given incident context."""
    
    success_rates = ACTION_SUCCESS_RATES.get(incident_type, {}).get(cause, {})
    success_rate = success_rates.get(action, 0.1)  # Default low success for unknown combinations
    
    # Add some randomness to simulate real-world variability
    noise = random.uniform(-0.1, 0.1)
    final_rate = max(0, min(1, success_rate + noise))
    
    # Convert to reward
    if final_rate > 0.7:
        return 10.0  # High success
    elif final_rate > 0.4:
        return 5.0   # Partial success
    elif final_rate > 0.2:
        return -5.0  # Failed
    else:
        return -10.0  # Made things worse


def format_as_prompt(context: Dict) -> str:
    """Format incident context as a prompt for the model."""
    
    return f"""You are an SRE AI agent. Analyze this incident and select the best remediation action.

## Incident Details
- Type: {context['incident_type']}
- Severity: {context['severity']}
- Pod: {context['pod_name']}
- Namespace: {context['namespace']}
- Time: {context['timestamp']}

## Metrics
{json.dumps(context['metrics'], indent=2)}

## Available Actions
1. restart_pod - Restart the affected pod
2. scale_horizontal - Add more replicas
3. increase_memory_limit - Increase memory limits
4. increase_cpu_limit - Increase CPU limits
5. rollback_deployment - Roll back to previous version
6. drain_node - Drain the node and reschedule
7. patch_config - Apply configuration patch
8. escalate_to_human - Escalate to human operator
9. no_action_needed - No action required

## Your Task
Select the single best action to resolve this incident. Respond with just the action name."""


def generate_training_example(context: Dict, action: str, reward: float) -> Dict:
    """Generate a single training example in Oumi format."""
    
    prompt = format_as_prompt(context)
    
    return {
        'prompt': prompt,
        'response': action,
        'reward': reward,
        'metadata': {
            'incident_type': context['incident_type'],
            'cause': context['cause'],
            'severity': context['severity'],
        }
    }


def generate_dataset(num_examples: int = 500) -> List[Dict]:
    """Generate a full training dataset."""
    
    dataset = []
    
    for _ in range(num_examples):
        # Random incident type
        incident_type = random.choice(list(INCIDENT_TYPES.keys()))
        context = generate_incident_context(incident_type)
        
        # Generate multiple action-reward pairs for GRPO
        for action in random.sample(ACTIONS, k=min(4, len(ACTIONS))):
            reward = calculate_reward(incident_type, context['cause'], action)
            example = generate_training_example(context, action, reward)
            dataset.append(example)
    
    return dataset


def save_dataset(dataset: List[Dict], output_path: str):
    """Save dataset in JSONL format for Oumi."""
    
    with open(output_path, 'w') as f:
        for example in dataset:
            f.write(json.dumps(example) + '\n')
    
    print(f"✅ Saved {len(dataset)} examples to {output_path}")


def main():
    print("🔧 Generating InfraGuard training dataset...")
    
    # Generate training set
    train_data = generate_dataset(num_examples=400)
    save_dataset(train_data, 'oumi/training/train.jsonl')
    
    # Generate validation set
    val_data = generate_dataset(num_examples=100)
    save_dataset(val_data, 'oumi/training/val.jsonl')
    
    # Print statistics
    print("\n📊 Dataset Statistics:")
    print(f"   Training examples: {len(train_data)}")
    print(f"   Validation examples: {len(val_data)}")
    
    # Print sample
    print("\n📝 Sample training example:")
    sample = train_data[0]
    print(f"   Prompt (truncated): {sample['prompt'][:200]}...")
    print(f"   Response: {sample['response']}")
    print(f"   Reward: {sample['reward']}")


if __name__ == '__main__':
    main()
