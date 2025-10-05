"""
FastAPI application for Visual SQL Plan Explorer.
"""
import uuid
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.core.normalize import normalize_plan
from app.core.metrics import compute_critical_path, heat_score, plan_summary
from app.core.advisor import suggest_indexes
from app.schemas import PlanDoc, CompareDoc, Advice, PlanParseRequest, PlanCompareRequest, AdviseRequest

app = FastAPI(
    title="Visual SQL Plan Explorer",
    description="API for parsing, analyzing, and visualizing PostgreSQL query plans",
    version="0.1.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo purposes
plan_cache: Dict[str, PlanDoc] = {}


@app.post("/plans/parse", response_model=PlanDoc)
async def parse_plan(request: PlanParseRequest) -> PlanDoc:
    """
    Parse a PostgreSQL EXPLAIN JSON plan into normalized format.
    """
    try:
        # Normalize the plan
        nodes, edges, summary = normalize_plan(request.rawExplainJson)
        
        # Compute metrics
        critical_path = compute_critical_path(nodes)
        for node in nodes:
            node.heat_score = heat_score(node, nodes)
        
        # Generate plan document
        plan_id = str(uuid.uuid4())
        plan_doc = PlanDoc(
            id=plan_id,
            summary=summary,
            nodes=nodes,
            edges=edges,
            critical_path=critical_path,
            warnings=summary.warnings
        )
        
        # Cache for demo
        plan_cache[plan_id] = plan_doc
        
        return plan_doc
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse plan: {str(e)}")


@app.post("/plans/compare", response_model=CompareDoc)
async def compare_plans(request: PlanCompareRequest) -> CompareDoc:
    """
    Compare two query plans and compute deltas.
    """
    try:
        # Parse both plans
        left_nodes, left_edges, left_summary = normalize_plan(request.left)
        right_nodes, right_edges, right_summary = normalize_plan(request.right)
        
        # Compute metrics for both
        left_critical_path = compute_critical_path(left_nodes)
        right_critical_path = compute_critical_path(right_nodes)
        
        for node in left_nodes:
            node.heat_score = heat_score(node, left_nodes)
        for node in right_nodes:
            node.heat_score = heat_score(node, right_nodes)
        
        # Create plan documents
        left_plan = PlanDoc(
            id=str(uuid.uuid4()),
            summary=left_summary,
            nodes=left_nodes,
            edges=left_edges,
            critical_path=left_critical_path,
            warnings=left_summary.warnings
        )
        
        right_plan = PlanDoc(
            id=str(uuid.uuid4()),
            summary=right_summary,
            nodes=right_nodes,
            edges=right_edges,
            critical_path=right_critical_path,
            warnings=right_summary.warnings
        )
        
        # Compute deltas
        left_time = left_summary.totalTimeMs
        right_time = right_summary.totalTimeMs
        time_pct = ((right_time - left_time) / max(left_time, 1)) * 100 if left_time > 0 else 0
        
        left_rows = left_summary.totalRows
        right_rows = right_summary.totalRows
        rows_mismatch = abs(right_rows - left_rows) / max(left_rows, 1) * 100 if left_rows > 0 else 0
        
        left_cost = left_summary.totalCost
        right_cost = right_summary.totalCost
        cost_pct = ((right_cost - left_cost) / max(left_cost, 1)) * 100 if left_cost > 0 else 0
        
        # Generate diff annotations (simplified)
        diff_annotations = []
        if abs(time_pct) > 10:
            diff_annotations.append(f"Execution time changed by {time_pct:.1f}%")
        if rows_mismatch > 10:
            diff_annotations.append(f"Row count mismatch: {rows_mismatch:.1f}%")
        if abs(cost_pct) > 10:
            diff_annotations.append(f"Cost changed by {cost_pct:.1f}%")
        
        return CompareDoc(
            left=left_plan,
            right=right_plan,
            deltas={
                "timePct": time_pct,
                "rowsMismatch": rows_mismatch,
                "costPct": cost_pct
            },
            diffAnnotations=diff_annotations
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to compare plans: {str(e)}")


@app.post("/advise", response_model=Advice)
async def advise_plan(request: AdviseRequest) -> Advice:
    """
    Generate index suggestions for a query plan.
    """
    try:
        indexes, notes = suggest_indexes(request.plan, request.schemaStats)
        return Advice(indexes=indexes, notes=notes)
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate advice: {str(e)}")


@app.get("/plans/{plan_id}", response_model=PlanDoc)
async def get_plan(plan_id: str) -> PlanDoc:
    """
    Retrieve a cached plan by ID (for demo purposes).
    """
    if plan_id not in plan_cache:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan_cache[plan_id]


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
