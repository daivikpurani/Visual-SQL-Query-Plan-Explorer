"""
Tests for the metrics module.
"""
import pytest
from app.core.metrics import compute_critical_path, heat_score, plan_summary
from app.schemas import PlanNode


def test_compute_critical_path_single_node():
    """Test critical path computation with a single node."""
    nodes = [
        PlanNode(
            id="1",
            depth=0,
            type="Seq Scan",
            actualTotalTime=100.0,
            actualRows=1000,
            actualLoops=1,
            actualExclusiveTime=100.0,
            costTotal=1000.0,
            costStartup=0.0,
            rowEstimate=1000,
            rowErrorFactor=1.0,
            buffers={},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.0,
            warnings=[]
        )
    ]
    
    critical_path = compute_critical_path(nodes)
    assert critical_path == ["1"]


def test_compute_critical_path_join():
    """Test critical path computation with a join."""
    nodes = [
        PlanNode(
            id="1",
            parentId=None,
            depth=0,
            type="Hash Join",
            actualTotalTime=100.0,
            actualRows=500,
            actualLoops=1,
            actualExclusiveTime=30.0,  # 100 - (40 + 30)
            costTotal=2000.0,
            costStartup=100.0,
            rowEstimate=500,
            rowErrorFactor=1.0,
            buffers={},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.0,
            warnings=[]
        ),
        PlanNode(
            id="2",
            parentId="1",
            depth=1,
            type="Seq Scan",
            actualTotalTime=40.0,
            actualRows=1000,
            actualLoops=1,
            actualExclusiveTime=40.0,
            costTotal=500.0,
            costStartup=0.0,
            rowEstimate=1000,
            rowErrorFactor=1.0,
            buffers={},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.0,
            warnings=[]
        ),
        PlanNode(
            id="3",
            parentId="1",
            depth=1,
            type="Seq Scan",
            actualTotalTime=30.0,
            actualRows=2000,
            actualLoops=1,
            actualExclusiveTime=30.0,
            costTotal=1000.0,
            costStartup=0.0,
            rowEstimate=2000,
            rowErrorFactor=1.0,
            buffers={},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.0,
            warnings=[]
        )
    ]
    
    critical_path = compute_critical_path(nodes)
    # Should include the join node and the slower child (node 2 with 40ms)
    assert "1" in critical_path
    assert "2" in critical_path
    assert "3" not in critical_path


def test_heat_score_calculation():
    """Test heat score calculation."""
    # Create nodes with different characteristics
    nodes = [
        PlanNode(
            id="1",
            depth=0,
            type="Seq Scan",
            actualTotalTime=100.0,
            actualRows=1000,
            actualLoops=1,
            actualExclusiveTime=100.0,  # High exclusive time
            costTotal=1000.0,
            costStartup=0.0,
            rowEstimate=1000,
            rowErrorFactor=1.0,
            buffers={"sharedRead": 1000},  # High shared read
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.0,
            warnings=[]
        ),
        PlanNode(
            id="2",
            depth=0,
            type="Index Scan",
            actualTotalTime=10.0,
            actualRows=100,
            actualLoops=1,
            actualExclusiveTime=10.0,  # Low exclusive time
            costTotal=100.0,
            costStartup=10.0,
            rowEstimate=100,
            rowErrorFactor=1.0,
            buffers={"sharedRead": 10},  # Low shared read
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.0,
            warnings=[]
        )
    ]
    
    # Calculate heat scores
    for node in nodes:
        node.heat_score = heat_score(node, nodes)
    
    # Node 1 should have higher heat score due to higher exclusive time and shared read
    assert nodes[0].heat_score > nodes[1].heat_score
    assert nodes[0].heat_score > 0.5  # Should be high
    assert nodes[1].heat_score < 0.5   # Should be low


def test_plan_summary():
    """Test plan summary generation."""
    nodes = [
        PlanNode(
            id="1",
            depth=0,
            type="Seq Scan",
            actualTotalTime=100.0,
            actualRows=1000,
            actualLoops=1,
            actualExclusiveTime=100.0,
            costTotal=1000.0,
            costStartup=0.0,
            rowEstimate=1000,
            rowErrorFactor=2.0,  # High error factor
            buffers={"sharedRead": 1000},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.8,  # High heat score
            warnings=["High shared read"]
        ),
        PlanNode(
            id="2",
            depth=0,
            type="Index Scan",
            actualTotalTime=10.0,
            actualRows=100,
            actualLoops=1,
            actualExclusiveTime=10.0,
            costTotal=100.0,
            costStartup=10.0,
            rowEstimate=100,
            rowErrorFactor=1.0,
            buffers={"sharedRead": 10},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.2,  # Low heat score
            warnings=[]
        )
    ]
    
    summary = plan_summary(nodes)
    
    assert summary["totalTimeMs"] == 110.0  # 100 + 10
    assert summary["totalCost"] == 1100.0   # 1000 + 100
    assert summary["totalRows"] == 1100     # 1000 + 100
    
    # Should have top offenders
    assert len(summary["topOffenders"]) > 0
    top_offender = summary["topOffenders"][0]
    assert top_offender["id"] == "1"  # Node with highest heat score
    assert top_offender["heatScore"] == 0.8
    
    # Should have warnings
    assert len(summary["warnings"]) > 0
    assert "High shared read" in summary["warnings"]
