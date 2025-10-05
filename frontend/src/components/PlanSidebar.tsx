import React, { useState } from 'react'
import { PlanDoc, PlanNode } from '../lib/api'
import { formatDuration, formatNumber } from '../lib/format'

interface PlanSidebarProps {
  node: PlanNode | null
  plan: PlanDoc | null
}

const PlanSidebar: React.FC<PlanSidebarProps> = ({ node, plan: _plan }) => {
  const [activeTab, setActiveTab] = useState<'details' | 'buffers' | 'json'>('details')

  if (!node) {
    return (
      <div className="plan-sidebar">
        <div className="sidebar-placeholder">
          <h3>Select a node to view details</h3>
          <p>Click on any node in the plan to see its detailed information.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="plan-sidebar">
      <div className="sidebar-header">
        <h3>{node.type}</h3>
        {node.relation && <span className="relation">{node.relation}</span>}
      </div>

      <div className="sidebar-tabs">
        <button 
          className={activeTab === 'details' ? 'active' : ''}
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
        <button 
          className={activeTab === 'buffers' ? 'active' : ''}
          onClick={() => setActiveTab('buffers')}
        >
          Buffers
        </button>
        <button 
          className={activeTab === 'json' ? 'active' : ''}
          onClick={() => setActiveTab('json')}
        >
          JSON
        </button>
      </div>

      <div className="sidebar-content">
        {activeTab === 'details' && (
          <div className="details-tab">
            <div className="detail-section">
              <h4>Execution Metrics</h4>
              <div className="metric-grid">
                <div className="metric-item">
                  <label>Total Time:</label>
                  <span>{formatDuration(node.actualTotalTime)}ms</span>
                </div>
                <div className="metric-item">
                  <label>Exclusive Time:</label>
                  <span>{formatDuration(node.actualExclusiveTime)}ms</span>
                </div>
                <div className="metric-item">
                  <label>Loops:</label>
                  <span>{node.actualLoops}</span>
                </div>
                <div className="metric-item">
                  <label>Actual Rows:</label>
                  <span>{formatNumber(node.actualRows)}</span>
                </div>
                <div className="metric-item">
                  <label>Estimated Rows:</label>
                  <span>{formatNumber(node.rowEstimate)}</span>
                </div>
                <div className="metric-item">
                  <label>Row Error Factor:</label>
                  <span className={node.rowErrorFactor > 2 ? 'error' : ''}>
                    {node.rowErrorFactor.toFixed(2)}x
                  </span>
                </div>
              </div>
            </div>

            <div className="detail-section">
              <h4>Cost Information</h4>
              <div className="metric-grid">
                <div className="metric-item">
                  <label>Total Cost:</label>
                  <span>{formatNumber(node.costTotal)}</span>
                </div>
                <div className="metric-item">
                  <label>Startup Cost:</label>
                  <span>{formatNumber(node.costStartup)}</span>
                </div>
              </div>
            </div>

            {node.filter && (
              <div className="detail-section">
                <h4>Filter Condition</h4>
                <div className="condition-box">
                  <code>{node.filter}</code>
                </div>
              </div>
            )}

            {node.joinCond && (
              <div className="detail-section">
                <h4>Join Condition</h4>
                <div className="condition-box">
                  <code>{node.joinCond}</code>
                </div>
              </div>
            )}

            {(node.parallelAware || node.workersLaunched > 0) && (
              <div className="detail-section">
                <h4>Parallel Execution</h4>
                <div className="metric-grid">
                  <div className="metric-item">
                    <label>Parallel Aware:</label>
                    <span>{node.parallelAware ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="metric-item">
                    <label>Workers Launched:</label>
                    <span>{node.workersLaunched}</span>
                  </div>
                </div>
              </div>
            )}

            {node.warnings.length > 0 && (
              <div className="detail-section">
                <h4>Warnings</h4>
                <div className="warnings-list">
                  {node.warnings.map((warning, i) => (
                    <div key={i} className="warning-item">
                      ⚠️ {warning}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'buffers' && (
          <div className="buffers-tab">
            <div className="detail-section">
              <h4>Buffer Statistics</h4>
              <div className="metric-grid">
                <div className="metric-item">
                  <label>Shared Hit:</label>
                  <span className="hit">{formatNumber(node.buffers.sharedHit)} blocks</span>
                </div>
                <div className="metric-item">
                  <label>Shared Read:</label>
                  <span className={node.buffers.sharedRead > 100 ? 'warning' : ''}>
                    {formatNumber(node.buffers.sharedRead)} blocks
                  </span>
                </div>
                <div className="metric-item">
                  <label>Temp Read:</label>
                  <span>{formatNumber(node.buffers.tempRead)} blocks</span>
                </div>
                <div className="metric-item">
                  <label>Temp Written:</label>
                  <span className={node.buffers.tempWritten > 100 ? 'warning' : ''}>
                    {formatNumber(node.buffers.tempWritten)} blocks
                  </span>
                </div>
              </div>
            </div>

            <div className="buffer-analysis">
              <h4>Analysis</h4>
              <div className="analysis-items">
                {node.buffers.sharedRead > 1000 && (
                  <div className="analysis-item warning">
                    High shared read indicates disk I/O - consider adding indexes
                  </div>
                )}
                {node.buffers.tempWritten > 100 && (
                  <div className="analysis-item warning">
                    Large temp files suggest memory pressure or inefficient operations
                  </div>
                )}
                {node.buffers.sharedHit > node.buffers.sharedRead * 10 && (
                  <div className="analysis-item success">
                    Good cache hit ratio - data is mostly in memory
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'json' && (
          <div className="json-tab">
            <h4>Raw Node Data</h4>
            <pre className="json-display">
              {JSON.stringify(node, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default PlanSidebar
