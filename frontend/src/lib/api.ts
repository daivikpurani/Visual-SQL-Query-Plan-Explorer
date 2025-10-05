import axios from 'axios'

// Define types locally to avoid circular imports
export interface PlanDoc {
  id: string
  summary: {
    totalTimeMs: number
    totalCost: number
    totalRows: number
    warnings: string[]
  }
  nodes: PlanNode[]
  edges: PlanEdge[]
  critical_path: string[]
  warnings: string[]
}

export interface PlanNode {
  id: string
  parentId?: string
  depth: number
  type: string
  relation?: string
  indexName?: string
  filter?: string
  joinCond?: string
  actualTotalTime: number
  actualRows: number
  actualLoops: number
  actualExclusiveTime: number
  costTotal: number
  costStartup: number
  rowEstimate: number
  rowErrorFactor: number
  buffers: {
    sharedHit: number
    sharedRead: number
    tempRead: number
    tempWritten: number
  }
  parallelAware: boolean
  workersLaunched: number
  heat_score: number
  warnings: string[]
}

export interface PlanEdge {
  source: string
  target: string
  label?: string
}

export interface IndexSuggestion {
  table: string
  columns: string[]
  where?: string
  sql: string
}

export interface Advice {
  indexes: IndexSuggestion[]
  notes: string[]
}

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const parsePlan = async (rawExplainJson: any): Promise<PlanDoc> => {
  const response = await api.post('/plans/parse', {
    rawExplainJson
  })
  return response.data
}

export const comparePlans = async (left: any, right: any): Promise<any> => {
  const response = await api.post('/plans/compare', {
    left,
    right
  })
  return response.data
}

export const getAdvice = async (plan: PlanDoc): Promise<Advice> => {
  const response = await api.post('/advise', {
    plan
  })
  return response.data
}

export const getPlan = async (planId: string): Promise<PlanDoc> => {
  const response = await api.get(`/plans/${planId}`)
  return response.data
}
