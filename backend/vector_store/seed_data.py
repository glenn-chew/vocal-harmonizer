"""
Script to seed the Supabase vector store with compliance rules and best practices
for the 18 supported cloud services.
"""

import asyncio
from vector_store.supabase_store import SupabaseVectorStore
from config import settings
import logging

logger = logging.getLogger(__name__)

# Compliance rules and best practices data
COMPLIANCE_RULES = [
    # AWS EC2 Security Rules
    {
        "title": "EC2 Instance Security Groups",
        "description": "EC2 instances should have restrictive security groups that only allow necessary traffic",
        "details": "Security groups should follow the principle of least privilege. Only open ports that are absolutely necessary for the application to function. Use specific IP ranges instead of 0.0.0.0/0 for SSH access.",
        "service_id": "aws-ec2",
        "category": "Network Security",
        "severity": "high",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-3.1", "owasp_category": "A01"}
    },
    {
        "title": "EC2 Instance Encryption",
        "description": "EC2 instances should use encrypted EBS volumes for data at rest",
        "details": "All EBS volumes attached to EC2 instances should be encrypted using AWS KMS. This protects data even if the physical storage is compromised.",
        "service_id": "aws-ec2",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-3.2", "owasp_category": "A02"}
    },
    {
        "title": "EC2 Instance Monitoring",
        "description": "EC2 instances should have CloudWatch monitoring enabled",
        "details": "Enable detailed monitoring and set up CloudWatch alarms for CPU, memory, disk usage, and network traffic. This helps detect security incidents and performance issues.",
        "service_id": "aws-ec2",
        "category": "Monitoring",
        "severity": "medium",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-3.3", "owasp_category": "A09"}
    },
    
    # AWS Lambda Security Rules
    {
        "title": "Lambda Function IAM Roles",
        "description": "Lambda functions should use IAM roles with minimal required permissions",
        "details": "Lambda execution roles should follow the principle of least privilege. Only grant permissions that the function actually needs to perform its tasks.",
        "service_id": "aws-lambda",
        "category": "Access Control",
        "severity": "high",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-4.1", "owasp_category": "A01"}
    },
    {
        "title": "Lambda Function Environment Variables",
        "description": "Sensitive data in Lambda environment variables should be encrypted",
        "details": "Use AWS Systems Manager Parameter Store or AWS Secrets Manager for sensitive configuration data instead of plain text environment variables.",
        "service_id": "aws-lambda",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-4.2", "owasp_category": "A02"}
    },
    {
        "title": "Lambda Function VPC Configuration",
        "description": "Lambda functions accessing VPC resources should be properly configured",
        "details": "When Lambda functions need to access VPC resources, ensure they are placed in private subnets and have appropriate security group configurations.",
        "service_id": "aws-lambda",
        "category": "Network Security",
        "severity": "medium",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-4.3", "owasp_category": "A01"}
    },
    
    # AWS S3 Security Rules
    {
        "title": "S3 Bucket Public Access",
        "description": "S3 buckets should not have public read or write access unless explicitly required",
        "details": "Use S3 bucket policies and Block Public Access settings to prevent accidental public exposure of data. Only enable public access for specific use cases like static website hosting.",
        "service_id": "aws-s3",
        "category": "Access Control",
        "severity": "critical",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-2.1", "owasp_category": "A01"}
    },
    {
        "title": "S3 Bucket Encryption",
        "description": "S3 buckets should have server-side encryption enabled",
        "details": "Enable server-side encryption (SSE-S3, SSE-KMS, or SSE-C) for all S3 buckets to protect data at rest. Use KMS for additional key management control.",
        "service_id": "aws-s3",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-2.2", "owasp_category": "A02"}
    },
    {
        "title": "S3 Bucket Versioning",
        "description": "S3 buckets should have versioning enabled for data protection",
        "details": "Enable versioning to protect against accidental deletion and maintain data integrity. Consider lifecycle policies to manage storage costs.",
        "service_id": "aws-s3",
        "category": "Data Protection",
        "severity": "medium",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-2.3", "owasp_category": "A02"}
    },
    
    # AWS RDS Security Rules
    {
        "title": "RDS Encryption at Rest",
        "description": "RDS instances should have encryption at rest enabled",
        "details": "Enable encryption at rest for all RDS instances to protect sensitive data. Use AWS KMS for key management and ensure backups are also encrypted.",
        "service_id": "aws-rds",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-5.1", "owasp_category": "A02"}
    },
    {
        "title": "RDS Public Access",
        "description": "RDS instances should not be publicly accessible",
        "details": "RDS instances should be placed in private subnets and not have public accessibility enabled unless absolutely necessary for specific use cases.",
        "service_id": "aws-rds",
        "category": "Network Security",
        "severity": "high",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-5.2", "owasp_category": "A01"}
    },
    {
        "title": "RDS Automated Backups",
        "description": "RDS instances should have automated backups enabled",
        "details": "Enable automated backups with appropriate retention periods. Test backup restoration procedures regularly to ensure data recovery capabilities.",
        "service_id": "aws-rds",
        "category": "Data Protection",
        "severity": "high",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-5.3", "owasp_category": "A02"}
    },
    
    # AWS CloudFront Security Rules
    {
        "title": "CloudFront HTTPS Only",
        "description": "CloudFront distributions should enforce HTTPS",
        "details": "Configure CloudFront to redirect HTTP to HTTPS and use SSL/TLS certificates. This protects data in transit and prevents man-in-the-middle attacks.",
        "service_id": "aws-cloudfront",
        "category": "Data Protection",
        "severity": "high",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-6.1", "owasp_category": "A02"}
    },
    {
        "title": "CloudFront Origin Access",
        "description": "CloudFront should use Origin Access Identity for S3 origins",
        "details": "Use Origin Access Identity (OAI) or Origin Access Control (OAC) to restrict direct access to S3 buckets, ensuring content is only accessible through CloudFront.",
        "service_id": "aws-cloudfront",
        "category": "Access Control",
        "severity": "medium",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-6.2", "owasp_category": "A01"}
    },
    
    # AWS SQS Security Rules
    {
        "title": "SQS Queue Encryption",
        "description": "SQS queues should have server-side encryption enabled",
        "details": "Enable server-side encryption for SQS queues to protect message content. Use AWS KMS for key management and ensure proper IAM policies.",
        "service_id": "aws-sqs",
        "category": "Data Protection",
        "severity": "high",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-7.1", "owasp_category": "A02"}
    },
    {
        "title": "SQS Access Policies",
        "description": "SQS queues should have restrictive access policies",
        "details": "Use IAM policies to control access to SQS queues. Implement least privilege access and avoid wildcard permissions.",
        "service_id": "aws-sqs",
        "category": "Access Control",
        "severity": "medium",
        "provider": "AWS",
        "metadata": {"cis_control": "CIS-7.2", "owasp_category": "A01"}
    },
    
    # Azure VM Security Rules
    {
        "title": "Azure VM Network Security Groups",
        "description": "Azure VMs should have restrictive Network Security Groups",
        "details": "Configure NSGs to allow only necessary traffic. Use specific source IP ranges and avoid allowing traffic from 0.0.0.0/0 unless absolutely required.",
        "service_id": "azure-vm",
        "category": "Network Security",
        "severity": "high",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-8.1", "owasp_category": "A01"}
    },
    {
        "title": "Azure VM Disk Encryption",
        "description": "Azure VMs should have disk encryption enabled",
        "details": "Enable Azure Disk Encryption (ADE) or use encrypted managed disks to protect data at rest. Use Azure Key Vault for key management.",
        "service_id": "azure-vm",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-8.2", "owasp_category": "A02"}
    },
    
    # Azure Functions Security Rules
    {
        "title": "Azure Functions Managed Identity",
        "description": "Azure Functions should use Managed Identity for authentication",
        "details": "Use Managed Identity instead of connection strings or keys for accessing Azure services. This eliminates the need to store credentials in code.",
        "service_id": "azure-functions",
        "category": "Access Control",
        "severity": "high",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-9.1", "owasp_category": "A01"}
    },
    {
        "title": "Azure Functions HTTPS Only",
        "description": "Azure Functions should enforce HTTPS",
        "details": "Configure Azure Functions to only accept HTTPS requests. This protects data in transit and ensures secure communication.",
        "service_id": "azure-functions",
        "category": "Data Protection",
        "severity": "high",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-9.2", "owasp_category": "A02"}
    },
    
    # Azure Storage Security Rules
    {
        "title": "Azure Storage Public Access",
        "description": "Azure Storage accounts should not allow public access",
        "details": "Configure storage accounts to prevent public access unless explicitly required. Use private endpoints and proper access policies.",
        "service_id": "azure-storage",
        "category": "Access Control",
        "severity": "critical",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-10.1", "owasp_category": "A01"}
    },
    {
        "title": "Azure Storage Encryption",
        "description": "Azure Storage should have encryption enabled",
        "details": "Enable encryption at rest for all storage accounts. Use customer-managed keys for additional control over encryption keys.",
        "service_id": "azure-storage",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-10.2", "owasp_category": "A02"}
    },
    
    # Azure SQL Security Rules
    {
        "title": "Azure SQL Encryption",
        "description": "Azure SQL databases should have encryption enabled",
        "details": "Enable Transparent Data Encryption (TDE) for all Azure SQL databases. Use customer-managed keys for additional security.",
        "service_id": "azure-sql",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-11.1", "owasp_category": "A02"}
    },
    {
        "title": "Azure SQL Firewall Rules",
        "description": "Azure SQL should have restrictive firewall rules",
        "details": "Configure firewall rules to allow access only from specific IP ranges. Avoid allowing access from 0.0.0.0/0.",
        "service_id": "azure-sql",
        "category": "Network Security",
        "severity": "high",
        "provider": "Azure",
        "metadata": {"cis_control": "CIS-11.2", "owasp_category": "A01"}
    },
    
    # GCP Compute Engine Security Rules
    {
        "title": "GCP Firewall Rules",
        "description": "GCP Compute Engine instances should have restrictive firewall rules",
        "details": "Configure VPC firewall rules to allow only necessary traffic. Use specific source IP ranges and avoid allowing traffic from 0.0.0.0/0.",
        "service_id": "gcp-compute",
        "category": "Network Security",
        "severity": "high",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-12.1", "owasp_category": "A01"}
    },
    {
        "title": "GCP Disk Encryption",
        "description": "GCP Compute Engine disks should be encrypted",
        "details": "Enable encryption for all persistent disks. Use Google-managed or customer-managed encryption keys for additional security.",
        "service_id": "gcp-compute",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-12.2", "owasp_category": "A02"}
    },
    
    # GCP Cloud Functions Security Rules
    {
        "title": "GCP Cloud Functions IAM",
        "description": "GCP Cloud Functions should use minimal IAM permissions",
        "details": "Configure Cloud Functions with IAM roles that follow the principle of least privilege. Only grant permissions necessary for the function to operate.",
        "service_id": "gcp-cloud-functions",
        "category": "Access Control",
        "severity": "high",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-13.1", "owasp_category": "A01"}
    },
    {
        "title": "GCP Cloud Functions HTTPS",
        "description": "GCP Cloud Functions should enforce HTTPS",
        "details": "Configure Cloud Functions to only accept HTTPS requests. This protects data in transit and ensures secure communication.",
        "service_id": "gcp-cloud-functions",
        "category": "Data Protection",
        "severity": "high",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-13.2", "owasp_category": "A02"}
    },
    
    # GCP Cloud Storage Security Rules
    {
        "title": "GCP Cloud Storage Public Access",
        "description": "GCP Cloud Storage buckets should not allow public access",
        "details": "Configure storage buckets to prevent public access unless explicitly required. Use IAM policies and bucket-level permissions.",
        "service_id": "gcp-storage",
        "category": "Access Control",
        "severity": "critical",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-14.1", "owasp_category": "A01"}
    },
    {
        "title": "GCP Cloud Storage Encryption",
        "description": "GCP Cloud Storage should have encryption enabled",
        "details": "Enable encryption at rest for all storage buckets. Use Google-managed or customer-managed encryption keys.",
        "service_id": "gcp-storage",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-14.2", "owasp_category": "A02"}
    },
    
    # GCP Cloud SQL Security Rules
    {
        "title": "GCP Cloud SQL Encryption",
        "description": "GCP Cloud SQL instances should have encryption enabled",
        "details": "Enable encryption at rest for all Cloud SQL instances. Use Google-managed or customer-managed encryption keys.",
        "service_id": "gcp-sql",
        "category": "Data Protection",
        "severity": "critical",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-15.1", "owasp_category": "A02"}
    },
    {
        "title": "GCP Cloud SQL Authorized Networks",
        "description": "GCP Cloud SQL should restrict authorized networks",
        "details": "Configure authorized networks to allow access only from specific IP ranges. Avoid allowing access from 0.0.0.0/0.",
        "service_id": "gcp-sql",
        "category": "Network Security",
        "severity": "high",
        "provider": "GCP",
        "metadata": {"cis_control": "CIS-15.2", "owasp_category": "A01"}
    },
    
    # General Architecture Security Rules
    {
        "title": "Network Segmentation",
        "description": "Architecture should implement proper network segmentation",
        "details": "Use VPCs, subnets, and security groups to segment different tiers of the application. Implement DMZ for public-facing components.",
        "service_id": None,
        "category": "Network Security",
        "severity": "high",
        "provider": "General",
        "metadata": {"owasp_category": "A01", "best_practice": "Defense in Depth"}
    },
    {
        "title": "Load Balancer Security",
        "description": "Load balancers should be properly configured for security",
        "details": "Use Application Load Balancers with WAF capabilities. Implement SSL termination and health checks. Configure proper security groups.",
        "service_id": None,
        "category": "Network Security",
        "severity": "medium",
        "provider": "General",
        "metadata": {"owasp_category": "A01", "best_practice": "Defense in Depth"}
    },
    {
        "title": "Monitoring and Logging",
        "description": "Comprehensive monitoring and logging should be implemented",
        "details": "Implement centralized logging, monitoring, and alerting. Use services like CloudWatch, Azure Monitor, or Google Cloud Monitoring.",
        "service_id": None,
        "category": "Monitoring",
        "severity": "medium",
        "provider": "General",
        "metadata": {"owasp_category": "A09", "best_practice": "Observability"}
    },
    {
        "title": "Backup and Disaster Recovery",
        "description": "Backup and disaster recovery procedures should be in place",
        "details": "Implement automated backups with appropriate retention policies. Test disaster recovery procedures regularly.",
        "service_id": None,
        "category": "Data Protection",
        "severity": "high",
        "provider": "General",
        "metadata": {"owasp_category": "A02", "best_practice": "Business Continuity"}
    }
]

async def seed_compliance_rules():
    """Seed the vector store with compliance rules"""
    vector_store = SupabaseVectorStore()
    
    logger.info("Starting to seed compliance rules...")
    
    success_count = 0
    error_count = 0
    
    for rule in COMPLIANCE_RULES:
        try:
            rule_id = vector_store.add_compliance_rule(rule)
            success_count += 1
            logger.info(f"Added rule: {rule['title']} (ID: {rule_id})")
        except Exception as e:
            error_count += 1
            logger.error(f"Failed to add rule '{rule['title']}': {str(e)}")
    
    logger.info(f"Seeding complete. Success: {success_count}, Errors: {error_count}")
    return success_count, error_count

def main():
    """Main function to run the seeding process"""
    logging.basicConfig(level=logging.INFO)
    
    try:
        success_count, error_count = asyncio.run(seed_compliance_rules())
        
        if error_count == 0:
            logger.info("All compliance rules seeded successfully!")
        else:
            logger.warning(f"Seeding completed with {error_count} errors")
            
    except Exception as e:
        logger.error(f"Seeding failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
