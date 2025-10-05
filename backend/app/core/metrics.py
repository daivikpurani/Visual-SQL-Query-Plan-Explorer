"""
Core metrics computation for query plan analysis.
"""
import statistics
from typing import List, Dict, Any, Tuple
from app.schemas import PlanNode


def compute_critical_path(nodes: List[PlanNode]) -> List[str]:
    """
    Compute the critical path through the query plan.
    
    The critical path is the sequence of nodes that maximizes the sum of exclusive times.
    This represents the bottleneck in query execution.
    
    Args:
        nodes: List of plan nodes
        
    Returns:
        List of node IDs representing the critical path
    """
    if not nodes:
        return []
    
    # Build adjacency list
    children = {}
    parents = {}
    for node in nodes:
        children[node.id] = []
        if node.parentId:
            children[node.parentId].append(node.id)
            parents[node.id] = node.parentId
    
    # Find root node
    root = None
    for node in nodes:
        if node.parentId is None:
            root = node
            break
    
    if not root:
        return []
    
    # Use dynamic programming to find critical path
    memo = {}
    
    def critical_path_from(node_id: str) -> Tuple[List[str], float]:
        """Find critical path starting from given node."""
        if node_id in memo:
            return memo[node_id]
        
        node = next((n for n in nodes if n.id == node_id), None)
        if not node:
            return [], 0.0
        
        # Base case: leaf node
        if not children[node_id]:
            memo[node_id] = ([node_id], node.actualExclusiveTime)
            return memo[node_id]
        
        # Find best child path
        best_path = []
        best_time = 0.0
        
        for child_id in children[node_id]:
            child_path, child_time = critical_path_from(child_id)
            if child_time > best_time:
                best_path = child_path
                best_time = child_time
        
        # Include this node in the path
        total_time = node.actualExclusiveTime + best_time
        memo[node_id] = ([node_id] + best_path, total_time)
        
        return memo[node_id]
    
    path, _ = critical_path_from(root.id)
    return path


def heat_score(node: PlanNode, all_nodes: List[PlanNode]) -> float:
    """
    Compute heat score for a node based on multiple metrics.
    
    Heat score combines z-scores of:
    - Exclusive time (60% weight)
    - Shared read blocks (25% weight) 
    - Row error factor (15% weight)
    
    Args:
        node: The node to score
        all_nodes: All nodes in the plan for normalization
        
    Returns:
        Heat score (higher = more problematic)
    """
    if not all_nodes:
        return 0.0
    
    # Extract metrics
    exclusive_times = [n.actualExclusiveTime for n in all_nodes]
    shared_reads = [n.buffers.get("sharedRead", 0) for n in all_nodes]
    row_errors = [n.rowErrorFactor for n in all_nodes]
    
    # Calculate z-scores
    def z_score(value: float, values: List[float]) -> float:
        if not values or len(values) < 2:
            return 0.0
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values) if len(values) > 1 else 0.0
        if std_val == 0:
            return 0.0
        return (value - mean_val) / std_val
    
    time_z = z_score(node.actualExclusiveTime, exclusive_times)
    read_z = z_score(node.buffers.get("sharedRead", 0), shared_reads)
    error_z = z_score(node.rowErrorFactor, row_errors)
    
    # Weighted combination
    heat_score = (0.6 * time_z) + (0.25 * read_z) + (0.15 * error_z)
    
    # Normalize to 0-1 range
    return max(0.0, min(1.0, (heat_score + 3) / 6))  # Assume z-scores roughly in [-3, 3]


def plan_summary(nodes: List[PlanNode]) -> Dict[str, Any]:
    """
    Generate a summary of the query plan with key metrics and top offenders.
    
    Args:
        nodes: List of plan nodes
        
    Returns:
        Dictionary with summary statistics
    """
    if not nodes:
        return {
            "totalTimeMs": 0.0,
            "totalCost": 0.0,
            "totalRows": 0,
            "topOffenders": [],
            "warnings": []
        }
    
    # Calculate totals
    total_time = sum(node.actualTotalTime for node in nodes)
    total_cost = sum(node.costTotal for node in nodes)
    total_rows = sum(node.actualRows for node in nodes)
    
    # Find top offenders by heat score
    sorted_nodes = sorted(nodes, key=lambda n: n.heat_score, reverse=True)
    top_offenders = []
    
    for node in sorted_nodes[:5]:  # Top 5 offenders
        if node.heat_score > 0.3:  # Only include significant offenders
            top_offenders.append({
                "id": node.id,
                "type": node.type,
                "relation": node.relation,
                "heatScore": node.heat_score,
                "exclusiveTime": node.actualExclusiveTime,
                "sharedRead": node.buffers.get("sharedRead", 0),
                "rowErrorFactor": node.rowErrorFactor
            })
    
    # Collect all warnings
    all_warnings = []
    for node in nodes:
        all_warnings.extend(node.warnings)
    
    return {
        "totalTimeMs": total_time,
        "totalCost": total_cost,
        "totalRows": total_rows,
        "topOffenders": top_offenders,
        "warnings": list(set(all_warnings))  # Remove duplicates
    }
