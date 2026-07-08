"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

const initialNodes = [
  {
    id: "1",
    position: { x: 250, y: 50 },
    data: { label: "Gate A (Optimal)" },
    style: { background: "#0F172A", color: "#00D084", border: "1px solid #00D084", borderRadius: '8px' },
  },
  {
    id: "2",
    position: { x: 100, y: 200 },
    data: { label: "Gate B (Optimal)" },
    style: { background: "#0F172A", color: "#00D084", border: "1px solid #00D084", borderRadius: '8px' },
  },
  {
    id: "3",
    position: { x: 400, y: 200 },
    data: { label: "Gate C (Congested)" },
    style: { background: "#0F172A", color: "#F59E0B", border: "1px solid #F59E0B", borderRadius: '8px' },
  },
  {
    id: "4",
    position: { x: 250, y: 350 },
    data: { label: "Metro Alpha" },
    style: { background: "#0F172A", color: "#4F8CFF", border: "1px solid #4F8CFF", borderRadius: '8px' },
  },
];

const initialEdges = [
  { id: "e1-2", source: "1", target: "2", animated: true, style: { stroke: '#00D084' } },
  { id: "e1-3", source: "1", target: "3", animated: true, style: { stroke: '#F59E0B' } },
  { id: "e2-4", source: "2", target: "4", animated: true, style: { stroke: '#4F8CFF' } },
  { id: "e3-4", source: "3", target: "4", animated: true, style: { stroke: '#F59E0B' } },
];

export function StadiumMap() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: any) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div style={{ width: "100%", height: "100%" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
      >
        <Background gap={16} size={1} color="#1e293b" />
      </ReactFlow>
    </div>
  );
}
