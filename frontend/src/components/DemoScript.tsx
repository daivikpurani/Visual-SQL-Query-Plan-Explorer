import React, { useState } from 'react'
import { PlanDoc } from '../lib/api'
import PlanCanvas from './PlanCanvas'
import MetricsBar from './MetricsBar'

interface DemoScriptProps {
  onPlanLoad: (plan: PlanDoc) => void
}

const DemoScript: React.FC<DemoScriptProps> = ({ onPlanLoad }) => {
  const [currentStep, setCurrentStep] = useState(0)
  const [currentPlan, setCurrentPlan] = useState<PlanDoc | null>(null)

  const demoSteps = [
    {
      title: "Sequential Scan Problem",
      description: "This query performs a sequential scan on a large table without proper indexing.",
      planFile: "plan_seq_scan.json",
      explanation: "Notice the high exclusive time and shared read blocks. This indicates the query is reading from disk."
    },
    {
      title: "Missing Index Detection", 
      description: "The advisor suggests creating an index on the filtered column.",
      planFile: "plan_missing_idx.json",
      explanation: "The advisor identified a filter condition that could benefit from an index."
    },
    {
      title: "After Index Creation",
      description: "After creating the suggested index, the query now uses an index scan.",
      planFile: "plan_with_index.json", 
      explanation: "Notice the dramatic improvement in execution time and reduction in shared reads."
    }
  ]

  const loadDemoPlan = async (planFile: string) => {
    try {
      // In a real implementation, this would load from the sample_plans directory
      // For now, we'll create a mock plan
      const mockPlan: PlanDoc = {
        id: `demo-${planFile}`,
        summary: {
          totalTimeMs: currentStep === 0 ? 1500 : currentStep === 1 ? 1200 : 50,
          totalCost: currentStep === 0 ? 10000 : currentStep === 1 ? 8000 : 100,
          totalRows: 1000,
          warnings: currentStep === 0 ? ["High shared read", "Sequential scan detected"] : []
        },
        nodes: [
          {
            id: "1",
            parentId: undefined,
            depth: 0,
            type: currentStep === 2 ? "Index Scan" : "Seq Scan",
            relation: "customers",
            actualTotalTime: currentStep === 0 ? 1500 : currentStep === 1 ? 1200 : 50,
            actualRows: 1000,
            actualLoops: 1,
            actualExclusiveTime: currentStep === 0 ? 1500 : currentStep === 1 ? 1200 : 50,
            costTotal: currentStep === 0 ? 10000 : currentStep === 1 ? 8000 : 100,
            costStartup: 0,
            rowEstimate: 1000,
            rowErrorFactor: 1.0,
            buffers: {
              sharedHit: currentStep === 2 ? 100 : 0,
              sharedRead: currentStep === 0 ? 500 : currentStep === 1 ? 400 : 0,
              tempRead: 0,
              tempWritten: 0
            },
            parallelAware: false,
            workersLaunched: 0,
            heat_score: currentStep === 0 ? 0.8 : currentStep === 1 ? 0.6 : 0.2,
            warnings: currentStep === 0 ? ["High shared read"] : []
          }
        ],
        edges: [],
        critical_path: ["1"],
        warnings: []
      }
      
      setCurrentPlan(mockPlan)
      onPlanLoad(mockPlan)
    } catch (error) {
      console.error('Failed to load demo plan:', error)
    }
  }

  const nextStep = () => {
    if (currentStep < demoSteps.length - 1) {
      const newStep = currentStep + 1
      setCurrentStep(newStep)
      loadDemoPlan(demoSteps[newStep].planFile)
    }
  }

  const prevStep = () => {
    if (currentStep > 0) {
      const newStep = currentStep - 1
      setCurrentStep(newStep)
      loadDemoPlan(demoSteps[newStep].planFile)
    }
  }

  const currentStepData = demoSteps[currentStep]

  return (
    <div className="demo-script">
      <div className="demo-header">
        <h2>Interactive Demo</h2>
        <div className="demo-progress">
          Step {currentStep + 1} of {demoSteps.length}
        </div>
      </div>

      <div className="demo-content">
        <div className="demo-step">
          <h3>{currentStepData.title}</h3>
          <p>{currentStepData.description}</p>
          <div className="demo-explanation">
            <strong>Analysis:</strong> {currentStepData.explanation}
          </div>
        </div>

        {currentPlan && (
          <div className="demo-visualization">
            <div className="demo-metrics">
              <MetricsBar plan={currentPlan} />
            </div>
            <div className="demo-canvas">
              <PlanCanvas 
                plan={currentPlan}
                onNodeSelect={() => {}}
                selectedNode={null}
                presentationMode={true}
              />
            </div>
          </div>
        )}

        <div className="demo-controls">
          <button 
            onClick={prevStep} 
            disabled={currentStep === 0}
            className="demo-btn prev"
          >
            ← Previous
          </button>
          <button 
            onClick={nextStep} 
            disabled={currentStep === demoSteps.length - 1}
            className="demo-btn next"
          >
            Next →
          </button>
        </div>

        <div className="demo-navigation">
          {demoSteps.map((step, index) => (
            <button
              key={index}
              onClick={() => {
                setCurrentStep(index)
                loadDemoPlan(step.planFile)
              }}
              className={`step-btn ${index === currentStep ? 'active' : ''}`}
            >
              {index + 1}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}

export default DemoScript
