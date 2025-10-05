"""
Core normalization logic for PostgreSQL EXPLAIN JSON plans.
"""
import uuid
import re
from typing import List, Dict, Any, Tuple, Optional
from app.schemas import PlanNode, PlanEdge, PlanSummary


def normalize_plan(raw_json: Dict[str, Any]) -> Tuple[List[PlanNode], List[PlanEdge], PlanSummary]:
    """
    Normalize a PostgreSQL EXPLAIN JSON plan into our internal format.
    
    Args:
        raw_json: The raw PostgreSQL EXPLAIN JSON (array format)
        
    Returns:
        Tuple of (nodes, edges, summary)
    """
    # Handle both array format and single plan format
    if isinstance(raw_json, list) and len(raw_json) > 0:
        plan_data = raw_json[0]
    else:
        plan_data = raw_json
    
    # Extract the actual plan
    plan = plan_data.get("Plan", {})
    
    nodes = []
    edges = []
    node_counter = 0
    
    # Recursively process the plan tree
    def process_node(node_data: Dict[str, Any], parent_id: Optional[str] = None, depth: int = 0) -> str:
        nonlocal node_counter
        node_id = str(uuid.uuid4())
        
        # Extract basic node information
        node_type = node_data.get("Node Type", "Unknown")
        relation = node_data.get("Relation Name")
        index_name = node_data.get("Index Name")
        
        # Extract timing information
        actual_total_time = node_data.get("Actual Total Time", 0.0)
        actual_rows = node_data.get("Actual Rows", 0)
        actual_loops = node_data.get("Actual Loops", 1)
        
        # Extract cost information
        total_cost = node_data.get("Total Cost", 0.0)
        startup_cost = node_data.get("Startup Cost", 0.0)
        rows_estimate = node_data.get("Plan Rows", 0)
        
        # Calculate row error factor
        row_error_factor = 1.0
        if rows_estimate > 0 and actual_rows > 0:
            row_error_factor = max(actual_rows, 1) / max(rows_estimate, 1)
        
        # Extract buffer information
        buffers = {}
        if "Buffers" in node_data:
            buf_data = node_data["Buffers"]
            buffers = {
                "sharedHit": buf_data.get("Shared Hit Blocks", 0),
                "sharedRead": buf_data.get("Shared Read Blocks", 0),
                "tempRead": buf_data.get("Temp Read Blocks", 0),
                "tempWritten": buf_data.get("Temp Written Blocks", 0),
            }
        
        # Extract parallel execution info
        parallel_aware = node_data.get("Parallel Aware", False)
        workers_launched = node_data.get("Workers Launched", 0)
        
        # Extract filter and join conditions
        filter_condition = node_data.get("Filter")
        join_condition = node_data.get("Join Filter") or node_data.get("Hash Cond") or node_data.get("Merge Cond")
        
        # Calculate exclusive time (will be updated after processing children)
        exclusive_time = actual_total_time
        
        # Create the node
        node = PlanNode(
            id=node_id,
            parentId=parent_id,
            depth=depth,
            type=node_type,
            relation=relation,
            indexName=index_name,
            filter=filter_condition,
            joinCond=join_condition,
            actualTotalTime=actual_total_time,
            actualRows=actual_rows,
            actualLoops=actual_loops,
            actualExclusiveTime=exclusive_time,
            costTotal=total_cost,
            costStartup=startup_cost,
            rowEstimate=rows_estimate,
            rowErrorFactor=row_error_factor,
            buffers=buffers,
            parallelAware=parallel_aware,
            workersLaunched=workers_launched,
        )
        
        # Add warnings
        warnings = []
        if row_error_factor > 4:
            warnings.append(f"High row estimate error: {row_error_factor:.1f}x")
        if buffers.get("sharedRead", 0) > 1000:
            warnings.append(f"High shared read: {buffers['sharedRead']} blocks")
        if buffers.get("tempWritten", 0) > 100:
            warnings.append(f"Large temp files: {buffers['tempWritten']} blocks")
        
        node.warnings = warnings
        nodes.append(node)
        
        # Process children
        children = node_data.get("Plans", [])
        for child_data in children:
            child_id = process_node(child_data, node_id, depth + 1)
            edges.append(PlanEdge(source=node_id, target=child_id))
        
        return node_id
    
    # Process the root node
    root_id = process_node(plan)
    
    # Calculate exclusive times (time spent in this node minus children)
    for node in nodes:
        children_time = 0.0
        for edge in edges:
            if edge.source == node.id:
                child_node = next((n for n in nodes if n.id == edge.target), None)
                if child_node:
                    # Adjust for loops
                    children_time += (child_node.actualTotalTime / max(child_node.actualLoops, 1)) * node.actualLoops
        
        node.actualExclusiveTime = max(0.0, node.actualTotalTime - children_time)
    
    # Calculate summary statistics
    # Use root node's time (the total execution time)
    root_node = next((node for node in nodes if node.parentId is None), None)
    total_time = root_node.actualTotalTime if root_node else sum(node.actualTotalTime for node in nodes)
    total_cost = root_node.costTotal if root_node else sum(node.costTotal for node in nodes)
    total_rows = root_node.actualRows if root_node else sum(node.actualRows for node in nodes)
    
    all_warnings = []
    for node in nodes:
        all_warnings.extend(node.warnings)
    
    summary = PlanSummary(
        totalTimeMs=total_time,
        totalCost=total_cost,
        totalRows=total_rows,
        warnings=list(set(all_warnings))  # Remove duplicates
    )
    
    return nodes, edges, summary
