import React, { useState } from 'react';
import './App.css';
import Sidebar from './components/Sidebar';
import Canvas from './components/Canvas';
import { DiagramNode, DiagramConnection, NodeInfo } from './types';
import { serialize } from './fuctions/serialize';

function App() {
  const [nodes, setNodes] = useState<DiagramNode[]>([]);
  const [connections, setConnections] = useState<DiagramConnection[]>([]);
  const [selectedNode, setSelectedNode] = useState<string | null>(null);

  const addNode = (node: DiagramNode) => {
    setNodes(prev => [...prev, node]);
  };

  const updateNode = (id: string, updates: Partial<DiagramNode>) => {
    setNodes(prev => prev.map(node => 
      node.id === id ? { ...node, ...updates } : node
    ));
  };

  const deleteNode = (id: string) => {
    setNodes(prev => prev.filter(node => node.id !== id));
    setConnections(prev => prev.filter(conn => 
      conn.from.id !== id && conn.to.id !== id
    ));
    if (selectedNode === id) {
      setSelectedNode(null);
    }
  };

  const addConnection = (connection: DiagramConnection) => {
    setConnections(prev => [...prev, connection]);
  };

  const deleteConnection = (id: string) => {
    setConnections(prev => prev.filter(conn => conn.id !== id));
  };

  const clearCanvas = () => {
    setNodes([]);
    setConnections([]);
    setSelectedNode(null);
  };

  // const exportDiagram = () => {
  //   const canvas = document.querySelector('.canvas-content') as HTMLElement;
  //   if (!canvas) return;

  //   // Create a temporary canvas for rendering
  //   const tempCanvas = document.createElement('canvas');
  //   const ctx = tempCanvas.getContext('2d');
  //   if (!ctx) return;

  //   // Set canvas size
  //   tempCanvas.width = canvas.scrollWidth;
  //   tempCanvas.height = canvas.scrollHeight;

  //   // Fill background
  //   ctx.fillStyle = '#ffffff';
  //   ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);

  //   // Add grid pattern
  //   ctx.strokeStyle = '#e5e7eb';
  //   ctx.lineWidth = 1;
  //   for (let x = 0; x < tempCanvas.width; x += 20) {
  //     ctx.beginPath();
  //     ctx.moveTo(x, 0);
  //     ctx.lineTo(x, tempCanvas.height);
  //     ctx.stroke();
  //   }
  //   for (let y = 0; y < tempCanvas.height; y += 20) {
  //     ctx.beginPath();
  //     ctx.moveTo(0, y);
  //     ctx.lineTo(tempCanvas.width, y);
  //     ctx.stroke();
  //   }

  //   // Convert to image and download
  //   const link = document.createElement('a');
  //   link.download = 'cloud-architecture-diagram.png';
  //   link.href = tempCanvas.toDataURL();
  //   link.click();
  // };

  

  const handleAskAI = () => {
    const serializedConnections = serialize(connections)
    console.log(serializedConnections)
  }
  return (
    <div className="app">
      <header className="app-header">
        <h1>Cloud Architecture Diagram Tool</h1>
        <div className="header-actions">
          <button onClick={handleAskAI} className="export-btn">
            Ask AI
          </button>
          <button onClick={clearCanvas} className="clear-btn">
            Clear Canvas
          </button>
        </div>
      </header>
      <div className="app-content">
        <Sidebar />
        <Canvas
          nodes={nodes}
          connections={connections}
          selectedNode={selectedNode}
          onAddNode={addNode}
          onUpdateNode={updateNode}
          onDeleteNode={deleteNode}
          onAddConnection={addConnection}
          onDeleteConnection={deleteConnection}
          onSelectNode={setSelectedNode}
        />
      </div>
    </div>
  );
}

export default App;
