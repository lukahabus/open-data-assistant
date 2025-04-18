import React, { useRef, useEffect } from 'react';
import { Dataset } from '../../types/dataset';

interface Connection {
  source: string;
  target: string;
  strength: number;
  relationship: string;
}

interface RelationshipGraphProps {
  datasets: Dataset[];
  connections: Connection[];
}

const RelationshipGraph: React.FC<RelationshipGraphProps> = ({ datasets, connections }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!canvasRef.current || datasets.length === 0) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      const container = canvas.parentElement;
      if (container) {
        canvas.width = container.clientWidth;
        canvas.height = container.clientHeight;
      }
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Map each dataset to a position
    const positions: Record<string, { x: number, y: number }> = {};
    const radius = Math.min(canvas.width, canvas.height) / 3;
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // Position nodes in a circle
    datasets.forEach((dataset, i) => {
      const angle = (i / datasets.length) * 2 * Math.PI;
      positions[dataset.id] = {
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
      };
    });

    // Draw connections
    connections.forEach((connection) => {
      const sourcePos = positions[connection.source];
      const targetPos = positions[connection.target];
      
      if (sourcePos && targetPos) {
        // Draw connection line with strength-based width and opacity
        ctx.beginPath();
        ctx.moveTo(sourcePos.x, sourcePos.y);
        ctx.lineTo(targetPos.x, targetPos.y);
        ctx.strokeStyle = `rgba(66, 153, 225, ${connection.strength})`;
        ctx.lineWidth = Math.max(1, connection.strength * 5);
        ctx.stroke();
        
        // Draw relationship label
        const midX = (sourcePos.x + targetPos.x) / 2;
        const midY = (sourcePos.y + targetPos.y) / 2;
        
        // Add a white background for the text
        const textMeasure = ctx.measureText(connection.relationship);
        const padding = 5;
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.fillRect(
          midX - textMeasure.width / 2 - padding, 
          midY - 10 - padding,
          textMeasure.width + padding * 2,
          20 + padding * 2
        );
        
        ctx.fillStyle = '#4A5568';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(connection.relationship, midX, midY);
      }
    });

    // Draw nodes
    datasets.forEach((dataset) => {
      const position = positions[dataset.id];
      
      if (position) {
        // Draw circle
        ctx.beginPath();
        ctx.arc(position.x, position.y, 30, 0, 2 * Math.PI);
        ctx.fillStyle = '#EBF8FF';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#4299E1';
        ctx.stroke();
        
        // Draw text
        ctx.fillStyle = '#2C5282';
        ctx.font = 'bold 14px Arial';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        // Draw dataset name (abbreviated if needed)
        const name = dataset.title.length > 15 
          ? dataset.title.substring(0, 12) + '...' 
          : dataset.title;
        ctx.fillText(name, position.x, position.y);
      }
    });

    return () => {
      window.removeEventListener('resize', resizeCanvas);
    };
  }, [datasets, connections]);

  return (
    <canvas 
      ref={canvasRef} 
      className="w-full h-full"
    />
  );
};

export default RelationshipGraph;