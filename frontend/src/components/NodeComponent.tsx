import React, { useState, useRef } from 'react';
import { DiagramNode } from '../types';
import './NodeComponent.css';

interface NodeComponentProps {
  node: DiagramNode;
  isSelected: boolean;
  onUpdate: (id: string, updates: Partial<DiagramNode>) => void;
  onDelete: (id: string) => void;
  onClick: (id: string, e: React.MouseEvent) => void;
  onStartConnection: (id: string) => void;
}

const NodeComponent: React.FC<NodeComponentProps> = ({
  node,
  isSelected,
  onUpdate,
  onDelete,
  onClick,
  onStartConnection,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [isEditing, setIsEditing] = useState(false);
  const [editLabel, setEditLabel] = useState(node.label);
  const nodeRef = useRef<HTMLDivElement>(null);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 0) { // Left click
      setIsDragging(true);
      setDragStart({
        x: e.clientX - node.x,
        y: e.clientY - node.y,
      });
    } else if (e.button === 2) { // Right click
      e.preventDefault();
      onStartConnection(node.id);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      const newX = e.clientX - dragStart.x;
      const newY = e.clientY - dragStart.y;
      onUpdate(node.id, { x: newX, y: newY });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleDoubleClick = () => {
    setIsEditing(true);
    setEditLabel(node.label);
  };

  const handleLabelSubmit = () => {
    if (editLabel.trim()) {
      onUpdate(node.id, { label: editLabel.trim() });
    }
    setIsEditing(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleLabelSubmit();
    } else if (e.key === 'Escape') {
      setIsEditing(false);
      setEditLabel(node.label);
    }
  };

  const handleContextMenu = (e: React.MouseEvent) => {
    e.preventDefault();
    onStartConnection(node.id);
  };

  return (
    <div
      ref={nodeRef}
      className={`node ${isSelected ? 'selected' : ''} ${isDragging ? 'dragging' : ''}`}
      style={{
        left: node.x,
        top: node.y,
        width: node.width,
        height: node.height,
        borderColor: node.color,
      }}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onDoubleClick={handleDoubleClick}
      onClick={(e) => onClick(node.id, e)}
      onContextMenu={handleContextMenu}
    >
      <div className="node-header" style={{ backgroundColor: node.color }}>
        <div className="node-icon">{node.icon}</div>
        {isSelected && (
          <button
            className="delete-btn"
            onClick={(e) => {
              e.stopPropagation();
              onDelete(node.id);
            }}
            title="Delete node"
          >
            ×
          </button>
        )}
      </div>
      
      <div className="node-body">
        {isEditing ? (
          <input
            type="text"
            value={editLabel}
            onChange={(e) => setEditLabel(e.target.value)}
            onBlur={handleLabelSubmit}
            onKeyDown={handleKeyDown}
            className="node-label-input"
            autoFocus
          />
        ) : (
          <div className="node-label" title="Double-click to edit">
            {node.label}
          </div>
        )}
      </div>
      
      {isSelected && (
        <div className="node-connection-points">
          <div className="connection-point top" />
          <div className="connection-point right" />
          <div className="connection-point bottom" />
          <div className="connection-point left" />
        </div>
      )}
    </div>
  );
};

export default NodeComponent;
