#!/usr/bin/env python3
"""
AI-Powered Debugger for Kubernetes RAG Installer
Uses OpenAI API to analyze errors and provide solutions
"""

import os
import json
import logging
import subprocess
import traceback
from typing import Dict, List, Optional, Any
import openai
from datetime import datetime

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")

class AIDebugger:
    def __init__(self, log_file: str = "install.log"):
        self.log_file = log_file
        self.model = "gpt-4-turbo-preview"
        self.max_tokens = 2000
        self.temperature = 0.3
        self.debug_history = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_error(self, error_message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze an error using OpenAI API and provide solutions
        """
        try:
            # Build context information
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_error_prompt(error_message, context)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Parse response
            analysis = response.choices[0].message.content
            parsed_analysis = self._parse_ai_response(analysis)
            
            # Store in history
            self.debug_history.append({
                "timestamp": datetime.now().isoformat(),
                "error": error_message,
                "context": context,
                "analysis": parsed_analysis
            })
            
            self.logger.info(f"AI Analysis completed: {parsed_analysis.get('severity', 'UNKNOWN')} severity")
            return parsed_analysis
            
        except Exception as e:
            self.logger.error(f"Failed to analyze error with AI: {str(e)}")
            return {
                "severity": "CRITICAL",
                "summary": "AI analysis failed",
                "solutions": ["Check OpenAI API key and network connectivity"],
                "error": str(e)
            }
    
    def get_cluster_diagnostics(self) -> Dict[str, Any]:
        """
        Collect comprehensive cluster diagnostics
        """
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "nodes": {},
            "pods": {},
            "services": {},
            "events": {},
            "logs": {}
        }
        
        try:
            # Get node information
            result = subprocess.run(
                ["kubectl", "get", "nodes", "-o", "json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                diagnostics["nodes"] = json.loads(result.stdout)
            
            # Get pod information
            result = subprocess.run(
                ["kubectl", "get", "pods", "--all-namespaces", "-o", "json"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                diagnostics["pods"] = json.loads(result.stdout)
            
            # Get recent events
            result = subprocess.run(
                ["kubectl", "get", "events", "--all-namespaces", "--sort-by=.metadata.creationTimestamp"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                diagnostics["events"] = result.stdout
            
            # Get logs from key pods
            key_pods = [
                "kube-apiserver-master1",
                "kube-controller-manager-master1", 
                "kube-scheduler-master1",
                "etcd-master1"
            ]
            
            for pod in key_pods:
                try:
                    result = subprocess.run(
                        ["kubectl", "logs", pod, "-n", "kube-system", "--tail=50"],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        diagnostics["logs"][pod] = result.stdout
                except:
                    continue
                    
        except Exception as e:
            self.logger.error(f"Failed to collect diagnostics: {str(e)}")
            diagnostics["error"] = str(e)
        
        return diagnostics
    
    def suggest_fixes(self, diagnostics: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Use AI to suggest fixes based on diagnostics
        """
        try:
            system_prompt = """
            You are a Kubernetes expert troubleshooting assistant. Analyze the provided cluster diagnostics 
            and suggest specific, actionable fixes. Focus on:
            1. Node issues (NotReady, resource problems)
            2. Pod failures (CrashLoopBackOff, ImagePullBackOff, etc.)
            3. Service connectivity issues
            4. Resource constraints
            5. Configuration problems
            
            Provide fixes in order of priority and include exact commands to run.
            """
            
            user_prompt = f"""
            Analyze these cluster diagnostics and suggest fixes:
            
            {json.dumps(diagnostics, indent=2)}
            
            Provide your response in JSON format with the following structure:
            {{
                "priority": "HIGH|MEDIUM|LOW",
                "issue": "Brief description of the issue",
                "solution": "Detailed solution steps",
                "commands": ["command1", "command2"],
                "explanation": "Why this fix should work"
            }}
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions if isinstance(suggestions, list) else [suggestions]
            
        except Exception as e:
            self.logger.error(f"Failed to generate suggestions: {str(e)}")
            return [{
                "priority": "HIGH",
                "issue": "AI suggestion generation failed",
                "solution": "Manual troubleshooting required",
                "commands": [],
                "explanation": str(e)
            }]
    
    def validate_solution(self, solution: str, original_error: str) -> Dict[str, Any]:
        """
        Validate if a proposed solution is appropriate for the original error
        """
        try:
            system_prompt = """
            You are a validation expert. Review if the proposed solution is appropriate for the original error.
            Consider:
            1. Does the solution address the root cause?
            2. Is it safe to implement?
            3. Are there any potential side effects?
            4. Is there a better approach?
            
            Provide a confidence score (0-100) and reasoning.
            """
            
            user_prompt = f"""
            Original Error: {original_error}
            
            Proposed Solution: {solution}
            
            Validate this solution and provide:
            1. Confidence score (0-100)
            2. Reasoning
            3. Potential risks
            4. Alternative approaches (if any)
            """
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.2
            )
            
            return {
                "validation": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to validate solution: {str(e)}")
            return {"error": str(e)}
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt for error analysis
        """
        return """
        You are an expert Kubernetes and DevOps engineer specializing in troubleshooting 
        Kubernetes cluster deployments, GPU operator installations, and NVIDIA RAG blueprint deployments.
        
        Your expertise includes:
        - Kubespray Kubernetes cluster deployment
        - NVIDIA GPU Operator installation and configuration
        - NVIDIA RAG blueprint deployment
        - Ansible automation
        - SSH connectivity issues
        - Container orchestration problems
        - GPU resource management
        - Vector database (Milvus) configuration
        
        When analyzing errors, provide:
        1. Severity assessment (LOW, MEDIUM, HIGH, CRITICAL)
        2. Root cause analysis
        3. Step-by-step solutions
        4. Prevention measures
        5. Relevant documentation links
        
        Always prioritize safety and provide commands that can be safely executed.
        """
    
    def _build_error_prompt(self, error_message: str, context: Dict[str, Any] = None) -> str:
        """
        Build the user prompt for error analysis
        """
        context_str = ""
        if context:
            context_str = f"\nContext Information:\n{json.dumps(context, indent=2)}"
        
        return f"""
        Analyze this error from a Kubernetes RAG installer:
        
        Error Message:
        {error_message}
        
        {context_str}
        
        Please provide your analysis in JSON format:
        {{
            "severity": "LOW|MEDIUM|HIGH|CRITICAL",
            "summary": "Brief error summary",
            "root_cause": "Detailed root cause analysis",
            "solutions": [
                {{
                    "step": 1,
                    "description": "Step description",
                    "command": "exact command to run",
                    "explanation": "Why this step is needed"
                }}
            ],
            "prevention": "How to prevent this in the future",
            "documentation": ["relevant links"],
            "estimated_time": "Estimated time to fix"
        }}
        """
    
    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the AI response and extract structured information
        """
        try:
            # Try to extract JSON from the response
            if "```json" in response:
                json_start = response.find("```json") + 7
                json_end = response.find("```", json_start)
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)
            elif "{" in response and "}" in response:
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_str = response[json_start:json_end].strip()
                return json.loads(json_str)
            else:
                # Fallback to unstructured response
                return {
                    "severity": "UNKNOWN",
                    "summary": "AI analysis completed",
                    "raw_response": response,
                    "solutions": ["Manual review required"]
                }
        except json.JSONDecodeError:
            return {
                "severity": "UNKNOWN", 
                "summary": "Failed to parse AI response",
                "raw_response": response,
                "solutions": ["Manual review required"]
            }
    
    def get_debug_history(self) -> List[Dict[str, Any]]:
        """
        Get the history of all debug sessions
        """
        return self.debug_history
    
    def export_debug_report(self, filename: str = None) -> str:
        """
        Export a comprehensive debug report
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"debug_report_{timestamp}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "debug_history": self.debug_history,
            "log_file": self.log_file,
            "summary": {
                "total_errors": len(self.debug_history),
                "critical_errors": len([e for e in self.debug_history if e.get("analysis", {}).get("severity") == "CRITICAL"]),
                "high_errors": len([e for e in self.debug_history if e.get("analysis", {}).get("severity") == "HIGH"])
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filename
