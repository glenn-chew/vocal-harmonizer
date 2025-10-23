import openai
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all AI agents with shared OpenAI functionality"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o"  # Latest GPT-4 model
        
    def _call_openai(self, messages: List[Dict[str, str]], temperature: float = 0.1) -> str:
        """Make a call to OpenAI API with error handling"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=4000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            raise Exception(f"AI service unavailable: {str(e)}")
    
    def _parse_json_response(self, response: str, expected_keys: List[str]) -> Dict[str, Any]:
        """Parse JSON response with validation"""
        try:
            # Try to extract JSON from response if it's wrapped in markdown
            if "```json" in response:
                start = response.find("```json") + 7
                end = response.find("```", start)
                json_str = response[start:end].strip()
            else:
                json_str = response.strip()
            
            data = json.loads(json_str)
            
            # Validate required keys
            for key in expected_keys:
                if key not in data:
                    raise ValueError(f"Missing required key: {key}")
            
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise Exception(f"Invalid response format from AI: {str(e)}")
        except ValueError as e:
            logger.error(f"Response validation failed: {str(e)}")
            raise Exception(f"Invalid response structure: {str(e)}")
    
    def _get_supported_services_context(self) -> str:
        """Get formatted context about supported cloud services"""
        services_by_provider = {}
        logger.info(f"Processing {len(settings.supported_services)} services")
        for i, service in enumerate(settings.supported_services):
            logger.info(f"Service {i}: {type(service)} - {service}")
            try:
                provider = service["provider"]
                if provider not in services_by_provider:
                    services_by_provider[provider] = []
                services_by_provider[provider].append(service)
            except Exception as e:
                logger.error(f"Error processing service {i}: {e}")
                logger.error(f"Service object: {service}")
                raise
        
        context = "SUPPORTED CLOUD SERVICES:\n\n"
        for provider, services in services_by_provider.items():
            context += f"{provider} Services:\n"
            for service in services:
                context += f"- {service['name']} ({service['id']}): {service['category']}\n"
            context += "\n"
        
        return context
    
    def _validate_diagram_format(self, diagram: str) -> bool:
        """Validate that the diagram follows the expected serialized format"""
        if not diagram.strip():
            return False
        
        lines = diagram.strip().split('\n')
        if len(lines) < 3:
            return False
        
        # Check for start/end markers
        if not lines[0].startswith('@startdiagram') or not lines[-1].startswith('@enddiagram'):
            return False
        
        # Check that there are actual connections
        connection_lines = lines[1:-1]
        if not connection_lines:
            return False
        
        # Basic validation of connection format
        for line in connection_lines:
            parts = line.strip().split()
            if len(parts) < 4:
                return False
            # Should have: service_type id connector service_type id
            if parts[2] not in ['->', '-->', '..>']:
                return False
        
        return True
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """Process input data and return results"""
        pass
