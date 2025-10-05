import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { PlanDoc } from '../lib/api'
import { parsePlan } from '../lib/api'

interface UploadBoxProps {
  onPlanParsed: (plan: PlanDoc) => void
}

const UploadBox: React.FC<UploadBoxProps> = ({ onPlanParsed }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [jsonInput, setJsonInput] = useState('')

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    setIsLoading(true)
    setError(null)

    try {
      const text = await file.text()
      const jsonData = JSON.parse(text)
      const plan = await parsePlan(jsonData)
      onPlanParsed(plan)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse file')
    } finally {
      setIsLoading(false)
    }
  }, [onPlanParsed])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/json': ['.json']
    },
    multiple: false
  })

  const handleJsonSubmit = async () => {
    if (!jsonInput.trim()) return

    setIsLoading(true)
    setError(null)

    try {
      const jsonData = JSON.parse(jsonInput)
      const plan = await parsePlan(jsonData)
      onPlanParsed(plan)
      setJsonInput('')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to parse JSON')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="upload-box">
      <h2>Upload Query Plan</h2>
      
      <div className="upload-methods">
        <div 
          {...getRootProps()} 
          className={`dropzone ${isDragActive ? 'active' : ''}`}
        >
          <input {...getInputProps()} />
          <div className="dropzone-content">
            {isDragActive ? (
              <p>Drop the JSON file here...</p>
            ) : (
              <div>
                <p>Drag & drop a PostgreSQL EXPLAIN JSON file here</p>
                <p>or click to select a file</p>
              </div>
            )}
          </div>
        </div>

        <div className="divider">OR</div>

        <div className="json-input">
          <h3>Paste JSON directly:</h3>
          <textarea
            value={jsonInput}
            onChange={(e) => setJsonInput(e.target.value)}
            placeholder="Paste your PostgreSQL EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) output here..."
            rows={8}
          />
          <button 
            onClick={handleJsonSubmit}
            disabled={isLoading || !jsonInput.trim()}
          >
            {isLoading ? 'Parsing...' : 'Parse Plan'}
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      <div className="help-text">
        <h4>How to get a query plan:</h4>
        <pre>
{`-- In PostgreSQL:
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) 
SELECT * FROM your_table WHERE condition;

-- Copy the JSON output and paste it above`}
        </pre>
      </div>
    </div>
  )
}

export default UploadBox
