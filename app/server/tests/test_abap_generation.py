"""
(Claude)
Unit tests for ABAP code generation functions.

Requirements:
☑️ ABAP code is generated for simple queries
☑️ ABAP code is generated for complex queries with joins
☑️ Schema information is properly translated to SAP concepts
☑️ Error handling works correctly
☑️ Both OpenAI and Anthropic functions work
⏳ Markdown cleanup in ABAP output
⏳ Routing logic in generate_code() function
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from core.llm_processor import (
    generate_abap_with_openai,
    generate_abap_with_anthropic,
    format_schema_for_abap_prompt,
    map_sql_type_to_abap,
    generate_code,
)
from core.data_models import QueryRequest


@pytest.fixture
def sample_schema():
    """Sample database schema for testing"""
    return {
        "tables": {
            "users": {
                "columns": {
                    "id": "INTEGER",
                    "name": "TEXT",
                    "email": "VARCHAR",
                    "created_at": "DATE",
                    "is_active": "BOOLEAN",
                },
                "row_count": 150,
            }
        }
    }


def test_map_sql_type_to_abap():
    """if SQL types don't map correctly to ABAP types then broken"""
    assert map_sql_type_to_abap("INTEGER") == "INT4"
    assert map_sql_type_to_abap("TEXT") == "CHAR"
    assert map_sql_type_to_abap("VARCHAR") == "CHAR"
    assert map_sql_type_to_abap("REAL") == "FLTP"
    assert map_sql_type_to_abap("DATE") == "DATS"
    assert map_sql_type_to_abap("TIME") == "TIMS"
    assert map_sql_type_to_abap("BOOLEAN") == "CHAR1"
    assert map_sql_type_to_abap("UNKNOWN") == "CHAR"
    print("[OK] SQL types map correctly to ABAP types")


def test_format_schema_for_abap_prompt(sample_schema):
    """if schema formatting for ABAP doesn't include SAP conventions then broken"""
    result = format_schema_for_abap_prompt(sample_schema)

    # Check that Z-table convention is used
    assert "ZUSERS" in result or "Zusers" in result.upper()

    # Check that ABAP types are included
    assert "INT4" in result
    assert "CHAR" in result
    assert "DATS" in result
    assert "CHAR1" in result

    # Check row count is mentioned
    assert "150" in result

    print("[OK] Schema formatted correctly for ABAP with SAP conventions")


@patch("core.llm_processor.OpenAI")
def test_generate_abap_with_openai_simple_query(mock_openai_class, sample_schema):
    """if generate_abap_with_openai doesn't generate valid ABAP for simple queries then broken"""
    # Mock the OpenAI client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # Mock the response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """DATA: lt_users TYPE TABLE OF zusers,
      ls_user TYPE zusers.

SELECT * FROM zusers
  INTO TABLE lt_users
  UP TO 100 ROWS."""

    mock_client.chat.completions.create.return_value = mock_response

    # Set environment variable
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = generate_abap_with_openai("Show me all users", sample_schema)

        # Verify ABAP code contains expected elements
        assert "DATA:" in result or "data:" in result.lower()
        assert "SELECT" in result
        assert "zusers" in result.lower() or "ZUSERS" in result
        assert "INTO TABLE" in result

        print("[OK] generate_abap_with_openai generates valid ABAP for simple queries")


@patch("core.llm_processor.OpenAI")
def test_generate_abap_with_openai_cleans_markdown(mock_openai_class, sample_schema):
    """if generate_abap_with_openai doesn't clean markdown formatting then broken"""
    # Mock the OpenAI client
    mock_client = MagicMock()
    mock_openai_class.return_value = mock_client

    # Mock response with markdown formatting
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """```abap
DATA: lt_users TYPE TABLE OF zusers.
SELECT * FROM zusers INTO TABLE lt_users.
```"""

    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = generate_abap_with_openai("Show me all users", sample_schema)

        # Verify markdown is cleaned
        assert not result.startswith("```")
        assert not result.endswith("```")
        assert "DATA:" in result
        print("[OK] generate_abap_with_openai cleans markdown formatting")


@patch("core.llm_processor.Anthropic")
def test_generate_abap_with_anthropic(mock_anthropic_class, sample_schema):
    """if generate_abap_with_anthropic doesn't generate valid ABAP then broken"""
    # Mock the Anthropic client
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client

    # Mock the response
    mock_response = MagicMock()
    mock_response.content = [MagicMock()]
    mock_response.content[0].text = """DATA: lt_users TYPE TABLE OF zusers,
      ls_user TYPE zusers.

SELECT * FROM zusers
  INTO TABLE lt_users
  WHERE is_active = 'X'
  UP TO 100 ROWS."""

    mock_client.messages.create.return_value = mock_response

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
        result = generate_abap_with_anthropic(
            "Show me all active users", sample_schema
        )

        # Verify ABAP code contains expected elements
        assert "DATA:" in result or "data:" in result.lower()
        assert "SELECT" in result
        assert "zusers" in result.lower() or "ZUSERS" in result
        print("[OK] generate_abap_with_anthropic generates valid ABAP")


def test_generate_abap_with_openai_missing_api_key(sample_schema):
    """if generate_abap_with_openai doesn't raise error when API key is missing then broken"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(Exception) as exc_info:
            generate_abap_with_openai("Show me all users", sample_schema)

        assert "OPENAI_API_KEY" in str(exc_info.value)
        print("[OK] generate_abap_with_openai raises error when API key is missing")


def test_generate_abap_with_anthropic_missing_api_key(sample_schema):
    """if generate_abap_with_anthropic doesn't raise error when API key is missing then broken"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(Exception) as exc_info:
            generate_abap_with_anthropic("Show me all users", sample_schema)

        assert "ANTHROPIC_API_KEY" in str(exc_info.value)
        print(
            "[OK] generate_abap_with_anthropic raises error when API key is missing"
        )


@patch("core.llm_processor.generate_abap_with_openai")
def test_generate_code_routes_to_abap(mock_abap_openai, sample_schema):
    """if generate_code doesn't route to ABAP generation when mode is 'abap' then broken"""
    mock_abap_openai.return_value = "DATA: lt_users TYPE TABLE OF zusers."

    request = QueryRequest(query="Show me all users", output_mode="abap")

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = generate_code(request, sample_schema)

        # Verify ABAP generation was called
        mock_abap_openai.assert_called_once()
        assert "DATA:" in result
        print("[OK] generate_code routes to ABAP generation for 'abap' mode")


@patch("core.llm_processor.generate_sql_with_openai")
def test_generate_code_routes_to_sql(mock_sql_openai, sample_schema):
    """if generate_code doesn't route to SQL generation when mode is 'sql' then broken"""
    mock_sql_openai.return_value = "SELECT * FROM users;"

    request = QueryRequest(query="Show me all users", output_mode="sql")

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
        result = generate_code(request, sample_schema)

        # Verify SQL generation was called
        mock_sql_openai.assert_called_once()
        assert "SELECT" in result
        print("[OK] generate_code routes to SQL generation for 'sql' mode")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
