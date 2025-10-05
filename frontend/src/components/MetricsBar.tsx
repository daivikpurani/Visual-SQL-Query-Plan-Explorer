import React from 'react'
import { PlanDoc } from '../lib/api'
import { formatDuration, formatNumber } from '../lib/format'

interface MetricsBarProps {
  plan: PlanDoc
}

const MetricsBar: React.FC<MetricsBarProps> = ({ plan }) => {
  const { summary } = plan

  return (
    <div className="metrics-bar">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-label">Total Time</div>
          <div className="metric-value time">
            {formatDuration(summary.totalTimeMs)}
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Total Cost</div>
          <div className="metric-value cost">
            {formatNumber(summary.totalCost)}
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Total Rows</div>
          <div className="metric-value rows">
            {formatNumber(summary.totalRows)}
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Nodes</div>
          <div className="metric-value nodes">
            {plan.nodes.length}
          </div>
        </div>
        
        <div className="metric-card">
          <div className="metric-label">Warnings</div>
          <div className="metric-value warnings">
            {summary.warnings.length}
          </div>
        </div>
      </div>
      
      {summary.warnings.length > 0 && (
        <div className="warnings-summary">
          <h4>Plan Warnings:</h4>
          <ul>
            {summary.warnings.map((warning, index) => (
              <li key={index} className="warning-item">
                ⚠️ {warning}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default MetricsBar
