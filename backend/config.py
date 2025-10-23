import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # OpenAI Configuration
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Supabase Configuration
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")
    
    # Application Configuration
    environment: str = os.getenv("ENVIRONMENT", "dev")
    cors_origins: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
    
    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8080"))
    
    # Supported Cloud Services
    supported_services: List[dict] = [
        # AWS Services
        {"id": "aws-ec2", "name": "EC2", "category": "Compute", "provider": "AWS"},
        {"id": "aws-lambda", "name": "Lambda", "category": "Compute", "provider": "AWS"},
        {"id": "aws-s3", "name": "S3", "category": "Storage", "provider": "AWS"},
        {"id": "aws-rds", "name": "RDS", "category": "Database", "provider": "AWS"},
        {"id": "aws-cloudfront", "name": "CloudFront", "category": "CDN", "provider": "AWS"},
        {"id": "aws-sqs", "name": "SQS", "category": "Messaging", "provider": "AWS"},
        
        # Azure Services
        {"id": "azure-vm", "name": "Virtual Machine", "category": "Compute", "provider": "Azure"},
        {"id": "azure-functions", "name": "Functions", "category": "Compute", "provider": "Azure"},
        {"id": "azure-storage", "name": "Storage", "category": "Storage", "provider": "Azure"},
        {"id": "azure-sql", "name": "SQL Database", "category": "Database", "provider": "Azure"},
        {"id": "azure-cdn", "name": "CDN", "category": "CDN", "provider": "Azure"},
        {"id": "azure-service-bus", "name": "Service Bus", "category": "Messaging", "provider": "Azure"},
        
        # Google Cloud Services
        {"id": "gcp-compute", "name": "Compute Engine", "category": "Compute", "provider": "GCP"},
        {"id": "gcp-cloud-functions", "name": "Cloud Functions", "category": "Compute", "provider": "GCP"},
        {"id": "gcp-storage", "name": "Cloud Storage", "category": "Storage", "provider": "GCP"},
        {"id": "gcp-sql", "name": "Cloud SQL", "category": "Database", "provider": "GCP"},
        {"id": "gcp-cdn", "name": "Cloud CDN", "category": "CDN", "provider": "GCP"},
        {"id": "gcp-pubsub", "name": "Pub/Sub", "category": "Messaging", "provider": "GCP"}
    ]
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
