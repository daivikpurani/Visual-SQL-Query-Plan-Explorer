"""
Tests for the normalize module.
"""
import pytest
from app.core.normalize import normalize_plan


def test_normalize_simple_seq_scan():
    """Test normalization of a simple sequential scan plan."""
    raw_json = [
        {
            "Plan": {
                "Node Type": "Seq Scan",
                "Relation Name": "customers",
                "Startup Cost": 0.00,
                "Total Cost": 1000.00,
                "Plan Rows": 1000,
                "Plan Width": 200,
                "Actual Startup Time": 0.000,
                "Actual Total Time": 50.000,
                "Actual Rows": 1000,
                "Actual Loops": 1,
                "Buffers": {
                    "Shared Hit Blocks": 0,
                    "Shared Read Blocks": 100,
                    "Temp Read Blocks": 0,
                    "Temp Written Blocks": 0
                }
            },
            "Planning Time": 0.100,
            "Execution Time": 50.100
        }
    ]
    
    nodes, edges, summary = normalize_plan(raw_json)
    
    assert len(nodes) == 1
    assert len(edges) == 0
    
    node = nodes[0]
    assert node.type == "Seq Scan"
    assert node.relation == "customers"
    assert node.actualTotalTime == 50.0
    assert node.actualRows == 1000
    assert node.actualExclusiveTime == 50.0
    assert node.buffers["sharedRead"] == 100
    
    assert summary.totalTimeMs == 50.0
    assert summary.totalCost == 1000.0
    assert summary.totalRows == 1000


def test_normalize_join_plan():
    """Test normalization of a join plan."""
    raw_json = [
        {
            "Plan": {
                "Node Type": "Hash Join",
                "Join Type": "Inner",
                "Startup Cost": 100.00,
                "Total Cost": 2000.00,
                "Plan Rows": 500,
                "Plan Width": 300,
                "Actual Startup Time": 10.000,
                "Actual Total Time": 100.000,
                "Actual Rows": 500,
                "Actual Loops": 1,
                "Hash Cond": "(o.customer_id = c.id)",
                "Plans": [
                    {
                        "Node Type": "Seq Scan",
                        "Relation Name": "customers",
                        "Startup Cost": 0.00,
                        "Total Cost": 500.00,
                        "Plan Rows": 1000,
                        "Plan Width": 200,
                        "Actual Startup Time": 0.000,
                        "Actual Total Time": 30.000,
                        "Actual Rows": 1000,
                        "Actual Loops": 1,
                        "Buffers": {
                            "Shared Hit Blocks": 0,
                            "Shared Read Blocks": 50,
                            "Temp Read Blocks": 0,
                            "Temp Written Blocks": 0
                        }
                    },
                    {
                        "Node Type": "Seq Scan",
                        "Relation Name": "orders",
                        "Startup Cost": 0.00,
                        "Total Cost": 1000.00,
                        "Plan Rows": 2000,
                        "Plan Width": 100,
                        "Actual Startup Time": 0.000,
                        "Actual Total Time": 40.000,
                        "Actual Rows": 2000,
                        "Actual Loops": 1,
                        "Buffers": {
                            "Shared Hit Blocks": 0,
                            "Shared Read Blocks": 80,
                            "Temp Read Blocks": 0,
                            "Temp Written Blocks": 0
                        }
                    }
                ]
            },
            "Planning Time": 0.200,
            "Execution Time": 100.200
        }
    ]
    
    nodes, edges, summary = normalize_plan(raw_json)
    
    assert len(nodes) == 3  # Hash Join + 2 Seq Scans
    assert len(edges) == 2  # 2 edges from join to children
    
    # Find the join node
    join_node = next(node for node in nodes if node.type == "Hash Join")
    assert join_node.actualTotalTime == 100.0
    assert join_node.actualExclusiveTime == 30.0  # 100 - (30 + 40)
    assert join_node.joinCond == "(o.customer_id = c.id)"
    
    # Check that children have correct parent relationships
    child_nodes = [node for node in nodes if node.parentId == join_node.id]
    assert len(child_nodes) == 2
    
    assert summary.totalTimeMs == 100.0
    assert summary.totalCost == 2000.0
    assert summary.totalRows == 500


def test_row_error_factor_calculation():
    """Test row error factor calculation."""
    raw_json = [
        {
            "Plan": {
                "Node Type": "Seq Scan",
                "Relation Name": "customers",
                "Startup Cost": 0.00,
                "Total Cost": 1000.00,
                "Plan Rows": 100,  # Estimated
                "Plan Width": 200,
                "Actual Startup Time": 0.000,
                "Actual Total Time": 50.000,
                "Actual Rows": 1000,  # Actual (10x higher)
                "Actual Loops": 1,
                "Buffers": {
                    "Shared Hit Blocks": 0,
                    "Shared Read Blocks": 100,
                    "Temp Read Blocks": 0,
                    "Temp Written Blocks": 0
                }
            },
            "Planning Time": 0.100,
            "Execution Time": 50.100
        }
    ]
    
    nodes, edges, summary = normalize_plan(raw_json)
    
    node = nodes[0]
    assert node.rowEstimate == 100
    assert node.actualRows == 1000
    assert node.rowErrorFactor == 10.0  # 1000 / 100
    
    # Should have a warning about high row error factor
    assert len(node.warnings) > 0
    assert any("row estimate error" in warning.lower() for warning in node.warnings)
