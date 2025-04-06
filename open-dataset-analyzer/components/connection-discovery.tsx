"use client"

import { useState, useEffect, useCallback } from "react"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { ArrowPathIcon, LinkIcon, LightBulbIcon, ArrowsRightLeftIcon } from "@heroicons/react/24/outline"
import ReactFlow, {
  MiniMap,
  Controls,
  Background,
  addEdge,
  applyNodeChanges,
  applyEdgeChanges,
  Node,
  Edge,
  NodeChange,
  EdgeChange,
  Connection,
} from 'react-flow-renderer';
import 'react-flow-renderer/dist/style.css';

type ConnectionData = {
  id: string;
  dataset: string;
  relatedDataset: string;
  confidence: number;
  relationshipType: string;
  description: string;
};

export default function ConnectionDiscovery() {
  const [isDiscovering, setIsDiscovering] = useState(false)
  const [connections, setConnections] = useState<ConnectionData[]>([
    {
      id: "1",
      dataset: "Air Quality Measurements",
      relatedDataset: "Public Transport Schedule",
      confidence: 78,
      relationshipType: "Temporal correlation",
      description: "Air quality measurements show correlation with public transport frequency",
    },
    {
      id: "2",
      dataset: "COVID-19 Cases by Region",
      relatedDataset: "Air Quality Measurements",
      confidence: 65,
      relationshipType: "Geographic overlap",
      description: "Both datasets cover the same geographic regions",
    },
  ])

  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    [setNodes]
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    [setEdges]
  );

  useEffect(() => {
    const datasetNames = new Set<string>();
    connections.forEach(conn => {
      datasetNames.add(conn.dataset);
      datasetNames.add(conn.relatedDataset);
    });

    const initialNodes: Node[] = Array.from(datasetNames).map((name, index) => ({
      id: name,
      data: { label: name },
      position: { x: Math.random() * 400, y: Math.random() * 200 },
    }));

    const initialEdges: Edge[] = connections.map((conn, index) => ({
      id: `e-${conn.id}`,
      source: conn.dataset,
      target: conn.relatedDataset,
      label: `${conn.relationshipType} (${conn.confidence}%)`,
      animated: conn.confidence > 75,
      style: { stroke: conn.confidence > 70 ? 'hsl(var(--chart-1))' : 'hsl(var(--secondary))' },
    }));

    setNodes(initialNodes);
    setEdges(initialEdges);

  }, [connections]);

  const handleDiscover = () => {
    setIsDiscovering(true)
    setTimeout(() => {
      const newConnection = {
        id: (connections.length + 1).toString(),
        dataset: "Public Transport Schedule",
        relatedDataset: "COVID-19 Cases by Region",
        confidence: Math.floor(Math.random() * 30) + 60,
        relationshipType: "Temporal pattern",
        description: "Transport schedule changes correlate with COVID-19 case fluctuations",
      }
      setConnections([newConnection, ...connections])
      setIsDiscovering(false)
    }, 2500)
  }

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Connection Discovery</CardTitle>
        <CardDescription>Discover relationships between datasets using LLM analysis</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="connections">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="connections">Connections</TabsTrigger>
            <TabsTrigger value="visualization">Visualization</TabsTrigger>
          </TabsList>
          <TabsContent value="connections" className="space-y-4">
            <div className="space-y-4 mt-4">
              {connections.map((connection) => (
                <div key={connection.id} className="rounded-md border p-3 space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="font-medium flex items-center">
                      <LinkIcon className="h-4 w-4 mr-2" />
                      Connection #{connection.id}
                    </div>
                    <Badge variant={connection.confidence > 70 ? "default" : "secondary"}>
                      {connection.confidence}% confidence
                    </Badge>
                  </div>

                  <div className="flex items-center text-sm">
                    <ArrowsRightLeftIcon className="h-4 w-4 mr-2 text-muted-foreground" />
                    <span className="font-medium">{connection.dataset}</span>
                    <span className="mx-2">↔</span>
                    <span className="font-medium">{connection.relatedDataset}</span>
                  </div>

                  <div className="text-sm">
                    <span className="font-medium">Type: </span>
                    {connection.relationshipType}
                  </div>

                  <div className="text-sm text-muted-foreground flex items-start">
                    <LightBulbIcon className="h-4 w-4 mr-2 mt-0.5 flex-shrink-0" />
                    <span>{connection.description}</span>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="visualization" className="space-y-4">
            <div className="space-y-4 mt-4">
              <div style={{ height: '300px', border: '1px solid hsl(var(--border))', borderRadius: 'var(--radius)' }}>
                <ReactFlow
                  nodes={nodes}
                  edges={edges}
                  onNodesChange={onNodesChange}
                  onEdgesChange={onEdgesChange}
                  fitView
                  attributionPosition="bottom-left"
                >
                  <MiniMap />
                  <Controls />
                  <Background />
                </ReactFlow>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
      <CardFooter className="border-t px-6 py-4">
        <Button onClick={handleDiscover} disabled={isDiscovering} className="w-full">
          {isDiscovering ? (
            <>
              <ArrowPathIcon className="h-4 w-4 mr-2 animate-spin" />
              Discovering Connections...
            </>
          ) : (
            "Discover New Connections"
          )}
        </Button>
      </CardFooter>
    </Card>
  )
}

