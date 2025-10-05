import React, { useMemo, useState } from 'react'
import { ReactFlow, Node, Edge, Background, Controls, useNodesState, useEdgesState } from 'reactflow'
import 'reactflow/dist/style.css'
import { PlanDoc, PlanNode } from '../lib/api'
import { getHeatColor } from '../lib/color'
import { formatDuration, formatNumber } from '../lib/format'

interface PlanCanvasProps {
  plan: PlanDoc
  onNodeSelect: (node: PlanNode) => void
  selectedNode: PlanNode | null
  presentationMode: boolean
}

const PlanCanvas: React.FC<PlanCanvasProps> = ({ 
  plan, 
  onNodeSelect, 
  selectedNode, 
  presentationMode 
}) => {
  const [showCriticalPath, setShowCriticalPath] = useState(false)
  const [showHeatmap, setShowHeatmap] = useState(true)
  const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set())

  const { nodes, edges } = useMemo(() => {
    const reactFlowNodes: Node[] = plan.nodes.map(node => {
      const isCritical = showCriticalPath && plan.critical_path.includes(node.id)
      const isSelected = selectedNode?.id === node.id
      const isExpanded = expandedNodes.has(node.id)
      
      return {
        id: node.id,
        type: 'custom',
        position: { 
          x: node.depth * 300, 
          y: Math.random() * 400 // Simple layout - could be improved
        },
        data: {
          ...node,
          isCritical,
          isSelected,
          isExpanded,
          onSelect: () => onNodeSelect(node),
          onToggleExpand: () => {
            const newExpanded = new Set(expandedNodes)
            if (expandedNodes.has(node.id)) {
              newExpanded.delete(node.id)
            } else {
              newExpanded.add(node.id)
            }
            setExpandedNodes(newExpanded)
          }
        },
        style: {
          backgroundColor: showHeatmap ? getHeatColor(node.heat_score) : '#fff',
          border: isCritical ? '3px solid #ff6b6b' : isSelected ? '2px solid #4ecdc4' : '1px solid #ddd',
          borderRadius: '8px',
          padding: presentationMode ? '16px' : '12px',
          fontSize: presentationMode ? '14px' : '12px',
          minWidth: presentationMode ? '200px' : '150px',
          boxShadow: isCritical ? '0 0 20px rgba(255, 107, 107, 0.5)' : '0 2px 8px rgba(0,0,0,0.1)'
        }
      }
    })

    const reactFlowEdges: Edge[] = plan.edges.map(edge => ({
      id: `${edge.source}-${edge.target}`,
      source: edge.source,
      target: edge.target,
      style: {
        stroke: showCriticalPath && 
                plan.critical_path.includes(edge.source) && 
                plan.critical_path.includes(edge.target) 
                ? '#ff6b6b' : '#999',
        strokeWidth: showCriticalPath && 
                    plan.critical_path.includes(edge.source) && 
                    plan.critical_path.includes(edge.target) 
                    ? 3 : 1
      }
    }))

    return { nodes: reactFlowNodes, edges: reactFlowEdges }
  }, [plan, showCriticalPath, selectedNode, expandedNodes, presentationMode, onNodeSelect])

  const [nodesState, , onNodesChange] = useNodesState(nodes)
  const [edgesState, , onEdgesChange] = useEdgesState(edges)

  return (
    <div className="plan-canvas">
      <div className="canvas-controls">
        <div className="control-group">
          <label>
            <input
              type="checkbox"
              checked={showCriticalPath}
              onChange={(e) => setShowCriticalPath(e.target.checked)}
            />
            Highlight Critical Path
          </label>
          <label>
            <input
              type="checkbox"
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
            />
            Show Heatmap
          </label>
        </div>
        
        <div className="canvas-stats">
          <span>Nodes: {plan.nodes.length}</span>
          <span>Total Time: {formatDuration(plan.summary.totalTimeMs)}</span>
          <span>Total Cost: {formatNumber(plan.summary.totalCost)}</span>
        </div>
      </div>

      <div className="canvas-container" style={{ height: presentationMode ? '600px' : '500px' }}>
        <ReactFlow
          nodes={nodesState}
          edges={edgesState}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          fitViewOptions={{ padding: 0.1 }}
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  )
}

// Custom node component (unused for now)
/*
const CustomNode: React.FC<{ data: any }> = ({ data }) => {
  const node = data as PlanNode & {
    isCritical: boolean
    isSelected: boolean
    isExpanded: boolean
    onSelect: () => void
    onToggleExpand: () => void
  }

  return (
    <div 
      className={`custom-node ${node.isCritical ? 'critical' : ''} ${node.isSelected ? 'selected' : ''}`}
      onClick={node.onSelect}
    >
      <div className="node-header">
        <span className="node-type">{node.type}</span>
        {node.relation && <span className="node-relation">{node.relation}</span>}
        {node.indexName && <span className="node-index">({node.indexName})</span>}
      </div>
      
      <div className="node-metrics">
        <div className="metric-row">
          <span>Rows:</span>
          <span className="metric-value">
            {formatNumber(node.actualRows)} / {formatNumber(node.rowEstimate)}
            {node.rowErrorFactor > 2 && (
              <span className="error-indicator">⚠️ {node.rowErrorFactor.toFixed(1)}x</span>
            )}
          </span>
        </div>
        
        <div className="metric-row">
          <span>Time:</span>
          <span className="metric-value">
            {formatDuration(node.actualExclusiveTime)}ms
          </span>
        </div>
        
        <div className="metric-row">
          <span>Buffers:</span>
          <span className="metric-value">
            {formatNumber(node.buffers.sharedHit)}H / {formatNumber(node.buffers.sharedRead)}R
          </span>
        </div>
      </div>
      
      <div className="heat-bar">
        <div 
          className="heat-fill" 
          style={{ 
            width: `${node.heat_score * 100}%`,
            backgroundColor: getHeatColor(node.heat_score)
          }}
        />
      </div>
      
      {node.warnings.length > 0 && (
        <div className="node-warnings">
          {node.warnings.map((warning, i) => (
            <div key={i} className="warning">⚠️ {warning}</div>
          ))}
        </div>
      )}
    </div>
  )
}
*/

export default PlanCanvas
