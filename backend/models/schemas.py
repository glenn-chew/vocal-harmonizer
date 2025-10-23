from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum

class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class RiskItem(BaseModel):
    id: str
    level: RiskLevel
    title: str
    description: str
    service_affected: Optional[str] = None
    recommendation: str
    compliance_rule: Optional[str] = None

class ComplianceIssue(BaseModel):
    id: str
    rule: str
    description: str
    severity: RiskLevel
    affected_services: List[str] = []

class RiskAnalysisResponse(BaseModel):
    risks: List[RiskItem]
    compliance_issues: List[ComplianceIssue]
    summary: str
    overall_risk_score: int = Field(ge=0, le=100)

class VerificationRequest(BaseModel):
    original_diagram: str
    risks: List[RiskItem]

class VerificationResponse(BaseModel):
    original: str
    corrected: str
    changes: List[Dict[str, Any]]
    explanation: str

class AnalysisRequest(BaseModel):
    diagram: str

class AnalysisResponse(BaseModel):
    analysis: RiskAnalysisResponse
    verification: VerificationResponse

class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    services: Dict[str, str]

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

