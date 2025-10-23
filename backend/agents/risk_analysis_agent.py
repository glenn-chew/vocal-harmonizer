import json
import uuid
from typing import List, Dict, Any
from agents.base_agent import BaseAgent
from vector_store.supabase_store import SupabaseVectorStore
from models.schemas import RiskItem, ComplianceIssue, RiskAnalysisResponse, RiskLevel
import logging

logger = logging.getLogger(__name__)

class RiskAnalysisAgent(BaseAgent):
    """Agent for analyzing architecture diagrams for security risks"""
    
    def __init__(self):
        super().__init__()
        self.vector_store = SupabaseVectorStore()
        
    def process(self, diagram: str) -> RiskAnalysisResponse:
        """Analyze a serialized architecture diagram for security risks"""
        try:
            # Validate diagram format
            if not self._validate_diagram_format(diagram):
                raise ValueError("Invalid diagram format")
            
            # Extract services from diagram
            services = self._extract_services_from_diagram(diagram)
            
            # Get relevant compliance rules
            compliance_rules = self._get_relevant_compliance_rules(services, diagram)
            
            # Analyze risks using OpenAI
            analysis_result = self._analyze_risks_with_ai(diagram, services, compliance_rules)
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(analysis_result['risks'])
            
            return RiskAnalysisResponse(
                risks=analysis_result['risks'],
                compliance_issues=analysis_result['compliance_issues'],
                summary=analysis_result['summary'],
                overall_risk_score=risk_score
            )
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {str(e)}")
            raise Exception(f"Risk analysis failed: {str(e)}")
    
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
    
    def _get_relevant_compliance_rules(self, services: List[str], diagram: str) -> List[Dict[str, Any]]:
        """Get relevant compliance rules for the services in the diagram"""
        all_rules = []
        
        # Get service-specific rules
        for service in services:
            service_rules = self.vector_store.get_service_specific_rules(service)
            all_rules.extend(service_rules)
        
        # Get general architecture rules
        architecture_rules = self.vector_store.search_relevant_rules(
            f"architecture security best practices {diagram}",
            limit=10
        )
        all_rules.extend(architecture_rules)
        
        # Remove duplicates
        seen_ids = set()
        unique_rules = []
        for rule in all_rules:
            if rule['id'] not in seen_ids:
                seen_ids.add(rule['id'])
                unique_rules.append(rule)
        
        return unique_rules
    
    def _analyze_risks_with_ai(self, diagram: str, services: List[str], compliance_rules: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Use OpenAI to analyze risks based on diagram and compliance rules"""
        
        # Format compliance rules for the prompt
        rules_context = self._format_compliance_rules(compliance_rules)
        services_context = self._get_supported_services_context()
        
        prompt = f"""
You are a cloud security expert analyzing architecture diagrams for security risks. 

{services_context}

COMPLIANCE RULES AND BEST PRACTICES:
{rules_context}

ARCHITECTURE DIAGRAM TO ANALYZE:
{diagram}

SERVICES DETECTED: {', '.join(services)}

Please analyze this architecture diagram for security risks and compliance issues. Focus ONLY on the supported services listed above.

Return your analysis in the following JSON format:
{{
    "risks": [
        {{
            "id": "unique_id",
            "level": "critical|high|medium|low",
            "title": "Risk Title",
            "description": "Detailed description of the risk",
            "service_affected": "service_id_if_applicable",
            "recommendation": "Specific recommendation to fix the risk",
            "compliance_rule": "Relevant compliance rule if applicable"
        }}
    ],
    "compliance_issues": [
        {{
            "id": "unique_id",
            "rule": "Compliance rule name",
            "description": "Description of the compliance issue",
            "severity": "critical|high|medium|low",
            "affected_services": ["service1", "service2"]
        }}
    ],
    "summary": "Overall summary of the security posture and main concerns"
}}

Focus on these key security areas:
1. Network security and segmentation
2. Data encryption (at rest and in transit)
3. Access controls and IAM
4. Logging and monitoring
5. Backup and disaster recovery
6. Service-specific security configurations
7. Data flow security
8. Compliance with cloud security best practices

Be specific about which services are affected and provide actionable recommendations.
"""
        
        messages = [
            {"role": "system", "content": "You are a cloud security expert with deep knowledge of AWS, Azure, and GCP security best practices."},
            {"role": "user", "content": prompt}
        ]
        
        response = self._call_openai(messages, temperature=0.1)
        
        # Parse the response
        expected_keys = ["risks", "compliance_issues", "summary"]
        analysis_data = self._parse_json_response(response, expected_keys)
        
        # Convert to proper model objects
        risks = []
        for risk_data in analysis_data['risks']:
            risk = RiskItem(
                id=risk_data.get('id', str(uuid.uuid4())),
                level=RiskLevel(risk_data['level']),
                title=risk_data['title'],
                description=risk_data['description'],
                service_affected=risk_data.get('service_affected'),
                recommendation=risk_data['recommendation'],
                compliance_rule=risk_data.get('compliance_rule')
            )
            risks.append(risk)
        
        compliance_issues = []
        for issue_data in analysis_data['compliance_issues']:
            issue = ComplianceIssue(
                id=issue_data.get('id', str(uuid.uuid4())),
                rule=issue_data['rule'],
                description=issue_data['description'],
                severity=RiskLevel(issue_data['severity']),
                affected_services=issue_data.get('affected_services', [])
            )
            compliance_issues.append(issue)
        
        return {
            'risks': risks,
            'compliance_issues': compliance_issues,
            'summary': analysis_data['summary']
        }
    
    def _format_compliance_rules(self, rules: List[Dict[str, Any]]) -> str:
        """Format compliance rules for the AI prompt"""
        if not rules:
            return "No specific compliance rules found."
        
        formatted_rules = []
        for rule in rules:
            formatted_rule = f"• {rule['title']}: {rule['description']}"
            if rule.get('service_id'):
                formatted_rule += f" (Service: {rule['service_id']})"
            if rule.get('severity'):
                formatted_rule += f" (Severity: {rule['severity']})"
            formatted_rules.append(formatted_rule)
        
        return "\n".join(formatted_rules)
    
    def _calculate_risk_score(self, risks: List[RiskItem]) -> int:
        """Calculate overall risk score (0-100) based on risk levels"""
        if not risks:
            return 0
        
        score_weights = {
            RiskLevel.CRITICAL: 25,
            RiskLevel.HIGH: 15,
            RiskLevel.MEDIUM: 8,
            RiskLevel.LOW: 3
        }
        
        total_score = 0
        for risk in risks:
            total_score += score_weights.get(risk.level, 0)
        
        # Cap at 100
        return min(total_score, 100)

