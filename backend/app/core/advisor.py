"""
Index advisor for suggesting missing indexes based on query plans.
"""
import re
from typing import List, Dict, Any, Optional, Tuple
from app.schemas import PlanDoc, IndexSuggestion


def suggest_indexes(plan: PlanDoc, schema_stats: Optional[Dict[str, Any]] = None) -> Tuple[List[IndexSuggestion], List[str]]:
    """
    Suggest indexes based on query plan analysis.
    
    Args:
        plan: The parsed query plan
        schema_stats: Optional schema statistics (not used in current implementation)
        
    Returns:
        Tuple of (index_suggestions, notes)
    """
    suggestions = []
    notes = []
    
    # Analyze each node for index opportunities
    for node in plan.nodes:
        node_suggestions, node_notes = analyze_node(node, plan.nodes)
        suggestions.extend(node_suggestions)
        notes.extend(node_notes)
    
    # Remove duplicate suggestions
    unique_suggestions = []
    seen = set()
    for suggestion in suggestions:
        key = (suggestion.table, tuple(suggestion.columns))
        if key not in seen:
            unique_suggestions.append(suggestion)
            seen.add(key)
    
    return unique_suggestions, notes


def analyze_node(node, all_nodes: List) -> Tuple[List[IndexSuggestion], List[str]]:
    """
    Analyze a single node for index opportunities.
    
    Args:
        node: The plan node to analyze
        all_nodes: All nodes in the plan
        
    Returns:
        Tuple of (suggestions, notes)
    """
    suggestions = []
    notes = []
    
    # Handle different node types
    table = node.relation
    
    # 1. Sequential scan with filters
    if node.type == "Seq Scan" and node.filter and table:
        filter_suggestions = analyze_filter_condition(node.filter, table)
        suggestions.extend(filter_suggestions)
    
    # 2. Sort operations
    if node.type == "Sort":
        sort_suggestions = analyze_sort_node(node, all_nodes)
        suggestions.extend(sort_suggestions)
    
    # 3. Join conditions (don't require relation field)
    if node.type in ["Hash Join", "Merge Join", "Nested Loop"] and node.joinCond:
        # For join nodes, we need to analyze the join condition and suggest indexes
        # on the tables involved in the join
        join_suggestions = analyze_join_condition(node.joinCond, table)
        suggestions.extend(join_suggestions)
    
    # 4. Index scan opportunities (missing indexes)
    if node.type == "Seq Scan" and node.heat_score > 0.5:
        notes.append(f"High-cost sequential scan on {table} - consider adding indexes")
    
    return suggestions, notes


def analyze_filter_condition(filter_condition: str, table: str) -> List[IndexSuggestion]:
    """
    Analyze filter conditions to suggest indexes.
    
    Args:
        filter_condition: The filter condition string
        table: The table name
        
    Returns:
        List of index suggestions
    """
    suggestions = []
    
    # Extract column names and operators
    # Pattern for equality conditions: column = value
    equality_pattern = r'(\w+)\s*=\s*[\'"][^\'"]*[\'"]'
    equality_matches = re.findall(equality_pattern, filter_condition)
    
    # Pattern for range conditions: column BETWEEN/</>/<=/>= value
    range_pattern = r'(\w+)\s*(?:BETWEEN|<=|>=|<|>)\s*[\'"][^\'"]*[\'"]'
    range_matches = re.findall(range_pattern, filter_condition)
    
    # Also handle numeric range conditions
    range_pattern_numeric = r'(\w+)\s*(?:BETWEEN|<=|>=|<|>)\s*\d+'
    range_matches.extend(re.findall(range_pattern_numeric, filter_condition))
    
    # Pattern for LIKE conditions: column LIKE 'prefix%'
    like_pattern = r'(\w+)\s+LIKE\s+[\'"]([^\'"]*%[^\'"]*)[\'"]'
    like_matches = re.findall(like_pattern, filter_condition)
    
    # Suggest composite index for multiple equality conditions
    if len(equality_matches) > 1:
        columns = list(set(equality_matches))
        if len(columns) > 1:
            index_name = f"idx_{table}_{'_'.join(columns[:3])}"  # Limit to 3 columns
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({', '.join(columns)})"
            suggestions.append(IndexSuggestion(
                table=table,
                columns=columns,
                where=filter_condition,
                sql=sql
            ))
    
    # Suggest single-column indexes for individual conditions
    for column in equality_matches:
        index_name = f"idx_{table}_{column}"
        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})"
        suggestions.append(IndexSuggestion(
            table=table,
            columns=[column],
            where=f"{column} = ?",
            sql=sql
        ))
    
    # Suggest indexes for range conditions
    for column in range_matches:
        index_name = f"idx_{table}_{column}_range"
        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column})"
        suggestions.append(IndexSuggestion(
            table=table,
            columns=[column],
            where=f"{column} BETWEEN ? AND ?",
            sql=sql
        ))
    
    # Suggest text pattern indexes for LIKE conditions
    for column, pattern in like_matches:
        if pattern.endswith('%'):
            index_name = f"idx_{table}_{column}_text"
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}({column} text_pattern_ops)"
            suggestions.append(IndexSuggestion(
                table=table,
                columns=[column],
                where=f"{column} LIKE '{pattern}'",
                sql=sql
            ))
    
    return suggestions


def analyze_sort_node(sort_node, all_nodes: List) -> List[IndexSuggestion]:
    """
    Analyze sort nodes to suggest indexes for ORDER BY optimization.
    
    Args:
        sort_node: The sort node
        all_nodes: All nodes in the plan
        
    Returns:
        List of index suggestions
    """
    suggestions = []
    
    # Look for LIMIT node that follows this sort
    limit_node = None
    for node in all_nodes:
        if node.parentId == sort_node.id and node.type == "Limit":
            limit_node = node
            break
    
    # Extract sort keys from sort node (this would need to be parsed from the plan)
    # For now, we'll make a generic suggestion
    if limit_node and sort_node.relation:
        table = sort_node.relation
        # In a real implementation, we'd parse the sort keys from the plan
        # For demo purposes, we'll suggest a generic sort index
        index_name = f"idx_{table}_sort"
        sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}(/* add sort columns here */)"
        suggestions.append(IndexSuggestion(
            table=table,
            columns=["/* sort columns */"],
            where="ORDER BY optimization",
            sql=sql
        ))
    
    return suggestions


def analyze_join_condition(join_condition: str, table: str = None) -> List[IndexSuggestion]:
    """
    Analyze join conditions to suggest indexes.
    
    Args:
        join_condition: The join condition string
        table: Optional table name to filter suggestions
        
    Returns:
        List of index suggestions
    """
    suggestions = []
    
    # Pattern for join conditions: table.column = other_table.column
    join_pattern = r'(\w+)\.(\w+)\s*=\s*\w+\.\w+'
    join_matches = re.findall(join_pattern, join_condition)
    
    for table_name, column in join_matches:
        # If no specific table is provided, suggest for all tables
        # If table is provided, only suggest for that table
        if table is None or table_name == table:
            index_name = f"idx_{table_name}_{column}_join"
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({column})"
            suggestions.append(IndexSuggestion(
                table=table_name,
                columns=[column],
                where=f"JOIN on {column}",
                sql=sql
            ))
    
    return suggestions
