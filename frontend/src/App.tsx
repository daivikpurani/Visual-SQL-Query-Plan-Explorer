import { useState } from 'react'
import UploadBox from './components/UploadBox'
import PlanCanvas from './components/PlanCanvas'
import PlanSidebar from './components/PlanSidebar'
import IndexAdvisor from './components/IndexAdvisor'
import PlanCompare from './components/PlanCompare'
import DemoScript from './components/DemoScript'
import MetricsBar from './components/MetricsBar'
import { PlanDoc, PlanNode } from './lib/api'
import './styles.css'

function App() {
  const [currentPlan, setCurrentPlan] = useState<PlanDoc | null>(null)
  const [selectedNode, setSelectedNode] = useState<PlanNode | null>(null)
  const [showCompare, setShowCompare] = useState(false)
  const [showDemo, setShowDemo] = useState(false)
  const [presentationMode, setPresentationMode] = useState(false)

  const handlePlanParsed = (plan: PlanDoc) => {
    setCurrentPlan(plan)
    setSelectedNode(null)
  }

  const handleNodeSelect = (node: PlanNode) => {
    setSelectedNode(node)
  }

  return (
    <div className={`app ${presentationMode ? 'presentation-mode' : ''}`}>
      <header className="app-header">
        <h1>Visual SQL Plan Explorer</h1>
        <div className="header-controls">
          <button 
            onClick={() => setShowDemo(!showDemo)}
            className={showDemo ? 'active' : ''}
          >
            Demo Mode
          </button>
          <button 
            onClick={() => setShowCompare(!showCompare)}
            className={showCompare ? 'active' : ''}
          >
            Compare Plans
          </button>
          <button 
            onClick={() => setPresentationMode(!presentationMode)}
            className={presentationMode ? 'active' : ''}
          >
            Presentation
          </button>
        </div>
      </header>

      <main className="app-main">
        {showDemo ? (
          <DemoScript onPlanLoad={handlePlanParsed} />
        ) : showCompare ? (
          <PlanCompare onPlanLoad={handlePlanParsed} />
        ) : (
          <>
            <div className="upload-section">
              <UploadBox onPlanParsed={handlePlanParsed} />
            </div>
            
            {currentPlan && (
              <div className="plan-section">
                <div className="metrics-bar">
                  <MetricsBar plan={currentPlan} />
                </div>
                
                <div className="visualization-section">
                  <div className="canvas-container">
                    <PlanCanvas 
                      plan={currentPlan}
                      onNodeSelect={handleNodeSelect}
                      selectedNode={selectedNode}
                      presentationMode={presentationMode}
                    />
                  </div>
                  
                  <div className="sidebar-container">
                    <PlanSidebar 
                      node={selectedNode}
                      plan={currentPlan}
                    />
                  </div>
                </div>
                
                <div className="advisor-section">
                  <IndexAdvisor plan={currentPlan} />
                </div>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default App
