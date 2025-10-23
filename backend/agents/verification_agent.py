import json
import uuid
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from models.schemas import RiskItem, VerificationResponse
import logging

logger = logging.getLogger(__name__)

class VerificationAgent(BaseAgent):
    """Agent for generating corrected architecture diagrams based on risk analysis"""
    
    def __init__(self):
        super().__init__()
        
    def process(self, original_diagram: str, risks: List[RiskItem]) -> VerificationResponse:
        """Generate a corrected architecture diagram based on risk analysis"""
        try:
            # Validate original diagram format
            if not self._validate_diagram_format(original_diagram):
                raise ValueError("Invalid original diagram format")
            
            # Debug logging
            logger.info(f"Processing verification with {len(risks)} risks")
            if risks:
                logger.info(f"First risk type: {type(risks[0])}")
                logger.info(f"First risk attributes: {dir(risks[0])}")
            
            # Generate corrected diagram using AI
            corrected_result = self._generate_corrected_diagram(original_diagram, risks)
            
            # Extract changes made
            changes = self._extract_changes(original_diagram, corrected_result['corrected_diagram'])
            
            return VerificationResponse(
                original=original_diagram,
                corrected=corrected_result['corrected_diagram'],
                changes=changes,
                explanation=corrected_result['explanation']
            )
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise Exception(f"Verification failed: {str(e)}")
    
    def _generate_corrected_diagram(self, original_diagram: str, risks: List[RiskItem]) -> Dict[str, str]:
        """Use OpenAI to generate a corrected architecture diagram"""
        
        # Format risks for the prompt
        risks_context = self._format_risks_for_prompt(risks)
        services_context = self._get_supported_services_context()
        
        prompt = f"""
You are a cloud security architect tasked with fixing security issues in architecture diagrams.

{services_context}

ORIGINAL ARCHITECTURE DIAGRAM:
{original_diagram}

SECURITY RISKS IDENTIFIED:
{risks_context}

Your task is to generate a corrected version of the architecture diagram that addresses the identified security risks. 

IMPORTANT CONSTRAINTS:
1. You MUST only use the supported services listed above
2. The output MUST be in the exact same serialized format as the input
3. You can add new services, remove services, or modify connections
4. Focus on security hardening while maintaining functionality
5. Add security services like WAF, encryption gateways, monitoring, etc. if needed
6. Ensure proper network segmentation and access controls

Return your response in the following JSON format:
{{
    "corrected_diagram": "The corrected diagram in the same serialized format",
    "explanation": "Detailed explanation of the changes made and why they improve security"
}}

The corrected diagram should:
- Address all critical and high severity risks
- Implement defense in depth
- Follow cloud security best practices
- Maintain the original functionality where possible
- Use only the supported services listed above

Format the corrected diagram exactly like this:
@startdiagram
[service_type] [id] [connector] [service_type] [id]
[service_type] [id] [connector] [service_type] [id]
@enddiagram
"""
        
        messages = [
            {"role": "system", "content": "You are a cloud security architect with expertise in AWS, Azure, and GCP security best practices."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.2)
        
        # Parse the response
        expected_keys = ["corrected_diagram", "explanation"]
        result_data = self._parse_json_response(response, expected_keys)
        
        # Validate the corrected diagram format
        if not self._validate_diagram_format(result_data['corrected_diagram']):
            raise ValueError("Generated diagram has invalid format")
        
        return result_data
    
    def _format_risks_for_prompt(self, risks: List[RiskItem]) -> str:
        """Format risks for the AI prompt"""
        if not risks:
            return "No specific risks identified."
        
        formatted_risks = []
        for i, risk in enumerate(risks):
            try:
                logger.info(f"Processing risk {i}: {type(risk)}")
                logger.info(f"Risk level: {risk.level}, type: {type(risk.level)}")
                risk_text = f"• [{risk.level.upper()}] {risk.title}: {risk.description}"
                if risk.service_affected:
                    risk_text += f" (Affects: {risk.service_affected})"
                if risk.recommendation:
                    risk_text += f" (Fix: {risk.recommendation})"
                formatted_risks.append(risk_text)
            except Exception as e:
                logger.error(f"Error formatting risk {i}: {e}")
                logger.error(f"Risk object: {risk}")
                logger.error(f"Risk object type: {type(risk)}")
                logger.error(f"Risk object attributes: {dir(risk)}")
                raise
        
        return "\n".join(formatted_risks)
    
    def _extract_changes(self, original: str, corrected: str) -> List[Dict[str, Any]]:
        """Extract and describe the changes made between original and corrected diagrams"""
        changes = []
        
        # Parse both diagrams
        original_connections = self._parse_diagram_connections(original)
        corrected_connections = self._parse_diagram_connections(corrected)
        
        # Find added connections
        original_set = set(original_connections)
        corrected_set = set(corrected_connections)
        
        added = corrected_set - original_set
        removed = original_set - corrected_set
        
        # Add change descriptions
        for connection in added:
            changes.append({
                "type": "added",
                "description": f"Added connection: {connection}",
                "reason": "Security improvement"
            })
        
        for connection in removed:
            changes.append({
                "type": "removed", 
                "description": f"Removed connection: {connection}",
                "reason": "Security risk mitigation"
            })
        
        # Check for service additions/removals
        original_services = self._extract_services_from_diagram(original)
        corrected_services = self._extract_services_from_diagram(corrected)
        
        added_services = set(corrected_services) - set(original_services)
        removed_services = set(original_services) - set(corrected_services)
        
        for service in added_services:
            changes.append({
                "type": "service_added",
                "description": f"Added service: {service}",
                "reason": "Security enhancement"
            })
        
        for service in removed_services:
            changes.append({
                "type": "service_removed",
                "description": f"Removed service: {service}",
                "reason": "Security risk elimination"
            })
        
        return changes
    
    def _parse_diagram_connections(self, diagram: str) -> List[str]:
        """Parse diagram to extract connection strings"""
        connections = []
        lines = diagram.strip().split('\n')
        
        for line in lines[1:-1]:  # Skip start/end markers
            if line.strip():
                connections.append(line.strip())
        
        return connections
    
    def _extract_services_from_diagram(self, diagram: str) -> List[str]:
        """Extract service IDs from the diagram"""
        services = set()
        lines = diagram.strip().split('\n')
        
        for line in lines[1:-1]:  # Skip start/end markers
            parts = line.strip().split()
            if len(parts) >= 4:
                # Extract service types (first and fourth parts)
                services.add(parts[0])
                services.add(parts[3])
        
        return list(services)
