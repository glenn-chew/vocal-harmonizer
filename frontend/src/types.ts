export interface DiagramNode {
  id: string;
  type: string;
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color?: string;
  icon?: string;
}

export interface DiagramConnection {
  id: string;
  from: string;
  to: string;
  label?: string;
  type?: 'solid' | 'dashed' | 'dotted';
  color?: string;
}

export interface CloudService {
  id: string;
  name: string;
  category: string;
  icon: string;
  color: string;
  description: string;
}

export interface DragItem {
  type: 'service';
  service: CloudService;
}
