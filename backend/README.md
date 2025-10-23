# Architecture Security Analysis Backend

An agentic backend system for analyzing cloud architecture diagrams for security risks and generating corrected versions.

## Features

- **Risk Analysis Agent**: Analyzes serialized architecture diagrams for security risks using OpenAI GPT-4 and compliance knowledge from Supabase vector store
- **Verification Agent**: Generates corrected architecture diagrams based on risk analysis feedback
- **Vector Store Integration**: Uses Supabase with pgvector for storing and retrieving compliance rules
- **REST API**: FastAPI-based endpoints for frontend integration

## Supported Cloud Services

The system supports security analysis for 18 cloud services across AWS, Azure, and Google Cloud:

### AWS Services
- EC2, Lambda, S3, RDS, CloudFront, SQS

### Azure Services  
- Virtual Machine, Functions, Storage, SQL Database, CDN, Service Bus

### Google Cloud Services
- Compute Engine, Cloud Functions, Cloud Storage, Cloud SQL, Cloud CDN, Pub/Sub

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_service_role_key_here
ENVIRONMENT=dev
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 3. Supabase Setup

1. Create a new Supabase project
2. Enable the pgvector extension
3. Create the required table and function:

```sql
-- Create compliance_rules table
CREATE TABLE compliance_rules (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    details TEXT,
    service_id TEXT,
    category TEXT,
    severity TEXT,
    provider TEXT,
    embedding VECTOR(1536),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector similarity search function
CREATE OR REPLACE FUNCTION match_compliance_rules(
    query_embedding VECTOR(1536),
    match_threshold FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    title TEXT,
    description TEXT,
    details TEXT,
    service_id TEXT,
    category TEXT,
    severity TEXT,
    provider TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE SQL
AS $$
    SELECT
        compliance_rules.id,
        compliance_rules.title,
        compliance_rules.description,
        compliance_rules.details,
        compliance_rules.service_id,
        compliance_rules.category,
        compliance_rules.severity,
        compliance_rules.provider,
        compliance_rules.metadata,
        1 - (compliance_rules.embedding <=> query_embedding) AS similarity
    FROM compliance_rules
    WHERE 1 - (compliance_rules.embedding <=> query_embedding) > match_threshold
    ORDER BY compliance_rules.embedding <=> query_embedding
    LIMIT match_count;
$$;
```

### 4. Seed Compliance Data

```bash
python vector_store/seed_data.py
```

### 5. Run the Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /api/health
```

### Analyze Architecture
```
POST /api/analyze
Content-Type: application/json

{
  "diagram": "@startdiagram\naws-ec2 web-server -> aws-rds database\n@enddiagram"
}
```

### Verify Architecture
```
POST /api/verify
Content-Type: application/json

{
  "original_diagram": "@startdiagram\naws-ec2 web-server -> aws-rds database\n@enddiagram",
  "risks": [...]
}
```

### Combined Analysis and Verification
```
POST /api/analyze-and-verify
Content-Type: application/json

{
  "diagram": "@startdiagram\naws-ec2 web-server -> aws-rds database\n@enddiagram"
}
```

## Diagram Format

The system expects diagrams in the serialized format used by the frontend:

```
@startdiagram
[service_type] [id] [connector] [service_type] [id]
[service_type] [id] [connector] [service_type] [id]
@enddiagram
```

Example:
```
@startdiagram
aws-ec2 web-server -> aws-rds database
aws-s3 storage-bucket -> aws-cloudfront cdn
@enddiagram
```

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   FastAPI        │    │   Supabase      │
│   (React)       │◄──►│   Backend        │◄──►│   Vector Store  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   OpenAI GPT-4   │
                       │   (Agents)       │
                       └──────────────────┘
```

## Development

### Project Structure
```
backend/
├── agents/
│   ├── base_agent.py          # Base agent class
│   ├── risk_analysis_agent.py # Risk analysis agent
│   └── verification_agent.py  # Verification agent
├── models/
│   └── schemas.py             # Pydantic models
├── vector_store/
│   ├── supabase_store.py      # Vector store client
│   └── seed_data.py           # Compliance rules data
├── config.py                  # Configuration
├── main.py                    # FastAPI application
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Testing

Test the API with curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Analyze a simple diagram
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"diagram": "@startdiagram\naws-ec2 web -> aws-rds db\n@enddiagram"}'
```

## Security Considerations

- All API keys should be stored securely in environment variables
- The vector store should be properly secured with appropriate access controls
- Consider implementing rate limiting for production use
- Monitor API usage and costs for OpenAI calls

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate error handling and logging
3. Update tests when adding new features
4. Ensure all new compliance rules are added to the seed data

