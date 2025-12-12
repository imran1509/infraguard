#!/usr/bin/env python3
"""
Script to trigger Cline CLI for incident remediation.
Called by Kestra when autonomous fixes are needed.
"""

import argparse
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

def create_incident_prompt(incident_data: dict) -> str:
    """Generate a prompt for Cline based on incident data."""
    
    incident_type = incident_data.get('type', 'unknown')
    severity = incident_data.get('severity', 'warning')
    pod = incident_data.get('pod', 'unknown')
    message = incident_data.get('message', '')
    
    prompts = {
        'high_memory': f"""
## Incident: High Memory Usage
- **Severity**: {severity}
- **Pod**: {pod}
- **Issue**: {message}

Please analyze and fix this memory issue:

1. Check the current memory limits in k8s/manifests/sample-apps.yaml
2. Identify if this is a memory leak or insufficient limits
3. Generate a fix:
   - If limits are too low: Create a patch to increase memory limits by 50%
   - If memory leak suspected: Create a diagnostic script to identify the leak
4. Create a PR with the fix

Output a Kubernetes patch file at: k8s/patches/memory-fix-{pod}.yaml
""",
        'crash_loop': f"""
## Incident: Pod Crash Loop
- **Severity**: {severity}
- **Pod**: {pod}
- **Issue**: {message}

Please analyze and fix this crash loop:

1. First, suggest a command to check pod logs
2. Analyze common causes: OOMKilled, config errors, dependency failures
3. Generate a remediation:
   - Create a rollback script if recent deployment caused this
   - Or create a config patch to fix the issue
4. Create a PR with the fix

Output remediation at: scripts/remediation/fix-crashloop-{pod}.sh
""",
        'pod_not_running': f"""
## Incident: Pod Not Running
- **Severity**: {severity}  
- **Pod**: {pod}
- **Issue**: Pod is in non-running state

Please investigate and fix:

1. Check pod status and events
2. Identify why pod isn't running (ImagePullBackOff, Pending, etc.)
3. Generate appropriate fix:
   - For ImagePullBackOff: Check image name/tag
   - For Pending: Check resource availability
   - For Failed: Check logs and fix code/config
4. Create PR with the fix
""",
        'cpu_spike': f"""
## Incident: High CPU Usage
- **Severity**: {severity}
- **Pod**: {pod}
- **Issue**: {message}

Please analyze and fix this CPU spike:

1. Check current CPU limits
2. Determine if this is normal load or anomaly
3. Generate fix:
   - Create HPA configuration for auto-scaling
   - Or increase CPU limits if appropriate
4. Output at: k8s/patches/cpu-fix-{pod}.yaml
"""
    }
    
    return prompts.get(incident_type, f"""
## Incident: {incident_type}
- **Severity**: {severity}
- **Pod**: {pod}
- **Issue**: {message}

Please analyze this incident and suggest a fix.
""")


def create_branch_name(incident_data: dict) -> str:
    """Create a git branch name for the fix."""
    incident_type = incident_data.get('type', 'unknown')
    pod = incident_data.get('pod', 'unknown')
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    return f"fix/{incident_type}-{pod}-{timestamp}"


def trigger_cline(prompt: str, branch_name: str) -> dict:
    """
    Trigger Cline to fix the incident.
    
    Note: This is a placeholder. In practice, you would either:
    1. Use Cline's CLI interface (if available)
    2. Use the VS Code extension API
    3. Create a file that Cline watches and responds to
    """
    
    # Create a task file for Cline
    task_file = PROJECT_ROOT / "cline-tasks" / f"task-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    task_file.parent.mkdir(exist_ok=True)
    
    task_content = f"""# Cline Task - Incident Fix

## Branch
Create fixes on branch: `{branch_name}`

## Task
{prompt}

## Instructions
1. Create the branch first: `git checkout -b {branch_name}`
2. Implement the fix
3. Commit with message: `fix: automated incident remediation`
4. Push the branch: `git push -u origin {branch_name}`

## After Completion
Mark this task as complete by creating: `cline-tasks/completed/{task_file.name}`
"""
    
    with open(task_file, 'w') as f:
        f.write(task_content)
    
    print(f"✅ Created Cline task: {task_file}")
    print(f"📝 Branch name: {branch_name}")
    print(f"\n📋 Task content:\n{'-'*50}")
    print(task_content)
    
    return {
        'task_file': str(task_file),
        'branch_name': branch_name,
        'status': 'created'
    }


def main():
    parser = argparse.ArgumentParser(description='Trigger Cline for incident fix')
    parser.add_argument('--incident', type=str, required=True,
                       help='JSON string of incident data')
    parser.add_argument('--dry-run', action='store_true',
                       help='Print prompt without triggering Cline')
    
    args = parser.parse_args()
    
    # Parse incident data
    try:
        incident_data = json.loads(args.incident)
    except json.JSONDecodeError as e:
        print(f"Error parsing incident JSON: {e}")
        return 1
    
    print(f"🚨 Processing incident: {incident_data.get('type', 'unknown')}")
    print(f"   Pod: {incident_data.get('pod', 'unknown')}")
    print(f"   Severity: {incident_data.get('severity', 'unknown')}")
    
    # Generate prompt
    prompt = create_incident_prompt(incident_data)
    branch_name = create_branch_name(incident_data)
    
    if args.dry_run:
        print(f"\n📝 Would create prompt:\n{'-'*50}")
        print(prompt)
        print(f"\n🌿 Branch: {branch_name}")
        return 0
    
    # Trigger Cline
    result = trigger_cline(prompt, branch_name)
    print(f"\n✅ Result: {json.dumps(result, indent=2)}")
    
    return 0


if __name__ == '__main__':
    exit(main())
