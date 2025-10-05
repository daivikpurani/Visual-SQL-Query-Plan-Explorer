import React, { useState, useEffect } from 'react'
import { PlanDoc, Advice } from '../lib/api'
import { getAdvice } from '../lib/api'

interface IndexAdvisorProps {
  plan: PlanDoc
}

const IndexAdvisor: React.FC<IndexAdvisorProps> = ({ plan }) => {
  const [advice, setAdvice] = useState<Advice | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetchAdvice()
  }, [plan.id])

  const fetchAdvice = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const adviceData = await getAdvice(plan)
      setAdvice(adviceData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get advice')
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = (sql: string) => {
    navigator.clipboard.writeText(sql)
    // Could add a toast notification here
  }

  if (isLoading) {
    return (
      <div className="index-advisor">
        <h3>Index Advisor</h3>
        <div className="loading">Analyzing plan for index suggestions...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="index-advisor">
        <h3>Index Advisor</h3>
        <div className="error">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="index-advisor">
      <div className="advisor-header">
        <h3>Index Advisor</h3>
        <button onClick={fetchAdvice} className="refresh-btn">
          Refresh Analysis
        </button>
      </div>

      {advice && (
        <div className="advisor-content">
          {advice.indexes.length > 0 ? (
            <div className="suggestions-section">
              <h4>Suggested Indexes ({advice.indexes.length})</h4>
              <div className="suggestions-list">
                {advice.indexes.map((suggestion, index) => (
                  <div key={index} className="suggestion-item">
                    <div className="suggestion-header">
                      <span className="suggestion-title">
                        {suggestion.table} ({suggestion.columns.join(', ')})
                      </span>
                      <button 
                        onClick={() => copyToClipboard(suggestion.sql)}
                        className="copy-btn"
                        title="Copy SQL to clipboard"
                      >
                        📋 Copy SQL
                      </button>
                    </div>
                    
                    {suggestion.where && (
                      <div className="suggestion-condition">
                        <strong>Condition:</strong> {suggestion.where}
                      </div>
                    )}
                    
                    <div className="suggestion-sql">
                      <code>{suggestion.sql}</code>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="no-suggestions">
              <h4>No Index Suggestions</h4>
              <p>No obvious index improvements found for this query plan.</p>
            </div>
          )}

          {advice.notes.length > 0 && (
            <div className="notes-section">
              <h4>Analysis Notes</h4>
              <ul className="notes-list">
                {advice.notes.map((note, index) => (
                  <li key={index} className="note-item">
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="advisor-footer">
            <div className="disclaimer">
              <small>
                <strong>Note:</strong> These suggestions are based on heuristics and should be 
                validated with your specific workload and data distribution. Consider running 
                ANALYZE on affected tables after creating indexes.
              </small>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default IndexAdvisor
