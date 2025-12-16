"""
(Claude)
Unit tests for data models with output_mode field validation.

Requirements:
- QueryRequest accepts "sql" output mode
- QueryRequest accepts "abap" output mode
- QueryRequest defaults to "sql" when output mode is not specified
- QueryRequest rejects invalid output modes
- QueryResponse handles both SQL and ABAP code
"""

import pytest
from pydantic import ValidationError
from core.data_models import QueryRequest, QueryResponse


def test_query_request_accepts_sql_mode():
    """if QueryRequest doesn't accept 'sql' output mode then broken"""
    request = QueryRequest(query="test query", output_mode="sql")
    assert request.output_mode == "sql"
    print("[OK] QueryRequest accepts 'sql' output mode")


def test_query_request_accepts_abap_mode():
    """if QueryRequest doesn't accept 'abap' output mode then broken"""
    request = QueryRequest(query="test query", output_mode="abap")
    assert request.output_mode == "abap"
    print("[OK] QueryRequest accepts 'abap' output mode")


def test_query_request_defaults_to_sql():
    """if QueryRequest doesn't default to 'sql' when output_mode not specified then broken"""
    request = QueryRequest(query="test query")
    assert request.output_mode == "sql"
    print("[OK] QueryRequest defaults to 'sql' output mode")


def test_query_request_rejects_invalid_mode():
    """if QueryRequest doesn't reject invalid output modes then broken"""
    with pytest.raises(ValidationError) as exc_info:
        QueryRequest(query="test query", output_mode="invalid")

    assert "output_mode" in str(exc_info.value)
    print("[OK] QueryRequest rejects invalid output mode")


def test_query_response_handles_sql():
    """if QueryResponse doesn't handle SQL code properly then broken"""
    response = QueryResponse(
        sql="SELECT * FROM users",
        code="SELECT * FROM users",
        output_mode="sql",
        results=[{"id": 1, "name": "Alice"}],
        columns=["id", "name"],
        row_count=1,
        execution_time_ms=10.5
    )
    assert response.sql == "SELECT * FROM users"
    assert response.code == "SELECT * FROM users"
    assert response.output_mode == "sql"
    print("[OK] QueryResponse handles SQL code")


def test_query_response_handles_abap():
    """if QueryResponse doesn't handle ABAP code properly then broken"""
    abap_code = "SELECT * FROM zusers INTO TABLE lt_users."
    response = QueryResponse(
        sql=abap_code,  # Backward compatibility field
        code=abap_code,
        output_mode="abap",
        results=[],
        columns=[],
        row_count=0,
        execution_time_ms=15.2
    )
    assert response.code == abap_code
    assert response.output_mode == "abap"
    print("[OK] QueryResponse handles ABAP code")


def test_query_response_backward_compatibility():
    """if QueryResponse breaks backward compatibility with sql field then broken"""
    response = QueryResponse(
        sql="SELECT * FROM users",
        results=[],
        columns=[],
        row_count=0,
        execution_time_ms=5.0
    )
    assert response.sql == "SELECT * FROM users"
    assert response.code is None  # Optional field
    assert response.output_mode is None  # Optional field
    print("[OK] QueryResponse maintains backward compatibility")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
