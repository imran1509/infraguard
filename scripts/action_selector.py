#!/usr/bin/env python3
"""
Use the fine-tuned Oumi model to select remediation actions.
"""

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json

class ActionSelector:
    def __init__(self, model_path: str = "./infraguard-model-final"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    
    def select_action(self, incident_data: dict) -> str:
        """Select best action for an incident."""
        
        prompt = self._format_prompt(incident_data)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=20,
            temperature=0.3,
            do_sample=True
        )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        action = self._extract_action(response)
        
        return action
    
    def _format_prompt(self, data: dict) -> str:
        return f"""Incident: {data.get('type', 'unknown')}
Severity: {data.get('severity', 'warning')}
Pod: {data.get('pod', 'unknown')}
Metrics: {json.dumps(data.get('metrics', {}))}

Select action:"""
    
    def _extract_action(self, response: str) -> str:
        """Extract action from model response."""
        actions = [
            'restart_pod', 'scale_horizontal', 'increase_memory_limit',
            'increase_cpu_limit', 'rollback_deployment', 'drain_node',
            'patch_config', 'escalate_to_human', 'no_action_needed'
        ]
        
        response_lower = response.lower()
        for action in actions:
            if action in response_lower:
                return action
        
        return 'escalate_to_human'  # Default safe action


# Usage
if __name__ == '__main__':
    selector = ActionSelector()
    
    test_incident = {
        'type': 'high_memory',
        'severity': 'critical',
        'pod': 'api-server-123',
        'metrics': {'memory_usage_percent': 92}
    }
    
    action = selector.select_action(test_incident)
    print(f"Recommended action: {action}")

