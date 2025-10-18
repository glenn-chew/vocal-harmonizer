import React, { useState, useRef, useCallback } from 'react';
import { useDrop } from 'react-dnd';
import { DiagramNode, DiagramConnection, DragItem } from '../types';
import NodeComponent from './NodeComponent';
import ConnectionComponent from './ConnectionComponent';
import './Canvas.css';

interface CanvasProps {
  nodes: DiagramNode[];
  connections: DiagramConnection[];
  selectedNode: string | null;
  onAddNode: (node: DiagramNode) => void;
  onUpdateNode: (id: string, updates: Partial<DiagramNode>) => void;
  onDeleteNode: (id: string) => void;
  onAddConnection: (connection: DiagramConnection) => void;
  onDeleteConnection: (id: string) => void;
  onSelectNode: (id: string | null) => void;
}

const Canvas: React.FC<CanvasProps> = ({
  nodes,
  connections,
  selectedNode,
  onAddNode,
  onUpdateNode,
  onDeleteNode,
  onAddConnection,
  onDeleteConnection,
  onSelectNode,
}) => {
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState<string | null>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const canvasRef = useRef<HTMLDivElement>(null);

  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'service',
    drop: (item: DragItem, monitor) => {
      if (!canvasRef.current) return;

      const offset = monitor.getClientOffset();
      if (!offset) return;

      const canvasRect = canvasRef.current.getBoundingClientRect();
      const x = offset.x - canvasRect.left;
      const y = offset.y - canvasRect.top;

      const newNode: DiagramNode = {
        id: `${item.service.id}-${Date.now()}`,
        type: item.service.id,
        label: item.service.name,
        x: x - 50, // Center the node
        y: y - 25,
        width: 100,
        height: 50,
        color: item.service.color,
        icon: item.service.icon,
      };

      onAddNode(newNode);
    },
    collect: (monitor) => ({
      isOver: monitor.isOver(),
    }),
  }), [onAddNode]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isConnecting && connectionStart) {
      setMousePos({ x: e.clientX, y: e.clientY });
    }
  }, [isConnecting, connectionStart]);

  const handleNodeClick = useCallback((nodeId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (isConnecting) {
      if (connectionStart && connectionStart !== nodeId) {
        // Create connection
        const newConnection: DiagramConnection = {
          id: `conn-${Date.now()}`,
          from: connectionStart,
          to: nodeId,
          type: 'solid',
          color: '#6b7280',
        };
        onAddConnection(newConnection);
      }
      setIsConnecting(false);
      setConnectionStart(null);
    } else {
      onSelectNode(nodeId);
    }
  }, [isConnecting, connectionStart, onAddConnection, onSelectNode]);

  const handleCanvasClick = useCallback((e: React.MouseEvent) => {
    if (e.target === canvasRef.current) {
      onSelectNode(null);
      if (isConnecting) {
        setIsConnecting(false);
        setConnectionStart(null);
      }
    }
  }, [onSelectNode, isConnecting]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Delete' && selectedNode) {
      onDeleteNode(selectedNode);
    }
    if (e.key === 'Escape') {
      setIsConnecting(false);
      setConnectionStart(null);
      onSelectNode(null);
    }
  }, [selectedNode, onDeleteNode, onSelectNode]);

  const startConnection = useCallback((nodeId: string) => {
    setIsConnecting(true);
    setConnectionStart(nodeId);
  }, []);

  const getConnectionPreview = () => {
    if (!isConnecting || !connectionStart) return null;

    const startNode = nodes.find(n => n.id === connectionStart);
    if (!startNode) return null;

    const startX = startNode.x + startNode.width / 2;
    const startY = startNode.y + startNode.height / 2;

    return (
      <svg
        className="connection-preview"
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 10,
        }}
      >
        <line
          x1={startX}
          y1={startY}
          x2={mousePos.x - (canvasRef.current?.getBoundingClientRect().left || 0)}
          y2={mousePos.y - (canvasRef.current?.getBoundingClientRect().top || 0)}
          stroke="#3b82f6"
          strokeWidth="2"
          strokeDasharray="5,5"
        />
      </svg>
    );
  };

  return (
    <div
      ref={drop}
      className={`canvas ${isOver ? 'drag-over' : ''}`}
      onMouseMove={handleMouseMove}
      onClick={handleCanvasClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
    >
      <div ref={canvasRef} className="canvas-content">
        {connections.map(connection => (
          <ConnectionComponent
            key={connection.id}
            connection={connection}
            nodes={nodes}
            onDelete={onDeleteConnection}
          />
        ))}
        
        {nodes.map(node => (
          <NodeComponent
            key={node.id}
            node={node}
            isSelected={selectedNode === node.id}
            onUpdate={onUpdateNode}
            onDelete={onDeleteNode}
            onClick={handleNodeClick}
            onStartConnection={startConnection}
          />
        ))}
        
        {getConnectionPreview()}
      </div>
      
      <div className="canvas-toolbar">
        <div className="toolbar-info">
          {isConnecting ? (
            <span className="connection-hint">Click on another node to connect</span>
          ) : (
            <span>Drag services from sidebar • Right-click nodes to connect</span>
          )}
        </div>
        <div className="toolbar-stats">
          {nodes.length} nodes • {connections.length} connections
        </div>
      </div>
    </div>
  );
};

export default Canvas;
