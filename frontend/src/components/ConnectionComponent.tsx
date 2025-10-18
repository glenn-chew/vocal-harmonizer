import React, { useState, useMemo, useRef, useEffect } from 'react';
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
  const [isAnimating, setIsAnimating] = useState(false);
  const animationFrameRef = useRef<number | null>(null);

  const fromNode = nodes.find(n => n.id === connection.from.id);
  const toNode = nodes.find(n => n.id === connection.to.id);

  // Memoize expensive calculations to prevent unnecessary recalculations
  const connectionData = useMemo(() => {
    if (!fromNode || !toNode) {
      return null;
    }

    const fromX = fromNode.x + fromNode.width;
    const fromY = fromNode.y + fromNode.height / 2;
    const toX = toNode.x;
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

    return {
      fromX,
      fromY,
      toX,
      toY,
      pathData,
      distance
    };
  }, [fromNode, toNode]);

  // Detect when nodes are being dragged to enable smooth animation
  useEffect(() => {
    if (fromNode && toNode) {
      // Simple detection: if we're getting frequent updates, we're likely dragging
      setIsAnimating(true);
      
      // Use requestAnimationFrame for smooth updates
      const animate = () => {
        if (isAnimating) {
          animationFrameRef.current = requestAnimationFrame(animate);
        }
      };
      
      animationFrameRef.current = requestAnimationFrame(animate);
      
      // Stop animation after a short delay if no more updates
      const timeoutId = setTimeout(() => {
        setIsAnimating(false);
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      }, 100);
      
      return () => {
        clearTimeout(timeoutId);
        if (animationFrameRef.current) {
          cancelAnimationFrame(animationFrameRef.current);
          animationFrameRef.current = null;
        }
      };
    }
    
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [fromNode?.x, fromNode?.y, toNode?.x, toNode?.y, isAnimating]);

  if (!connectionData) {
    return null;
  }

  const { fromX, fromY, toX, toY, pathData } = connectionData;

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
      className={`connection ${isHovered ? 'hovered' : ''} ${isAnimating ? 'animating' : ''}`}
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
