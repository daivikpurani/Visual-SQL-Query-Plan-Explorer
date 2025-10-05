"""
Tests for the advisor module.
"""
import pytest
from app.core.advisor import suggest_indexes, analyze_filter_condition, analyze_join_condition
from app.schemas import PlanDoc, PlanNode, PlanSummary, PlanEdge


def test_analyze_filter_condition_equality():
    """Test index suggestion for equality filter conditions."""
    suggestions = analyze_filter_condition("city = 'New York'", "customers")
    
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion.table == "customers"
    assert suggestion.columns == ["city"]
    assert "CREATE INDEX" in suggestion.sql
    assert "customers(city)" in suggestion.sql


def test_analyze_filter_condition_multiple_equality():
    """Test index suggestion for multiple equality conditions."""
    suggestions = analyze_filter_condition("city = 'New York' AND status = 'active'", "customers")
    
    # Should suggest both single-column and composite indexes
    assert len(suggestions) >= 2
    
    # Check for composite index
    composite_suggestion = next((s for s in suggestions if len(s.columns) > 1), None)
    assert composite_suggestion is not None
    assert set(composite_suggestion.columns) == {"city", "status"}


def test_analyze_filter_condition_range():
    """Test index suggestion for range conditions."""
    suggestions = analyze_filter_condition("price BETWEEN 100 AND 500", "products")
    
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion.table == "products"
    assert suggestion.columns == ["price"]
    assert "price" in suggestion.sql


def test_analyze_filter_condition_like():
    """Test index suggestion for LIKE conditions."""
    suggestions = analyze_filter_condition("name LIKE 'iPhone%'", "products")
    
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion.table == "products"
    assert suggestion.columns == ["name"]
    assert "text_pattern_ops" in suggestion.sql


def test_analyze_join_condition():
    """Test index suggestion for join conditions."""
    suggestions = analyze_join_condition("orders.customer_id = customers.id", "orders")
    
    assert len(suggestions) == 1
    suggestion = suggestions[0]
    assert suggestion.table == "orders"
    assert suggestion.columns == ["customer_id"]
    assert "JOIN on customer_id" in suggestion.where


def test_suggest_indexes_seq_scan():
    """Test index suggestions for sequential scan nodes."""
    nodes = [
        PlanNode(
            id="1",
            depth=0,
            type="Seq Scan",
            relation="customers",
            filter="city = 'New York'",
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
            heat_score=0.8,
            warnings=[]
        )
    ]
    
    plan = PlanDoc(
        id="test-plan",
        summary=PlanSummary(totalTimeMs=100.0, totalCost=1000.0, totalRows=1000, warnings=[]),
        nodes=nodes,
        edges=[],
        critical_path=[],
        warnings=[]
    )
    
    suggestions, notes = suggest_indexes(plan)
    
    assert len(suggestions) > 0
    assert any(s.table == "customers" and "city" in s.columns for s in suggestions)
    assert len(notes) > 0
    assert any("sequential scan" in note.lower() for note in notes)


def test_suggest_indexes_join():
    """Test index suggestions for join nodes."""
    nodes = [
        PlanNode(
            id="1",
            depth=0,
            type="Hash Join",
            joinCond="orders.customer_id = customers.id",
            actualTotalTime=100.0,
            actualRows=500,
            actualLoops=1,
            actualExclusiveTime=30.0,
            costTotal=2000.0,
            costStartup=100.0,
            rowEstimate=500,
            rowErrorFactor=1.0,
            buffers={},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.6,
            warnings=[]
        ),
        PlanNode(
            id="2",
            depth=1,
            type="Seq Scan",
            relation="orders",
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
            heat_score=0.7,
            warnings=[]
        )
    ]
    
    plan = PlanDoc(
        id="test-plan",
        summary=PlanSummary(totalTimeMs=100.0, totalCost=2000.0, totalRows=500, warnings=[]),
        nodes=nodes,
        edges=[],
        critical_path=[],
        warnings=[]
    )
    
    suggestions, notes = suggest_indexes(plan)
    
    # Should suggest index on orders.customer_id for the join
    assert len(suggestions) > 0
    assert any(s.table == "orders" and "customer_id" in s.columns for s in suggestions)


def test_suggest_indexes_no_suggestions():
    """Test that no suggestions are made when not needed."""
    nodes = [
        PlanNode(
            id="1",
            depth=0,
            type="Index Scan",
            relation="customers",
            indexName="idx_customers_city",
            actualTotalTime=10.0,
            actualRows=100,
            actualLoops=1,
            actualExclusiveTime=10.0,
            costTotal=100.0,
            costStartup=10.0,
            rowEstimate=100,
            rowErrorFactor=1.0,
            buffers={},
            parallelAware=False,
            workersLaunched=0,
            heat_score=0.2,
            warnings=[]
        )
    ]
    
    plan = PlanDoc(
        id="test-plan",
        summary=PlanSummary(totalTimeMs=10.0, totalCost=100.0, totalRows=100, warnings=[]),
        nodes=nodes,
        edges=[],
        critical_path=[],
        warnings=[]
    )
    
    suggestions, notes = suggest_indexes(plan)
    
    # Should have minimal suggestions since it's already using an index
    assert len(suggestions) == 0 or len(suggestions) < 3
