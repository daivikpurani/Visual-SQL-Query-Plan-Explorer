import React, { useState } from 'react'
import { PlanDoc } from '../lib/api'
import UploadBox from './UploadBox'
import PlanCanvas from './PlanCanvas'
import MetricsBar from './MetricsBar'

interface PlanCompareProps {
  onPlanLoad: (plan: PlanDoc) => void
}

const PlanCompare: React.FC<PlanCompareProps> = ({ onPlanLoad: _onPlanLoad }) => {
  const [leftPlan, setLeftPlan] = useState<PlanDoc | null>(null)
  const [rightPlan, setRightPlan] = useState<PlanDoc | null>(null)
  const [comparison, setComparison] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleLeftPlan = (plan: PlanDoc) => {
    setLeftPlan(plan)
    if (rightPlan) {
      comparePlans(plan, rightPlan)
    }
  }

  const handleRightPlan = (plan: PlanDoc) => {
    setRightPlan(plan)
    if (leftPlan) {
      comparePlans(leftPlan, plan)
    }
  }

  const comparePlans = async (left: PlanDoc, right: PlanDoc) => {
    setIsLoading(true)
    try {
      // In a real implementation, this would call the backend comparison API
      // For now, we'll do a simple client-side comparison
      const timeDiff = ((right.summary.totalTimeMs - left.summary.totalTimeMs) / left.summary.totalTimeMs) * 100
      const costDiff = ((right.summary.totalCost - left.summary.totalCost) / left.summary.totalCost) * 100
      const rowsDiff = Math.abs(right.summary.totalRows - left.summary.totalRows) / left.summary.totalRows * 100

      setComparison({
        timeDiff,
        costDiff,
        rowsDiff,
        annotations: []
      })
    } catch (error) {
      console.error('Failed to compare plans:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="plan-compare">
      <h2>Plan Comparison</h2>
      
      <div className="compare-container">
        <div className="compare-side">
          <h3>Plan A (Baseline)</h3>
          <UploadBox onPlanParsed={handleLeftPlan} />
          {leftPlan && (
            <div className="plan-summary">
              <MetricsBar plan={leftPlan} />
            </div>
          )}
        </div>

        <div className="compare-divider">
          <div className="vs-indicator">VS</div>
          {comparison && (
            <div className="comparison-summary">
              <div className={`metric-change ${comparison.timeDiff > 0 ? 'worse' : 'better'}`}>
                Time: {comparison.timeDiff > 0 ? '+' : ''}{comparison.timeDiff.toFixed(1)}%
              </div>
              <div className={`metric-change ${comparison.costDiff > 0 ? 'worse' : 'better'}`}>
                Cost: {comparison.costDiff > 0 ? '+' : ''}{comparison.costDiff.toFixed(1)}%
              </div>
              <div className="metric-change">
                Rows: {comparison.rowsDiff.toFixed(1)}% diff
              </div>
            </div>
          )}
        </div>

        <div className="compare-side">
          <h3>Plan B (Comparison)</h3>
          <UploadBox onPlanParsed={handleRightPlan} />
          {rightPlan && (
            <div className="plan-summary">
              <MetricsBar plan={rightPlan} />
            </div>
          )}
        </div>
      </div>

      {leftPlan && rightPlan && (
        <div className="side-by-side-canvas">
          <div className="canvas-side">
            <h4>Plan A</h4>
            <PlanCanvas 
              plan={leftPlan}
              onNodeSelect={() => {}}
              selectedNode={null}
              presentationMode={false}
            />
          </div>
          <div className="canvas-side">
            <h4>Plan B</h4>
            <PlanCanvas 
              plan={rightPlan}
              onNodeSelect={() => {}}
              selectedNode={null}
              presentationMode={false}
            />
          </div>
        </div>
      )}

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Comparing plans...</div>
        </div>
      )}
    </div>
  )
}

export default PlanCompare
