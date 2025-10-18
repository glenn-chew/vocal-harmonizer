# Cloud Architecture Diagram Tool

A modern React-based tool for creating cloud architecture diagrams with drag-and-drop functionality and interactive connections.

## Features

- **Drag & Drop Interface**: Drag cloud services from the sidebar onto the canvas
- **Interactive Connections**: Right-click nodes to create connections between services
- **Multiple Cloud Providers**: Support for AWS, Azure, and Google Cloud services
- **Modern UI**: Beautiful, responsive design with smooth animations
- **Export Functionality**: Export diagrams as PNG images
- **Real-time Editing**: Double-click nodes to edit labels
- **Keyboard Shortcuts**: Delete nodes with Delete key, escape to cancel operations

## Getting Started

### Prerequisites

- Node.js (version 14 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## How to Use

### Adding Services
1. **Drag from Sidebar**: Drag any service icon from the left sidebar onto the canvas
2. **Position**: Drop the service where you want it on the canvas
3. **Edit Labels**: Double-click on any node to edit its label

### Creating Connections
1. **Right-click** on a source node to start a connection
2. **Click** on the target node to complete the connection
3. **Delete Connections**: Double-click on any connection line to delete it

### Managing Nodes
- **Select**: Click on any node to select it
- **Move**: Drag selected nodes to reposition them
- **Delete**: Select a node and press the Delete key, or click the × button when selected

### Exporting
- Click the **"Export PNG"** button in the header to download your diagram as an image

## Available Services

### AWS Services
- EC2 (Compute)
- Lambda (Serverless)
- S3 (Storage)
- RDS (Database)
- VPC (Networking)
- IAM (Security)
- CloudFront (CDN)
- SQS (Messaging)

### Azure Services
- Virtual Machine (Compute)
- Functions (Serverless)
- Storage (Storage)
- SQL Database (Database)
- Virtual Network (Networking)
- Active Directory (Security)
- CDN (CDN)
- Service Bus (Messaging)

### Google Cloud Services
- Compute Engine (Compute)
- Cloud Functions (Serverless)
- Cloud Storage (Storage)
- Cloud SQL (Database)
- VPC (Networking)
- IAM (Security)
- Cloud CDN (CDN)
- Pub/Sub (Messaging)

### Generic Services
- Load Balancer
- API Gateway
- Monitoring
- Logging

## Keyboard Shortcuts

- **Delete**: Delete selected node
- **Escape**: Cancel current operation (connection mode, editing, etc.)

## Technologies Used

- **React 18** - UI framework
- **TypeScript** - Type safety
- **React DnD** - Drag and drop functionality
- **CSS3** - Styling and animations
- **HTML5 Canvas** - Export functionality

## Project Structure

```
src/
├── components/
│   ├── Sidebar.tsx          # Service palette
│   ├── Canvas.tsx           # Main drawing area
│   ├── NodeComponent.tsx    # Individual service nodes
│   └── ConnectionComponent.tsx # Connection lines
├── types.ts                 # TypeScript interfaces
├── App.tsx                  # Main application component
└── index.tsx               # Application entry point
```

## Customization

### Adding New Services
To add new cloud services, edit the `cloudServices` array in `src/components/Sidebar.tsx`:

```typescript
{
  id: 'unique-id',
  name: 'Service Name',
  category: 'Category',
  icon: '🆕',
  color: '#hexcolor',
  description: 'Service description'
}
```

### Styling
- Main styles: `src/App.css`
- Component styles: `src/components/*.css`
- Global styles: `src/index.css`

## Browser Support

- Chrome (recommended)
- Firefox
- Safari
- Edge

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
