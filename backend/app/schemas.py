"""
Pydantic models for the Visual SQL Plan Explorer API.
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from uuid import UUID


class PlanNode(BaseModel):
    """A single node in the query plan tree."""
    id: str
    parentId: Optional[str] = None
    depth: int
    type: str  # Seq Scan, Index Scan, Hash Join, etc.
    relation: Optional[str] = None  # table name
    indexName: Optional[str] = None
    filter: Optional[str] = None
    joinCond: Optional[str] = None
    
    # Timing metrics
    actualTotalTime: float = 0.0
    actualRows: int = 0
    actualLoops: int = 1
    actualExclusiveTime: float = 0.0
    
    # Cost metrics
    costTotal: float = 0.0
    costStartup: float = 0.0
    rowEstimate: int = 0
    rowErrorFactor: float = 1.0
    
    # Buffer metrics
    buffers: Dict[str, int] = Field(default_factory=dict)
    
    # Parallel execution
    parallelAware: bool = False
    workersLaunched: int = 0
    
    # Computed metrics
    heat_score: float = 0.0
    
    # Warnings
    warnings: List[str] = Field(default_factory=list)


class PlanEdge(BaseModel):
    """An edge connecting two nodes in the plan tree."""
    source: str
    target: str
    label: Optional[str] = None


class PlanSummary(BaseModel):
    """Summary statistics for a query plan."""
    totalTimeMs: float = 0.0
    totalCost: float = 0.0
    totalRows: int = 0
    warnings: List[str] = Field(default_factory=list)


class PlanDoc(BaseModel):
    """Complete plan document with nodes, edges, and metadata."""
    id: str
    summary: PlanSummary
    nodes: List[PlanNode]
    edges: List[PlanEdge]
    critical_path: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class PlanParseRequest(BaseModel):
    """Request to parse a PostgreSQL EXPLAIN JSON."""
    rawExplainJson: Dict[str, Any]


class PlanCompareRequest(BaseModel):
    """Request to compare two query plans."""
    left: Dict[str, Any]
    right: Dict[str, Any]


class IndexSuggestion(BaseModel):
    """An index suggestion."""
    table: str
    columns: List[str]
    where: Optional[str] = None
    sql: str


class AdviseRequest(BaseModel):
    """Request for index advice."""
    plan: PlanDoc
    schemaStats: Optional[Dict[str, Any]] = None


class Advice(BaseModel):
    """Index advice response."""
    indexes: List[IndexSuggestion]
    notes: List[str] = Field(default_factory=list)


class CompareDoc(BaseModel):
    """Comparison result between two plans."""
    left: PlanDoc
    right: PlanDoc
    deltas: Dict[str, float]
    diffAnnotations: List[str] = Field(default_factory=list)
