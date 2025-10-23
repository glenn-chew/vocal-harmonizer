import openai
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
import logging
from config import settings

logger = logging.getLogger(__name__)

class SupabaseVectorStore:
    """Vector store for compliance knowledge using Supabase with pgvector"""
    
    def __init__(self):
        self.supabase: Client = create_client(settings.supabase_url, settings.supabase_key)
        self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        self.embedding_model = "text-embedding-3-small"
        
    def _get_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    def add_compliance_rule(self, rule: Dict[str, Any]) -> str:
        """Add a compliance rule to the vector store"""
        try:
            # Generate embedding for the rule content
            content = f"{rule['title']} {rule['description']} {rule.get('details', '')}"
            embedding = self._get_embedding(content)
            
            # Insert into Supabase
            result = self.supabase.table('compliance-rules').insert({
                'title': rule['title'],
                'description': rule['description'],
                'details': rule.get('details', ''),
                'service_id': rule.get('service_id'),
                'category': rule.get('category', ''),
                'severity': rule.get('severity', 'medium'),
                'provider': rule.get('provider', ''),
                'embedding': embedding,
                'metadata': rule.get('metadata', {})
            }).execute()
            
            if result.data:
                logger.info(f"Added compliance rule: {rule['title']}")
                return result.data[0]['id']
            else:
                raise Exception("Failed to insert compliance rule")
                
        except Exception as e:
            logger.error(f"Failed to add compliance rule: {str(e)}")
            raise Exception(f"Failed to add compliance rule: {str(e)}")
    
    def search_relevant_rules(self, query: str, limit: int = 5, service_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for relevant compliance rules using vector similarity"""
        try:
            # Generate embedding for the query
            query_embedding = self._get_embedding(query)
            
            # Build the search query
            search_query = self.supabase.rpc(
                'match_compliance_rules',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': 0.7,
                    'match_count': limit
                }
            )
            
            # Add service filter if provided
            if service_filter:
                search_query = search_query.eq('service_id', service_filter)
            
            result = search_query.execute()
            
            if result.data:
                logger.info(f"Found {len(result.data)} relevant compliance rules")
                return result.data
            else:
                logger.warning("No relevant compliance rules found")
                return []
                
        except Exception as e:
            logger.error(f"Failed to search compliance rules: {str(e)}")
            # Fallback to simple text search
            return self._fallback_search(query, limit, service_filter)
    
    def _fallback_search(self, query: str, limit: int = 5, service_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fallback text search when vector search fails"""
        try:
            search_query = self.supabase.table('compliance_rules').select('*')
            
            if service_filter:
                search_query = search_query.eq('service_id', service_filter)
            
            # Simple text search in title and description
            search_query = search_query.or_(
                f"title.ilike.%{query}%,description.ilike.%{query}%"
            ).limit(limit)
            
            result = search_query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Fallback search failed: {str(e)}")
            return []
    
    def get_service_specific_rules(self, service_id: str) -> List[Dict[str, Any]]:
        """Get all compliance rules for a specific service"""
        try:
            result = self.supabase.table('compliance_rules').select('*').eq('service_id', service_id).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get service-specific rules: {str(e)}")
            return []
    
    def get_rules_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get compliance rules by category"""
        try:
            result = self.supabase.table('compliance_rules').select('*').eq('category', category).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get rules by category: {str(e)}")
            return []
    
    def initialize_database(self):
        """Initialize the database schema if it doesn't exist"""
        try:
            # This would typically be done via Supabase migrations
            # For now, we'll just log that initialization is needed
            logger.info("Database initialization should be done via Supabase migrations")
            logger.info("Required table: compliance_rules with columns: id, title, description, details, service_id, category, severity, provider, embedding, metadata, created_at")
            logger.info("Required function: match_compliance_rules for vector similarity search")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise Exception(f"Database initialization failed: {str(e)}")
    
    def health_check(self) -> bool:
        """Check if the vector store is healthy"""
        try:
            # Simple query to test connection
            result = self.supabase.table('compliance-rules').select('id').limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Vector store health check failed: {str(e)}")
            return False
