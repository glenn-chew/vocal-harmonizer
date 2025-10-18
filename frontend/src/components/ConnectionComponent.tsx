import React, { useState } from 'react';
import { DiagramConnection, DiagramNode } from '../types';
import './ConnectionComponent.css';

interface ConnectionComponentProps {
  connection: DiagramConnection;
  nodes: DiagramNode[];
  onDelete: (id: string) => void;
}

const ConnectionComponent: React.FC<ConnectionComponentProps> = ({
  connection,
  nodes,
  onDelete,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const fromNode = nodes.find(n => n.id === connection.from);
  const toNode = nodes.find(n => n.id === connection.to);

  if (!fromNode || !toNode) {
    return null;
  }

  const fromX = fromNode.x + fromNode.width / 2;
  const fromY = fromNode.y + fromNode.height / 2;
  const toX = toNode.x + toNode.width / 2;
  const toY = toNode.y + toNode.height / 2;

  // Calculate control points for curved line
  const dx = toX - fromX;
  const dy = toY - fromY;
  const distance = Math.sqrt(dx * dx + dy * dy);
  const controlOffset = Math.min(distance * 0.3, 100);

  const controlX1 = fromX + (dx > 0 ? controlOffset : -controlOffset);
  const controlY1 = fromY;
  const controlX2 = toX - (dx > 0 ? controlOffset : -controlOffset);
  const controlY2 = toY;

  const pathData = `M ${fromX} ${fromY} C ${controlX1} ${controlY1}, ${controlX2} ${controlY2}, ${toX} ${toY}`;

  const getStrokeDashArray = () => {
    switch (connection.type) {
      case 'dashed':
        return '5,5';
      case 'dotted':
        return '2,3';
      default:
        return 'none';
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (e.detail === 2) { // Double click
      onDelete(connection.id);
    }
  };

  return (
    <svg
      className={`connection ${isHovered ? 'hovered' : ''}`}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
      }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <defs>
        <marker
          id={`arrowhead-${connection.id}`}
          markerWidth="10"
          markerHeight="7"
          refX="9"
          refY="3.5"
          orient="auto"
        >
          <polygon
            points="0 0, 10 3.5, 0 7"
            fill={connection.color || '#6b7280'}
          />
        </marker>
      </defs>
      
      <path
        d={pathData}
        stroke={connection.color || '#6b7280'}
        strokeWidth={isHovered ? 3 : 2}
        strokeDasharray={getStrokeDashArray()}
        fill="none"
        markerEnd={`url(#arrowhead-${connection.id})`}
        className="connection-line"
        onClick={handleClick}
        style={{ pointerEvents: 'stroke' }}
      />
      
      {isHovered && (
        <circle
          cx={toX}
          cy={toY}
          r="4"
          fill={connection.color || '#6b7280'}
          className="connection-endpoint"
          onClick={handleClick}
          style={{ pointerEvents: 'all' }}
        />
      )}
      
      {connection.label && (
        <text
          x={(fromX + toX) / 2}
          y={(fromY + toY) / 2 - 10}
          textAnchor="middle"
          fontSize="12"
          fill="#6b7280"
          className="connection-label"
        >
          {connection.label}
        </text>
      )}
    </svg>
  );
};

export default ConnectionComponent;
