import React from 'react';
import { useDrag } from 'react-dnd';
import { CloudService, DragItem } from '../types';
import './Sidebar.css';

const cloudServices: CloudService[] = [
  // AWS Services
  { id: 'aws-ec2', name: 'EC2', category: 'Compute', icon: '🖥️', color: '#FF9900', description: 'Elastic Compute Cloud' },
  { id: 'aws-lambda', name: 'Lambda', category: 'Compute', icon: '⚡', color: '#FF9900', description: 'Serverless Functions' },
  { id: 'aws-s3', name: 'S3', category: 'Storage', icon: '🪣', color: '#FF9900', description: 'Simple Storage Service' },
  { id: 'aws-rds', name: 'RDS', category: 'Database', icon: '🗄️', color: '#FF9900', description: 'Relational Database' },
  { id: 'aws-vpc', name: 'VPC', category: 'Networking', icon: '🌐', color: '#FF9900', description: 'Virtual Private Cloud' },
  { id: 'aws-iam', name: 'IAM', category: 'Security', icon: '🔐', color: '#FF9900', description: 'Identity & Access Management' },
  { id: 'aws-cloudfront', name: 'CloudFront', category: 'CDN', icon: '🌍', color: '#FF9900', description: 'Content Delivery Network' },
  { id: 'aws-sqs', name: 'SQS', category: 'Messaging', icon: '📬', color: '#FF9900', description: 'Simple Queue Service' },
  
  // Azure Services
  { id: 'azure-vm', name: 'Virtual Machine', category: 'Compute', icon: '🖥️', color: '#0078D4', description: 'Azure Virtual Machine' },
  { id: 'azure-functions', name: 'Functions', category: 'Compute', icon: '⚡', color: '#0078D4', description: 'Azure Functions' },
  { id: 'azure-storage', name: 'Storage', category: 'Storage', icon: '🪣', color: '#0078D4', description: 'Azure Storage' },
  { id: 'azure-sql', name: 'SQL Database', category: 'Database', icon: '🗄️', color: '#0078D4', description: 'Azure SQL Database' },
  { id: 'azure-vnet', name: 'Virtual Network', category: 'Networking', icon: '🌐', color: '#0078D4', description: 'Azure Virtual Network' },
  { id: 'azure-ad', name: 'Active Directory', category: 'Security', icon: '🔐', color: '#0078D4', description: 'Azure Active Directory' },
  { id: 'azure-cdn', name: 'CDN', category: 'CDN', icon: '🌍', color: '#0078D4', description: 'Azure Content Delivery Network' },
  { id: 'azure-service-bus', name: 'Service Bus', category: 'Messaging', icon: '📬', color: '#0078D4', description: 'Azure Service Bus' },
  
  // Google Cloud Services
  { id: 'gcp-compute', name: 'Compute Engine', category: 'Compute', icon: '🖥️', color: '#4285F4', description: 'Google Compute Engine' },
  { id: 'gcp-cloud-functions', name: 'Cloud Functions', category: 'Compute', icon: '⚡', color: '#4285F4', description: 'Google Cloud Functions' },
  { id: 'gcp-storage', name: 'Cloud Storage', category: 'Storage', icon: '🪣', color: '#4285F4', description: 'Google Cloud Storage' },
  { id: 'gcp-sql', name: 'Cloud SQL', category: 'Database', icon: '🗄️', color: '#4285F4', description: 'Google Cloud SQL' },
  { id: 'gcp-vpc', name: 'VPC', category: 'Networking', icon: '🌐', color: '#4285F4', description: 'Google Virtual Private Cloud' },
  { id: 'gcp-iam', name: 'IAM', category: 'Security', icon: '🔐', color: '#4285F4', description: 'Google Cloud IAM' },
  { id: 'gcp-cdn', name: 'Cloud CDN', category: 'CDN', icon: '🌍', color: '#4285F4', description: 'Google Cloud CDN' },
  { id: 'gcp-pubsub', name: 'Pub/Sub', category: 'Messaging', icon: '📬', color: '#4285F4', description: 'Google Cloud Pub/Sub' },
  
  // Generic Services
  { id: 'load-balancer', name: 'Load Balancer', category: 'Networking', icon: '⚖️', color: '#6B7280', description: 'Load Balancer' },
  { id: 'api-gateway', name: 'API Gateway', category: 'Networking', icon: '🚪', color: '#6B7280', description: 'API Gateway' },
  { id: 'monitoring', name: 'Monitoring', category: 'Monitoring', icon: '📊', color: '#6B7280', description: 'Monitoring Service' },
  { id: 'logging', name: 'Logging', category: 'Monitoring', icon: '📝', color: '#6B7280', description: 'Logging Service' },
];

const ServiceItem: React.FC<{ service: CloudService }> = ({ service }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'service',
    item: { type: 'service', service } as DragItem,
    collect: (monitor) => ({
      isDragging: monitor.isDragging(),
    }),
  }));

  return (
    <div
      ref={drag}
      className={`service-item ${isDragging ? 'dragging' : ''}`}
      style={{ borderColor: service.color }}
      title={service.description}
    >
      <div className="service-icon" style={{ backgroundColor: service.color }}>
        {service.icon}
      </div>
      <div className="service-info">
        <div className="service-name">{service.name}</div>
        <div className="service-category">{service.category}</div>
      </div>
    </div>
  );
};

const Sidebar: React.FC = () => {
  const categories = Array.from(new Set(cloudServices.map(service => service.category)));

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h2>Cloud Services</h2>
        <p>Drag services to the canvas</p>
      </div>
      
      <div className="sidebar-content">
        {categories.map(category => (
          <div key={category} className="category-section">
            <h3 className="category-title">{category}</h3>
            <div className="services-grid">
              {cloudServices
                .filter(service => service.category === category)
                .map(service => (
                  <ServiceItem key={service.id} service={service} />
                ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;
