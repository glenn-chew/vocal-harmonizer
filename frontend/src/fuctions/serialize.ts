import { DiagramConnection } from "../types";

/**
 * Converts an array of DiagramConnection objects into a structured,
 * LLM-readable text format (inspired by PlantUML / Mermaid syntax).
 */
export function serialize(connections: DiagramConnection[]): string {
  const lines: string[] = [];
  lines.push('@startdiagram');

  for (const conn of connections) {
    const fromType = conn.from.type
    const fromId = conn.from.id
    const toType = conn.to.type
    const toId = conn.to.id
    const connector = getConnectorSymbol(conn.type);

    lines.push(`${fromType} ${fromId} ${connector} ${toType} ${toId}`);
  }

  lines.push('@enddiagram');
  return lines.join('\n');
}

/**
 * Maps connection types to text symbols
 */
function getConnectorSymbol(type?: 'solid' | 'dashed' | 'dotted'): string {
  switch (type) {
    case 'dashed':
      return '-->';
    case 'dotted':
      return '..>';
    default:
      return '->';
  }
}

/**
 * Removes or escapes characters that could break the syntax
 */
function sanitize(label: string): string {
  return label.replace(/[^a-zA-Z0-9_\- ]/g, '_');
}
