import React, { useState } from 'react';
import { Rnd } from 'react-rnd';
import { DiagramNode, NodeInfo } from '../types';
import './ResizableNodeComponent.css';

interface ResizableNodeComponentProps {
    node: DiagramNode;
    isSelected: boolean;
    onUpdate: (id: string, updates: Partial<DiagramNode>) => void;
    onDelete: (id: string) => void;
    onClick: (nodeInfo: NodeInfo, e: React.MouseEvent) => void;
    onStartConnection: (nodeInfo: NodeInfo) => void;
}

const ResizableNodeComponent: React.FC<ResizableNodeComponentProps> = ({
    node,
    isSelected,
    onUpdate,
    onDelete,
    onClick,
    onStartConnection,
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editLabel, setEditLabel] = useState(node.label);
    const newNodeInfo: NodeInfo = {id: node.id, type: node.type}

    const handleLabelSubmit = () => {
        if (editLabel.trim()) onUpdate(node.id, { label: editLabel.trim() });
        setIsEditing(false);
    };

    return (
        <Rnd
            size={{ width: node.width, height: node.height }}
            position={{ x: node.x, y: node.y }}
            onDragStop={(e, d) => onUpdate(node.id, { x: d.x, y: d.y })}
            onResizeStop={(e, direction, ref, delta, position) => {
                onUpdate(node.id, {
                    width: ref.offsetWidth,
                    height: ref.offsetHeight,
                    ...position,
                });
            }}
            minWidth={30}
            minHeight={40}
            bounds="parent"
            enableResizing={{
                bottom: true,
                bottomLeft: true,
                bottomRight: true,
                left: true,
                right: true,
                top: true,
                topLeft: true,
                topRight: true
            }}
            onClick = {(e: React.MouseEvent) => onClick(newNodeInfo, e)}
            onContextMenu = {(e: React.MouseEvent) => {
                e.preventDefault();
                onStartConnection(newNodeInfo);
            }}
        >
            <div
                className={`resizable-node ${isSelected ? 'selected' : ''}`}
                style={{ borderColor: node.color }}
                onDoubleClick={() => {
                    setIsEditing(true);
                    setEditLabel(node.label);
                }}
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
                    onKeyDown={(e) => {
                        if (e.key === 'Enter') handleLabelSubmit();
                        else if (e.key === 'Escape') setIsEditing(false);
                    }}
                    className="node-label-input"
                    autoFocus
                />
            ) : (
                <div className="node-label">{node.label}</div>
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
        </Rnd >
    );
};

export default ResizableNodeComponent;
